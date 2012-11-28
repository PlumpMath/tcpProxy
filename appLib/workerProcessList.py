#coding=utf-8
from appLib import workerProcess
"""
1.解析配置文件
2.根据传入的dict，做适当的worker进程构建时的配置处理
3.创建所有工作进程并返回所有的工作进程列表
"""

"""
解析redis的配置
[1.69]
#host,port,dbindex,maxConnectCount:socketFile
master=127.0.0.1:6379:0:2
masterSocketFile="/tmp/1.69-6379.sock"
slave=127.0.0.1:6379:0:2,127.0.0.1:6380:0:2
slaveSocketFileTmpl="/tmp/__IP__-__PORT__.sock"
_conf为形如1.69的section的dict
"""

def getSubProcessConfBySection(_conf=dict() ):
    confDict = dict()
    confDict['master'] = dict()
    socketFileTmpl = _conf['socketfiletmpl']
    confDict['master']['dbhost'],confDict['master']['dbport'],confDict['master']['dbindex'],confDict['master']['maxconnectcount'] = _conf['master'].split(':')
    confDict['master']['socketfile'] = socketFileTmpl.replace( "__IP__",confDict['master']['dbhost'] )
    confDict['master']['socketfile'] = confDict['master']['socketfile'].replace( "__PORT__",confDict['master']['dbport'] )
    confDict['master']['pidfile'] = confDict['master']['socketfile'].replace( "sock", "pid")
    confDict['master']['backlog'] = _conf['masterbacklog']
    confDict['slave'] = list()
    slaveNodeConf = dict()
    slaveListConf = _conf['slave'].split(",")
    listLen = len( slaveListConf )
    for i in range( listLen ):
        slaveNodeConf['dbhost'],slaveNodeConf['dbport'],slaveNodeConf['dbindex'],slaveNodeConf['maxconnectcount'] = slaveListConf[i].split(':')
        slaveNodeConf['socketfile'] = socketFileTmpl.replace( "__IP__",slaveNodeConf['dbhost'] )
        slaveNodeConf['socketfile'] = slaveNodeConf['socketfile'].replace( "__PORT__",slaveNodeConf['dbport'] )
        slaveNodeConf['pidfile'] = slaveNodeConf['socketfile'].replace("sock","pid")
        slaveNodeConf['backlog'] = _conf['slavebacklog']
        confDict['slave'].append( slaveNodeConf )
        slaveNodeConf = dict()
    return confDict

#获取客户端所有的socketFile
def getClientSocketFileList( _confDict={} ):

    clientSocketFileList = list()
    #取得所有redis的section
    subProcessListConf = _confDict['default']['redislist'].split(",")
    listLen = len( subProcessListConf )
    #遍历每个section里的item并解析为redis的连接参数与侦听socket
    for i in range( listLen ):
        sectionMasterSlaveConfDict = getSubProcessConfBySection( _confDict[subProcessListConf[ i] ] )
        clientSocketFileList.append( sectionMasterSlaveConfDict['master']['socketfile'] )
        slaveConfList = sectionMasterSlaveConfDict['slave']
        slaveConfListLen = len( slaveConfList )
        #遍历辅库
        for j in range ( slaveConfListLen ):
            clientSocketFileList.append( slaveConfList[ j ]['socketfile'] )
    return clientSocketFileList

#遍历所有的redis实例
def getSubProcessObjList( _confDict=dict(), logObj = None):
    subProcessListObj = list()
    #取得所有redis的section
    subProcessListConf = _confDict['default']['redislist'].split(",")
    listLen = len( subProcessListConf )
    #遍历每个section里的item并解析为redis的连接参数与侦听socket
    for i in range( listLen ):
        sectionMasterSlaveConfDict = getSubProcessConfBySection( _confDict[subProcessListConf[ i] ] )
        subProcessListObj.append(workerProcess.workerProcess( sectionMasterSlaveConfDict['master'], logObj ) )
        slaveConfList = sectionMasterSlaveConfDict['slave']
        slaveConfListLen = len( slaveConfList )
        #遍历辅库
        for j in range ( slaveConfListLen ):
            subProcessListObj.append(workerProcess.workerProcess( slaveConfList[ j ], logObj ) )
    return subProcessListObj

@staticmethod
def reload( _confDict = None, _logObj =None ):
    return getSubProcessObjList( _confDict, _logObj )


