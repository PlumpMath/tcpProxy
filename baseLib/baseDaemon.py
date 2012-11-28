#coding=utf-8
import os,sys,atexit
"""
daemon进程的基类，完成如下功能：
1.daemon进程fork
2.daemon进程的pid文件生成与自动删除
"""
__version__ = 0.1

class baseDaemon(object):

    def __init__(self,_logObj=None):
        self.logObj = _logObj
        #firstfock后的主进程与子进程的状态标识，便于fork多个子进程,firstfock后的主进程最终fork完所有子进程后要退出,由子进程中的一个进程来控制其它进程
        self.mainProcessFlag = True

        self.pidFile= None
        #进程名，便于程序调试
        self.processName = None
    #私有方法，继承不可调用

    def __dettachEnv(self):
        os.chdir("/")
        os.setsid()
        os.umask(0)

    #私有方法，继承不可调用
    #daemon进程的第一次fork函数，fork完成后，主程序退出，子进程接管为主程序，后续程序mainProcessFlag来判断是否为主进程，此进程fork完成所有子进程后会主动退出
    def __forkMainProcess(self):
        #第一次fork后启动程序退出,由丢弃终端后的当前进程升为主程序
        pid = self.__fork( )
        #主程序退出
        if pid > 0:
            self.processName = 'mainProcess(%d)' % pid
            self.logObj.debug( 'mainProcess pid(%d) fork success' % pid )
            sys.exit(0)
        #子进程接管主进程进行后续的fork处理
        else:
            self.mainProcessFlag = True

    #私有方法，继承不可调用
    #最原始的fork
    def __fork( self ):
        #first fork
        try:
            pid = os.fork()
            #父进程根据条件决定是否退出
            return pid
        except OSError as e:
            self.logObj.error( str(e))
            sys.exit(1)

    #有pidFile参数，则由pidFile供程序来发送信号处理
    #若未传入pidFile则必须注册stop信号
    def forkAppProcess(self, _pidFile=None ):
        pid = self.__fork()
        #若为main进程的话
        if ( pid > 0 ):
            return pid
        #若为子进程则需要把mainProcessFlag重置为False，便于多进程的后续判断
        else:
            self.mainProcessFlag = False
            if ( not isinstance( _pidFile, type( None ) ) ):
                self.pidFile = _pidFile
                #生成pidFile便于后续的信号控制处理
                self.createPIDFile()
                #monitor进程的信号处理由子类去定义
                #notice子类需要重写stopBySignal方法来控制进程正常结束后再shutdown进程
                #signal.signal( signal.SIGTERM, self.stopAppProcess )
                #notice子类需要重写reload方法来控制进程正常结束后再reload进程
                #signal.signal( signal.SIGUSR1, self.reloadAppProcess )
            #无pidFile则注册退出函数，便于以信号方式退出程序
            else:
                pass
                #notice子类需要重写stopBySignal方法来控制进程正常结束后再shutdown进程
                #signal.signal( signal.SIGTERM, self.stopAppProcess )
                #notice子类需要重写reload方法来控制进程正常结束后再reload进程
                #signal.signal( signal.SIGUSR1, self.reloadAppProcess )


            # Flush standart file descriptors
            sys.stdout.flush()
            sys.stderr.flush()
            return pid

    def daemonInit(self):
        self.__forkMainProcess()
        self.__dettachEnv()

    def stop(self):
        pid = self.__getPID()
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            self.logObj.debug(message % self.pidFile)
            return # not an error in a restart

        if os.path.exists(self.pidFile):
            os.remove(self.pidFile)
        sys.exit(1)

    def createPIDFile(self, _pidFile = None ):
        if ( not isinstance( _pidFile, type( None ) ) ):
            self.pidFile = _pidFile
        atexit.register(self.__delPIDFile)
        pid = str(os.getpid())
        fd = open(self.pidFile,'w+')
        fd.write("%s\n" % pid)

    #私有方法，继承不可调用
    def __delPIDFile(self):
        if ( not isinstance( self.pidFile, type( None ) ) ):
            if (os.path.isfile(self.pidFile)):
                try:
                    os.remove(self.pidFile)
                except OSError as err:
                    pass

    #私有方法，继承不可调用
    def __getPID(self):
        try:
            pf = open(self.pidFile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except (IOError, TypeError):
            pid = None
        return pid
