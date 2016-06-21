# -*- coding: utf-8 -*-
import functools

import jobs.base
import utils.builtin
import precedure.jingying


class Jingying(jobs.base.Base):

    CVDB_PATH = 'jingying_webdrivercv'
    FF_PROFILE_PATH = '/home/jeff/.mozilla/firefox/ozyc3tvj.jeff'
    PRECEDURE_CLASS = precedure.jingying.Jingying

    industry_yamls = ['47.yaml', #医疗设备/器械
                      '01.yaml', #计算机软件
                      '37.yaml', #计算机硬件
                      '38.yaml', #计算机服务(系统、数据服务、维修)
                      '31.yaml', #通信/电信/网络设备
                      '35.yaml', #仪器仪表/工业自动化
                      '14.yaml', #机械/设备/重工
                      '52.yaml', #检测，认证
                      '07.yaml', #专业服务(咨询、人力资源、财会)
                      '24.yaml', #学术/科研
                      '21.yaml', #交通/运输/物流
                      '55.yaml', #航天/航空
                      '36.yaml', #电气/电力/水利
                      '61.yaml'  #新能源
                    ]

    def jobgenerator(self):
        for _file in self.industry_yamls:
            yamldata = utils.builtin.load_yaml('jingying/JOBTITLES', _file)
            sorted_id = sorted(yamldata,
                               key = lambda cvid: yamldata[cvid]['peo'][-1],
                               reverse=True)
            for cv_id in sorted_id:
                if not self.cvstorage.exists(cv_id):
                    cv_info = yamldata[cv_id]
                    job_process = functools.partial(self.downloadjob, cv_info)
                    yield job_process

instance = Jingying()

PROCESS_GEN = instance.jobgenerator()
PLAN = [dict(second='*/3', hour='8-17'),
        dict(second='*/5', hour='18-23'),
        dict(second='*/5', hour='0-7')]