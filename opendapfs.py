#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import logging

from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
from siphon.catalog import TDSCatalog
from functools import lru_cache

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn, fuse_get_context

if not hasattr(__builtins__, 'bytes'):
    bytes = str

@lru_cache(maxsize=1024)
def _getcatalog(catalog, path):
    start, therest = path[:1].split('/', 1)
    if start == '':
        return catalog, therest
#    elif start in catalog.catalog_refs:
#        newparent = catalog.catalog_refs[start].follow()
#        return _getcatalog(newparent, therest)
    else:
        return None


class OpendapFS(LoggingMixIn, Operations):
    'Browse an Opendap server as a FUSE filesystem'
    def __init__(self, configxml):
        self.catalog = TDSCatalog(configxml)
        
    def getattr(self, path, fh=None):
        cat, name = _getcatalog(self.catalog, path)
#        import ipdb; ipdb.set_trace()

        if cat is None:
            raise FuseOSError(ENOENT)
        elif name == '':
            st = dict(st_mode=(S_IFDIR | 0o755), st_nlink=2)
        elif name in cat.catalog_refs:
            st = dict(st_mode=(S_IFDIR | 0o755), st_nlink=2)
        elif name in cat.datasets:
            st = dict(st_mode=(S_IFREG | 0o444), st_size=size)
        else:
            raise FuseOSError(ENOENT)
        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time()
        return st

    read = None
#    def read(self, path, size, offset, fh):

    def readdir(self, path, fh):
        import ipdb; ipdb.set_trace()
        cat, name = _getcatalog(self.catalog, path)

        return list(cat.catalog_refs.keys()) + list(cat.datasets.keys())

    # Disable unused operations:
    access = None
    flush = None
    getxattr = None
    listxattr = None
    open = None
    opendir = None
    release = None
    releasedir = None
    statfs = None


if __name__ == '__main__':
    if len(argv) != 3:
        print('usage: %s <opendap_config.xml url> <mountpoint>' % argv[0])
        exit(1)

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(OpendapFS(argv[1]), argv[2], foreground=True)
