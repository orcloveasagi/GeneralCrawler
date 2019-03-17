# -*- mode: python -*-
import os
import json
from core import utils


class DataCache(object):
    data_cache = {}

    @classmethod
    def set(cls, name, data):
        cls.data_cache[name] = data

    @classmethod
    def get(cls, name):
        return cls.data_cache[name]


class RuntimeData(object):
    runtime_path = []

    @classmethod
    def runtime_data_path(cls):
        return os.path.join('.runtime', *cls.runtime_path)

    @classmethod
    def set(cls, name, data):
        if os.path.isdir(cls.runtime_data_path()) is False:
            os.makedirs(cls.runtime_data_path())

        runtime_data = {}
        if os.path.isfile(os.path.join(cls.runtime_data_path(), '.runtime.json')):
            with open(os.path.join(cls.runtime_data_path(), '.runtime.json'), 'r') as file:
                try:
                    runtime_data = json.loads(file.read())
                except json.decoder.JSONDecodeError:
                    pass
        runtime_data[name] = data

        with open(os.path.join(cls.runtime_data_path(), '.runtime.json'), 'w') as file:
            file.write(json.dumps(runtime_data))

    @classmethod
    def get(cls, name):
        if os.path.isdir(cls.runtime_data_path()) is False:
            os.makedirs(cls.runtime_data_path())
        runtime_data = {}
        with open(os.path.join(cls.runtime_data_path(), '.runtime.json'), 'r') as file:
            runtime_data = json.loads(file.read())
        return runtime_data[name]

    @classmethod
    def has(cls, name):
        if os.path.isdir(cls.runtime_data_path()) is False:
            os.makedirs(cls.runtime_data_path())
        runtime_data = {}
        if os.path.isfile(os.path.join(cls.runtime_data_path(), '.runtime.json')) is False:
            with open(os.path.join(cls.runtime_data_path(), '.runtime.json'), 'w') as file:
                file.write(json.dumps({}))
            return False
        with open(os.path.join(cls.runtime_data_path(), '.runtime.json'), 'r') as file:
            runtime_data = json.loads(file.read())
        return name in runtime_data


class System(object):
    __config = {}

    @classmethod
    def load_config(cls, path):
        with open(path, 'rb') as file:
            cls.__config.update(json.loads(file.read()))

    @classmethod
    def config(cls):
        return cls.__config

    @classmethod
    def runtime(cls):
        return os.path.join(cls.config()['runtime'])

    @classmethod
    def app(cls):
        return utils.module(cls.config()['app'])
