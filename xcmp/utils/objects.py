#!/usr/bin/python3
# coding:utf-8

import imghdr
from queue import Empty
from queue import Queue
from threading import Thread
from threading import current_thread
from typing import Dict
from typing import Sequence
from typing import Set

from xarg import commands
from xarg import scanner


class hashcmp:

    class item:

        def __init__(self, name: str, hash: str):
            assert isinstance(name, str)
            assert isinstance(hash, str)
            self.__name = name
            self.__hash = hash

        @property
        def name(self) -> str:
            return self.__name

        @property
        def hash(self) -> str:
            return self.__hash

    def __init__(self):
        self.__objdict: Dict[str, hashcmp.item] = dict()
        self.__objects: Set[hashcmp.item] = set()
        self.__same: Dict[str, Set[str]] = {}
        self.__diff: Dict[str, str] = {}

    def __iter__(self):
        return iter(self.__objects)

    def __getitem__(self, key: str):
        return self.__objdict[key]

    @property
    def diff(self) -> Dict[str, str]:
        return self.__diff

    @property
    def same(self) -> Dict[str, Set[str]]:
        return self.__same

    def add(self, item: item):
        assert isinstance(item, hashcmp.item)
        if item.name in self.__objdict:
            return

        self.__objects.add(item)
        self.__objdict[item.name] = item

        key = item.hash
        val = item.name
        if key in self.__diff:
            self.__same[key] = {self.__diff[key], val}
            del self.__diff[key]
        elif key in self.__same:
            self.__same[key].add(val)
        else:
            self.__diff[key] = val


class filecmp(hashcmp):
    '''
    scan files
    '''

    class item(hashcmp.item):

        def __init__(self, obj: scanner.object):
            assert isinstance(obj, scanner.object)
            hashcmp.item.__init__(self, name=obj.realpath, hash=obj.md5)
            self._obj = obj

    def __init__(self):
        hashcmp.__init__(self)

    @classmethod
    def scan(cls, paths: Sequence[str], exclude: Sequence[str] = []):

        class task_stat:

            def __init__(self):
                self.exit = False
                self.list = filecmp()
                self.q_item: Queue[filecmp.item] = Queue()

        scan_stat = task_stat()

        def task_scan():
            cmds = commands()
            name = current_thread().name
            cmds.logger.debug(f"task thread[{name}] start")
            while not scan_stat.exit or not scan_stat.q_item.empty():
                try:
                    item = scan_stat.q_item.get(timeout=0.01)
                except Empty:
                    continue

                scan_stat.list.add(item=item)
                scan_stat.q_item.task_done()
            cmds.logger.debug(f"task thread[{name}] exit")

        def handle(obj: scanner.object) -> bool:
            if not obj.isfile:
                return False

            item = filecmp.item(obj=obj)
            scan_stat.q_item.put(item)
            return True

        Thread(target=task_scan, name="filecmp-scan").start()
        scanner.load(paths=paths, exclude=exclude, handler=handle)

        # wait and exit
        scan_stat.q_item.join()
        scan_stat.exit = True
        return scan_stat.list


class imagecmp(hashcmp):
    '''
    scan images
    '''

    class item(hashcmp.item):

        def __init__(self, obj: scanner.object):
            assert isinstance(obj, scanner.object)
            hashcmp.item.__init__(self, name=obj.realpath, hash=obj.md5)
            self._obj = obj

    def __init__(self):
        hashcmp.__init__(self)

    @classmethod
    def scan(cls, paths: Sequence[str], exclude: Sequence[str] = []):

        class task_stat:

            def __init__(self):
                self.exit = False
                self.list = imagecmp()
                self.q_item: Queue[imagecmp.item] = Queue()

        scan_stat = task_stat()

        def task_scan():
            cmds = commands()
            name = current_thread().name
            cmds.logger.debug(f"task thread[{name}] start")
            while not scan_stat.exit or not scan_stat.q_item.empty():
                try:
                    item = scan_stat.q_item.get(timeout=0.01)
                except Empty:
                    continue

                scan_stat.list.add(item=item)
                scan_stat.q_item.task_done()
            cmds.logger.debug(f"task thread[{name}] exit")

        def handle(obj: scanner.object) -> bool:
            if not obj.isfile:
                return False

            imgres = imghdr.what(obj.path)
            if not isinstance(imgres, str):
                return False

            item = imagecmp.item(obj=obj)
            scan_stat.q_item.put(item)
            return True

        Thread(target=task_scan, name="imagecmp-scan").start()
        scanner.load(paths=paths, exclude=exclude, handler=handle)

        # wait and exit
        scan_stat.q_item.join()
        scan_stat.exit = True
        return scan_stat.list
