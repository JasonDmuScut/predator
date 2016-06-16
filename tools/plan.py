import os
import time
import random
import logging

import tools.log
import tools.mail

import apscheduler.events
import apscheduler.schedulers.blocking

scheduler = apscheduler.schedulers.blocking.BlockingScheduler()


def randomjob(cvinfo_gen, precedure, cvstorage):
    result = False
    job_logger = logging.getLogger('schedJob')
    print('The time is: %s' % time.ctime())
    cv_info = cvinfo_gen.next()
    cv_id = cv_info['id']
    cv_content =  precedure.cv(cv_info['href'])
    result = cvstorage.add(cv_id, cv_content.encode('utf-8'), 'followcat')
    print('Download: '+cv_id)
    job_logger.info('Download: '+cv_id)
    result = True
    return result


def err_listener(ev):
    err_logger = logging.getLogger('schedErrJob')
    if ev.exception:
        err_logger.error('%s error.', str(ev.job_id))
    else:
        err_logger.info('%s miss', str(ev.job_id))
    tools.mail.send_mail(['fengliji@willendare.com'], ev.job_id, "Wrong and stop!")
    global scheduler
    scheduler.shutdown()


def jobgenerator(yamldata, cvstorage):
    sorted_id = sorted(yamldata,
                       key = lambda cvid:yamldata[cvid]['peo'][-1],
                       reverse=True)
    for cv_id in sorted_id:
        if not cvstorage.exists(cv_id):
            yield yamldata[cv_id]


def jobadder(scheduler, job, plan, arguments=None):
    if arguments is None:
        arguments = []
    for each in plan:
        scheduler.add_job(job, 'cron', args=arguments, **each)


if __name__ == '__main__':
    import jobs.liepin
    CVDB_PATH = jobs.liepin.CVDB_PATH
    FF_PROFILE_PATH = jobs.liepin.FF_PROFILE_PATH
    PRECEDURE_CLASS = jobs.liepin.PRECEDURE_CLASS
    YAMLDATA = jobs.liepin.YAMLDATA
    PLAN = jobs.liepin.PLAN

    import storage.repocv
    import storage.gitinterface
    import downloader.webdriver
    yamldata = YAMLDATA
    wb_downloader = downloader.webdriver.Webdriver(FF_PROFILE_PATH)
    liepin_pre = PRECEDURE_CLASS(wbdownloader=wb_downloader)
    cvrepo = storage.gitinterface.GitInterface(CVDB_PATH)
    cvstorage = storage.repocv.CurriculumVitae(cvrepo)

    cvinfo_gen = jobgenerator(yamldata, cvstorage)
    jobadder(scheduler, randomjob, PLAN, arguments=[cvinfo_gen, liepin_pre, cvstorage])
    scheduler.add_listener(err_listener,
        apscheduler.events.EVENT_JOB_ERROR | apscheduler.events.EVENT_JOB_MISSED) 
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
