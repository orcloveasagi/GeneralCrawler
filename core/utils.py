# -*- mode: python -*-
import sys
import os
import importlib
import urllib.parse


def module(module_path: str):
    sys.path.append(os.path.join("."))
    return importlib.import_module(module_path)


def import_class(class_path: str):
    path_meta = class_path.split(".")
    return getattr(module('.'.join(path_meta[0:-1])), path_meta[-1])


def get_params(url):
    return dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))


def path_format(path):
    r_dir_filter = [
        ('/', '_'),
        ('\\', '_'),
        (':', '：'),
        ('*', '_'),
        ('?', u'？'),
        ('"', '_'),
        ('<', '['),
        ('>', ']'),
        ('|', '_'),
    ]
    for filter_ele in r_dir_filter:
        path = path.replace(filter_ele[0], filter_ele[1])
    return path
