# -*- coding: utf-8 -*-
import time
import logging
import functools

import utils.builtin
import precedure.liepin
import jobs.definition.cloudshare

from extractor.utils_parsing import *


class Liepin(jobs.definition.cloudshare.Cloudshare):

    CVDB_PATH = 'output/liepin'
    FF_PROFILE_PATH = '/home/followcat/.mozilla/firefox/yffp11op.followcat'
    PRECEDURE_CLASS = precedure.liepin.Liepin

    def cloudshare_yaml_template(self):
        template = super(Liepin, self).cloudshare_yaml_template()
        template['origin'] = u'猎聘爬取'
        return template

    def jobgenerator(self, classify_id):
        yamlname = classify_id + '.yaml'
        yamldata = utils.builtin.load_yaml('liepin/JOBTITLES', yamlname)
        sorted_id = sorted(yamldata,
                           key = lambda cvid: yamldata[cvid]['peo'][-1],
                           reverse=True)
        for cv_id in sorted_id:
            if not self.cvstorage.existscv(cv_id):
                cv_info = yamldata[cv_id]
                job_process = functools.partial(self.downloadjob, cv_info, classify_id)
                yield job_process

    def downloadjob(self, cv_info, classify_id):
        job_logger = logging.getLogger('schedJob')
        cv_id = cv_info['id']
        print('Download: '+cv_id)
        try:
            cv_content =  self.precedure.cv(cv_info['href'])
            cvresult = True
        except precedure.liepin.NocontentCVException:
            print('Failed! Download: '+cv_id)
            cvresult = False
        if cvresult is True:
            yamldata = self.extract_details(cv_info)
            cvresult = self.cvstorage.addcv(cv_id, cv_content.encode('utf-8'), yamldata)
            job_logger.info('Download: '+cv_id)
        else:
            job_logger.info('Failed! Download: '+cv_id)
        return cvresult

    def extract_details(self, uploaded_details):
        details = self.cloudshare_yaml_template()

        details['date'] = time.time()
        details['name'] = uploaded_details['name']
        details['id'] = uploaded_details['id']
        details['originid'] = uploaded_details['id']
        details['age']= re.compile('[0-9]*').match(uploaded_details['peo'][2]).group()
        details['filename'] = uploaded_details['href']
        add_cr = lambda x:'\n'+x.group()
        for education in re.compile(STUDIES, re.M).finditer(re.compile(PERIOD).sub(add_cr, uploaded_details['info'][0])):
            details['school'] = education.group('school')
            details['major'] = education.group('major')
            details['education'] = education.group('education').replace('\n', '')\
                                    .replace('\t', '').replace('\r', '').replace(' ', '')
        for expe in uploaded_details['info']:
            for w in re.compile(WORKXP, re.M).finditer(re.compile(PERIOD).sub(add_cr, expe)):
                details['experience'].append((fix_date(w.group('from')), fix_date(w.group('to')),
                    fix_name(w.group('company'))+'|'+fix_name(w.group('position'))+'('+fix_duration(w.group('duration'))+')'))
        if details['experience'] and re.match(TODAY, details['experience'][0][1]) is not None:
            details['company'] = uploaded_details['peo'][7]
            details['position'] = uploaded_details['peo'][6]
            if u'…' in details['company']:
                no_braket = lambda x:x.replace('(','').replace(')','')
                escape_star = lambda x:x.replace('*','\*')
                RE = re.compile(escape_star(no_braket(details['company'])[:-1]))
                xp = details['experience'][0]
                if RE.match(no_braket(xp[2])):
                    details['company'] = xp[2].split('|')[0]
        return details
