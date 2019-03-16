# -*- mode: python -*-
import json
import os
from core.system import System
import inspect


class AppRuntime(object):

    def __init__(self, space=None):
        self.space = space

    def file_path(self):
        return u'%s.json' % os.path.join(System.runtime(), self.space)

    def set(self, name, value):
        if self.has_runtime() is True:
            with open(self.file_path(), 'rb') as file:
                data = json.loads(file.read())
        else:
            data = {}
        data[name] = value

        os.makedirs(os.path.dirname(self.file_path()), exist_ok=True)

        with open(self.file_path(), 'w') as file:
            file.write(json.dumps(data))

    def get(self, name):
        if self.has_runtime() is False:
            return None

        with open(self.file_path(), 'rb') as file:
            data = json.loads(file.read())
        return data[name] if name in data else None

    def has_runtime(self):
        return os.path.isfile(self.file_path())


class AppInstance(object):

    def __init__(self, name=None):
        self.__config = {
            'loop': True
        }
        self.name = name
        self.__components = {}

    def config(self, config: dict = None):
        if config is None:
            return self.__config
        else:
            self.__config.update(config)
            return self

    def main_class(self):
        return self.__config['main_class']

    def loop(self, loop=None):
        if loop is None:
            return self.__config['loop']
        else:
            self.__config['loop'] = loop
            return self

    def runtime(self):
        '''
        :rtype: AppRuntime
        :return:
        '''
        if 'runtime' not in self.__components:
            self.__components['runtime'] = AppRuntime(self.name)
        return self.__components['runtime']


class App(object):
    instance_pool = {}

    @classmethod
    def instance(cls, name=None):
        '''

        :rtype: AppInstance
        :param name:
        :return:
        '''
        if name is None:
            name = inspect.getmodule(inspect.stack()[1][0]).__package__
        if name not in cls.instance_pool:
            cls.instance_pool[name] = AppInstance(name)
        return cls.instance_pool[name]
