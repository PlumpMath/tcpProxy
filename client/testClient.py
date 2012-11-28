#coding=utf-8
from baseLib import asyncoreEpoll,commFunc
import ConfigParser,logging,socket

#收到数据库的最大长度
MAX_RECV = 4096
#连线server的socket

class testClient(asyncoreEpoll.dispatcher):
    def __init__(self, _confFile=None, socketFile=None ):
        asyncoreEpoll.dispatcher.__init__(self)
        self.sendData = ""
        self.recivedData = ""

        cfObj = ConfigParser.ConfigParser()
        cfObj.read( _confFile )
        confIniDict = commFunc.convertListToDict( cfObj )
        self.logObj = logging
        self.logObj.basicConfig(
            filename=confIniDict[ 'client' ][ 'log' ],
            filemode='a+',
            format='%(asctime)s %(levelname) 5s %(name)s | %(message)s %(filename)s %(module)s %(lineno)d',
            datefmt='%Y-%m-%dT%H:%M:%S%z',
            level=commFunc.logDict[ confIniDict['default']['loglevel'] ])
        #self.logObj.getLogger('monitor')

        self.confDict = confIniDict
        #和server建立连接
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if ( not isinstance( socketFile,type(None)) ):
            self.connect(socketFile)

    def getConf(self):
        return self.confDict

    def getRecivedData(self):
        if ( len(self.recivedData)==0):
            self.handle_read()
            return self.recivedData

    def handle_connect(self):
        self.logObj.info( "handle_connect!" )

    def handle_close(self):
        self.logObj.info( "connect close!" )
        self.close()

    #收到的data
    def handle_read(self):
        self.logObj.info( "client handle_read begin!" )
        while True:
            try:
                self.recivedData = self.recv(MAX_RECV)
                #由于使用的是异步所以要try
                if len(self.recivedData)>0:
                    self.logObj.info( "recv:%s" % (self.recivedData ) )
                    break
            except:
                pass

    def writable(self):
        return False

