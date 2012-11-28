#coding=utf-8

from baseLib import commFunc
import logging
import ConfigParser
import os
import workerProcessList

"""
monitor初始化程序:
1.初始化全局配置文件
2.初始化全局日志文件
3.初始化worker进程列表与配置
"""
class monitorProcess(object):
    def __init__( self, _confFile="" ):

        self.confFile =_confFile
        self.confDict = dict()
        self.logObj=None
        self.workerProcessObjList = None
        self.reload()

    def reload(self):
        self.stopStatus = False
        self.reloadStatus = False
        cfObj = ConfigParser.ConfigParser()
        cfObj.read( self.confFile )
        confIniDict = commFunc.convertListToDict( cfObj )
        self.logObj = logging
        self.logObj.basicConfig(
            filename=confIniDict[ 'default' ][ 'log' ],
            filemode='a+',
            format='%(asctime)s %(levelname) 5s %(name)s | %(message)s %(filename)s %(module)s %(lineno)d',
            datefmt='%Y-%m-%dT%H:%M:%S%z',
            level=commFunc.logDict[ confIniDict['default']['loglevel'] ])
        #self.logObj.getLogger('monitor')

        self.pidFile = confIniDict['default']['pidfile']
        self.confDict = confIniDict
        self.logObj.info( 'monitorProcess init end!')
        self.workerProcessObjList = self.getWorkerProcessList()

    def run(self):
        while(True):
            if ( self.stopStatus or self.reloadStatus ):
                os.sys.exit(1)
            else:
                pass

    def getWorkerProcessList(self):
        return workerProcessList.getSubProcessObjList( self.confDict, self.logObj )

    def getConfDict(self):
        return self.confDict

    def getLogObj(self):
        return self.logObj
