import os
import time
import random
import logging
import argparse

import apscheduler.events
import apscheduler.schedulers.blocking

scheduler = apscheduler.schedulers.blocking.BlockingScheduler()


def schedulerjob(process_gen, sleep=True):
    result = False
    if sleep is True:
        nums_tensec = random.randint(0, 18)
        time.sleep(nums_tensec*10)
    print('The time is: %s' % time.ctime())
    job_process = process_gen.next()
    result = job_process()
    return result


def err_listener(ev):
    err_logger = logging.getLogger('schedErrJob')
    if ev.exception:
        err_logger.error('%s error.', str(ev.job_id))
    else:
        err_logger.info('%s miss', str(ev.job_id))
    global scheduler
    scheduler.shutdown()


def jobadder(scheduler, job, plan, arguments=None, kwarguments=None):
    if arguments is None:
        arguments = []
    if kwarguments is None:
        kwarguments = {}
    for each in plan:
        scheduler.add_job(job, 'cron', args=arguments, kwargs=kwarguments, **each)



parser = argparse.ArgumentParser(description='Plan tool.')
parser.add_argument('job', type=str, help='Process job generateor module.')

if __name__ == '__main__':
    import importlib

    args = parser.parse_args()
    jobmodule = importlib.import_module(args.job)

    PLAN = jobmodule.PLAN
    PROCESS_GEN = jobmodule.PROCESS_GEN

    jobadder(scheduler, schedulerjob, PLAN,
             arguments=[PROCESS_GEN],
             kwarguments=dict(sleep=False))
    scheduler.add_listener(err_listener,
        apscheduler.events.EVENT_JOB_ERROR | apscheduler.events.EVENT_JOB_MISSED)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
