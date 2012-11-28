#coding=utf-8
import logging
"""
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
"""
logDict = {'debug':logging.DEBUG,
           'info':logging.INFO,
           'warning':logging.warn,
           'error':logging.ERROR
            }
def convertListToDict( _cf ):
    sectionsList = _cf.sections()
    retDict = {}
    for val1 in sectionsList:
        retDict[ val1 ] = dict( _cf.items( val1 ) )
    return retDict
