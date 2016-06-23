import os
import time
import hashlib

import yaml
import utils._yaml


def md5(text):
    m = hashlib.md5()
    m.update(text)
    return unicode(m.hexdigest())

def loadfile(path):
    with open(path) as fp:
        stream = fp.read()
    return stream

def save_yaml(infodict, path, filename):
    with open(os.path.join(path, filename), 'w') as f:
        f.write(yaml.dump(infodict))


def load_yaml(path, filename):
    with open(os.path.join(path, filename), 'r') as yf:
        yaml_data = yf.read()
    yaml_info = yaml.load(yaml_data, Loader=utils._yaml.Loader)
    return yaml_info


def merge_yaml(idlist, path, output):
    yamldata = {}
    for each in idlist:
        filename = each + '.yaml'
        try:
            single_data = load_yaml(path, filename)
        except IOError:
            continue
        yamldata[each] = single_data
    dumpdata = yaml.dump(yamldata, Dumper=yaml.CSafeDumper, allow_unicode=True)
    with open(output, 'w') as f:
        f.write(dumpdata)

try:
    from subprocess import check_output
except ImportError:
    # Python < 2.7 fallback, stolen from the 2.7 stdlib
    def check_output(*popenargs, **kwargs):
        from subprocess import Popen, PIPE, CalledProcessError
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = Popen(stdout=PIPE, *popenargs, **kwargs)
        output, _ = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd, output=output)
        return output


def strftime(t):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
