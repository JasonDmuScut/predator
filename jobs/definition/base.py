import logging

import tools.log
import precedure.base
import storage.cv
import storage.gitinterface
import downloader.webdriver


class Base(object):

    CVDB_PATH = 'default_webdrivercv'
    FF_PROFILE_PATH = '/home/followcat/.mozilla/firefox/mtj6ft0d.default'
    PRECEDURE_CLASS = precedure.base.Base

    def __init__(self):
        self.wb_downloader = self.get_wb_downloader(self.FF_PROFILE_PATH)
        self.precedure = self.PRECEDURE_CLASS(wbdownloader=self.wb_downloader)
        self.cvrepo = storage.gitinterface.GitInterface(self.CVDB_PATH)
        self.cvstorage = storage.cv.CurriculumVitae(self.cvrepo)

    def downloadjob(self, cv_info):
        job_logger = logging.getLogger('schedJob')
        cv_id = cv_info['id']
        cv_content =  self.precedure.cv(cv_info['href'])
        result = self.cvstorage.add(cv_id, cv_content.encode('utf-8'), 'kabess')
        print('Download: '+cv_id)
        job_logger.info('Download: '+cv_id)
        result = True

    def get_wb_downloader(self, profile_path):
        return downloader.webdriver.Webdriver(profile_path)

    def jobgenerator(self):
        pass
