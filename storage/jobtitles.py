import glob
import yaml
import utils._yaml
import os.path

import utils.builtin


class JobTitles(object):
    path = 'JOBTITLES'

    def __init__(self, interface):
        self.interface = interface
        self.interface_path = self.interface.path + "/" + self.path
        self.info = ""
        self.table = {}
        if not os.path.exists(self.interface_path):
            os.makedirs(self.interface_path)

    def get(self, classify_id):
        if classify_id in self.table:
            return self.table[classify_id]
        yamlname = classify_id + '.yaml'
        yamldata = utils.builtin.load_yaml(self.interface_path, yamlname)
        return yamldata

    def remove(self, classify_id, cv_id):
        yamldata = self.get(classify_id)
        removed = yamldata.pop(cv_id)
        self.modify_data(classify_id, yamldata)
        return removed

    def add_datas(self, classify_id, datas, update_datas, header, committer=None):
        if len(datas) == 0:
            return True
        if header is None:
            header = dict()
        filename = classify_id + '.yaml'
        table = self.get(classify_id)

        if 'datas' not in table:
            new_table = dict()
            new_table['datas'] = dict()
            new_table['datas'].update(table)
            table = new_table
        table.update(header)
        for data in datas:
            table['datas'][data['id']] = data

        if update_datas is not None:
            for data in update_datas:
                if data['id'] not in table['datas']:
                    table['datas'][data['id']] = data
                    continue
                current = table['datas'][data['id']]
                for key in data['tags'].keys():
                    if key not in current['tags']:
                        current['tags'][key] = set()
                    current['tags'][key] = current['tags'][key].union(data['tags'][key])

        dump_data = yaml.dump(table, Dumper=yaml.CSafeDumper, allow_unicode=True)
        self.interface.add_file(os.path.join(self.path, filename), dump_data,
                                message="Add to classify id :" + filename,
                                committer=committer)
        return True

    def add_data(self, classify_id, data, committer=None):
        filename = classify_id + '.yaml'
        dump_data = yaml.dump(data, Dumper=yaml.CSafeDumper, allow_unicode=True)
        self.interface.add_file(os.path.join(self.path, filename), dump_data,
                                message="Add to classify id :" + filename,
                                committer=committer)
        return True

    def modify_data(self, classify_id, data, committer=None, message=None):
        filename = classify_id + '.yaml'
        dump_data = yaml.dump(data, Dumper=yaml.CSafeDumper, allow_unicode=True)
        self.interface.modify_file(os.path.join(self.path, filename), dump_data,
                                   message=message, committer=committer)
        return True

    def exists(self, classify_id, data_id):
        if classify_id not in self.table:
            self._initclassify(classify_id)
            self.table[classify_id] = utils.builtin.load_yaml(self.interface_path, classify_id+'.yaml')
        exists = False
        if 'datas' in self.table[classify_id]:
            datas = self.table[classify_id]['datas']
        else:
            datas = self.table[classify_id]
        return data_id in datas

    def _initclassify(self, classify_id):
        filename = classify_id + '.yaml'
        file_path = os.path.join(self.interface_path, filename)
        if not os.path.exists(file_path):
            table = {}
            self.interface.add_file(os.path.join(self.path, filename),
                                    yaml.dump(table, Dumper=yaml.CSafeDumper, allow_unicode=True),
                                    "Add classify file: " + filename)

