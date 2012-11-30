#coding=utf-8
from asyncore import *

"""
扩展async使其支持epoll
"""
def epoll(timeout=0.0, map=None):
    # Use the poll() support added to the select module in Python 2.0
    if map is None:
        map = socket_map
    if timeout is not None:
        # timeout is in milliseconds
        timeout = int(timeout*1000)
    pollster = select.epoll()
    if map:
        for fd, obj in map.items():
            flags = 0
            if obj.readable():
                flags |= select.EPOLLIN | select.EPOLLPRI| select.EPOLLET
            if obj.writable():
                flags |= select.EPOLLOUT
            if flags:
                # Only check for exceptions if object was either readable
                # or writable.
                flags |= select.EPOLLERR | select.EPOLLHUP
                pollster.register(fd, flags)
        try:
            r = pollster.poll(timeout)
        except select.error, err:
            if err.args[0] != EINTR:
                raise
            r = []
        for fd, flags in r:
            obj = map.get(fd)
            if obj is None:
                continue
            readwrite(obj, flags)
def loop(timeout=30.0, use_poll=False, map=None, count=None):
    if map is None:
        map = socket_map
    if use_poll and hasattr(select, 'epoll'):
        poll_fun = epoll
    else:
        if use_poll and hasattr(select, 'poll'):
            poll_fun = poll2
        else:
            poll_fun = poll

    if count is None:
        while map:
            poll_fun(timeout, map)

    else:
        while map and count > 0:
            poll_fun(timeout, map)
            count = count - 1