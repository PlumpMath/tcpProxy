#coding=utf-8
from baseLib import tcpConnectionPool
from baseLib import listenService
from baseLib import asyncoreEpoll
import os,signal
"""
worker处理进程：
1.注册信号，接收monitor发来的stop/reload/status信号,做相应后续处理
2.初始化远程连接对象
3.socket本地侦听,接收到数据后交由self.connObj的do方法来处理，处理完成后的数据回写本地socket
4.loop启动epoll
"""
class workerProcess(listenService.listenService):
    def __init__(self, _confDict=None, _logObj=None ):
        self.connConf = _confDict #{'pidfile':'','socketfile':'','dbhost':'','dbport':6379,'dbindex':0,'maxconnectcount':2}
        #建立redis连接池
        self.connObj = tcpConnectionPool.tcpConnectionPool(max_connections=self.connConf['maxconnectcount'],host=self.connConf['dbhost'],port=int(self.connConf['dbport']))
        self.logObj = _logObj
        self.transactionObj = None
        self.reloadStatus = False
        self.stopStatus = False

    def reload(self, _signum, _frame ):
        self.logObj.info("revice reload signal(%d) and reload programe!" % _signum)
        self.reloadStatus = True
        self.exit()

    def stop(self, _signum, _frame):
        self.logObj.info("revice stop signal(%d) and stop programe!" % _signum)
        self.stopStatus = True
        self.exit()

    def status(self, _signum, _frame ):
        self.logObj.info("revice status signal(%d) and status programe!" % _signum)
        pass

    def pre_start(self):
        """ create socket if needed and bind SIGKILL, SIGINT & SIGTERM
            signals
        """
        # handle signals
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGUSR1, self.reload)
        signal.signal(signal.SIGUSR2, self.status)

    def exit(self):
        if ( self.stopStatus or self.reloadStatus ):
            self.logObj.info('stop by signal and exit!')
            if ( isinstance( self.connObj,tcpConnectionPool.tcpConnectionPool ) ):
                self.connObj.disconnect()
            self.handle_close()
            os.sys.exit(1)

    def run(self):
        #注册信号事件
        self.pre_start()
        listenService.listenService.__init__(self, self.connConf['socketfile'], int( self.connConf['backlog'] ),_logObj= self.logObj, _processObj=self.connObj )
        #开启epoll
        asyncoreEpoll.loop()
#def __init__( self, _socketFile=None, _reciveSize=1024, _logObj=None, _processObj=None ):