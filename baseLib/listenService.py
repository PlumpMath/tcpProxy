#coding=utf-8
import  socket, os
from . import asyncoreEpoll


"""
服务端socket侦听：
1.侦听本地socket
2.有连接请求进来,handle_accept获取新的连接
3.根据新的连接创建clientAgent对象，后续的处理交由epoll接管
"""
#接收户端最大长度
MAX_RECV = 1024

#负责接收client的连线
class listenService( asyncoreEpoll.dispatcher ):

    def __init__( self, _socketFile=None, _backlog=None, _logObj=None, _processObj=None ):
        self.socketFile = _socketFile
        self.backlog = _backlog
        self.logObj = _logObj
        asyncoreEpoll.dispatcher.__init__( self )
        self.create_socket( socket.AF_UNIX, socket.SOCK_STREAM )
        #self.create_socket( socket.AF_UNIX, socket.SOCK_DGRAM )
        self.set_reuse_addr()
        self.processObj = _processObj

        self.bind( self.socketFile )
        self.listen( self.backlog )

    def handle_accept(self):
        #接收client的连线
        self.clientSocket, address = self.accept()
        #self.logObj.info( "new client from:%s" % self.clientSocket )
        #初始化客户端连接请求，后续处理交由epoll接管
        #self.clientSocketHandle = ClientAgent(self.clientSocket, self.processObj, self.logObj )
        ClientAgent(self.clientSocket, self.processObj,_logObj=self.logObj )

    def handle_close( self ):
        self.logObj.info( "server shutdown!" )
        if os.path.exists( self.socketFile ):
            os.remove( self.socketFile  )
        self.close()

#处理客户端连接类
class ClientAgent(asyncoreEpoll.dispatcher):
    def __init__(self, socket, _processObj=None, _logObj=None, _chunkSize=2048):
        #要送出的data
        self.sendData=""
        asyncoreEpoll.dispatcher.__init__(self, socket)
        self.processObj = _processObj
        self.chunkSize = _chunkSize
        self.logObj=_logObj

    #从client收到的data，直接扔给远端tcp,获取响应后，把响应数据回写sendData,epoll自动触发handle_write事件回写客户端
    def handle_read(self):
        self.reciveData = self.recv(MAX_RECV)
        if len( self.reciveData ) > 0:
            #self.logObj.debug( "recv:%s" % self.reciveData  )
            try:
                self.sendData =  self.processObj.do( self.reciveData )
                #self.logObj.info( "recv:%s|value:%s" % (self.reciveData, processValue ) )
                #self.sendData = processValue
            except Exception as err:
                self.logObj.info('tcpConnectionPoll error:%s'% str(err))

    #送出data到client,写完成后主动断开
    def handle_write(self,sendData=""):
        if self.sendData != "":
            sentLen = self.send( self.sendData )
            #可能发不完
            #if sentLen < len( self.sendData ):
            #    self.sendData = self.sendData[sentLen:]
            #    self.logObj.info('handle_write() -> (%d) "%s"'%(  sentLen, self.sendData[:sentLen] ))
            #else:
            #    #self.logObj.info('handle_write() -> (%d) "%s"'%(  sentLen, self.sendData[:sentLen] ))
            #    self.sendData=""

    def writeable(self):
        return False#bool(len(self.sendData)>0)

    def handle_close(self):
        self.processObj.disconnect()
        self.logObj.info( "close connection : %s " % str( self.socket ) )
        self.close()
