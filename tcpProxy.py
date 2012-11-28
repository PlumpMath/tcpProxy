#coding=utf-8
import sys,os
from appLib import monitorProcess
from baseLib import monitorDaemon

def help( argv ):
    if len( sys.argv ) != 2:
        print "start error: python tcpProxy.py conf/conf.ini"
        sys.exit(1)
    if ( not os.path.isfile( sys.argv[1] ) ):
        print "start error:%s file is not exists!" % sys.argv[1]

help( sys.argv )



pwdDir = os.getcwd()
if ( sys.argv[1].find(pwdDir) == -1 ):
    sys.argv[1] = os.getcwd()+"/"+sys.argv[1]

#初始化monitor进程并创建所有worker对象供子进程处理
monitorProcessObj = monitorProcess.monitorProcess( sys.argv[ 1 ] )

"""
创建所有进程并运行，每个worker进程开启uds侦听，monitor进程进入死循环等秲信号
"""
monitorObj = monitorDaemon.monitorDaemon( monitorProcessObj )
monitorObj.startMonitor()







