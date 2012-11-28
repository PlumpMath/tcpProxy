# coding=utf-8
import os,signal
from . import baseDaemon
"""
monitor控制类,此为主程序的入口
1.根据monitorProcess对象来初始化配置与日志
2.创建monitor进程与worker进程列表，并运行
3.注册全局信号处理函数(stop/start/restart/stop)
4.为monitor进程配置所有worker进程id号，供后续的status/stop信号处理
"""

class monitorDaemon(baseDaemon.baseDaemon):

    def __init__(self,  _monitorProcessObj=None ):
        self.init( _monitorProcessObj )

    def init(self, _monitorProcessObj=None ):

        self.logObj = _monitorProcessObj.getLogObj()
        baseDaemon.baseDaemon.__init__(self, _logObj = self.logObj )
        baseDaemon.baseDaemon.daemonInit(self)
        self.monitorProcessObj = _monitorProcessObj
        self.workerProcessObjList = self.monitorProcessObj.workerProcessObjList
        self.workerProcessPIDList = dict()
        #监控进程标识
        self.monitorFlag = False


    #内部方法，不为继承调用
    def __forkMonitorProcess(self ):
        pid = self.forkAppProcess( self.monitorProcessObj.pidFile )
        #若为mainProcess进程的话，则fork完monitor进程后退出，由monitor进程接管后续的fork workerprocess
        if ( pid > 0 ):
            self.logObj.info("mainProcess(%d) fork monitor process success monitor process fork worker process!" % os.getpid())
            os.sys.exit(1)
        else:
            #fork完成后，monitor进程号已经写了pidFile文件，控制台通过脚本来控制monitor进程
            self.logObj.info( 'monitorProcess (%s) fork end!' % self.monitorProcessObj.pidFile )
            #把第一个进程做为monitor进程
            self.monitorProcessObj.monitorFlag = True
            self.monitorFlag = True
            #定义monitor进程要注册的信号与执行的函数
            self.__setMonitorSignal()

    #1.由monitor进程进行fork,fork完成后直接runworkerProcess
    #2.注册进程号与对象到monitor进程队列，便于后续的ping操作来重启进程
    #内部方法，不为继承调用
    def __forkWorkerProcess(self, _appObj=None ):
        #若为主进程则进行fork
        if ( self.monitorFlag ):
            #子进程以管道方式回传进程id号
            r,w = os.pipe()
            #由monitor进程fork workerprocess进程，此子进程已经注册了退出信号
            pid  = self.forkAppProcess( )
            #monitor进程fork完成后不做任何事务
            if ( pid > 0 ):
                workerProcessPID = self.__getWorkerProcessPID( r,w )
                self.workerProcessPIDList[ workerProcessPID ] = _appObj
            else:
                self.monitorFlag = False
                self.__resetWorkerProcessVariables(r,w)
                self.logObj.info( 'workerProcess (%d) fork end!' % os.getpid() )
                _appObj.run()

        #非monitor进程则什么都不做
        else:
            pass

    #取得workerProcess进程ID号并关闭管道
    def __getWorkerProcessPID( self, r=None,w=None ):
        if ( self.monitorFlag ):
            os.close(w)
            r1 = os.fdopen( r )
            pidValue = r1.read()
            r1.close()
            workerProcessPID = int( pidValue )
            return workerProcessPID

    #重置workerProcess的monitor进程的无用变量
    def __resetWorkerProcessVariables(self,r=None, w=None):
        if ( not self.monitorFlag ):
            os.close(r)
            w1 = os.fdopen( w, 'w' )
            processID = os.getpid()
            w1.write( str(processID) )
            w1.close()
            self.monitorProcessObj = None
            self.workerProcessObjList = None
            self.workerProcessPIDList = None

    #shutdown所有worker process进程，内部函数，继承不可调用
    def __stopWorkerProcessList(self):
        if ( self.monitorFlag ):
            for pid,appObj in self.workerProcessPIDList.items():
                try:
                    #notice os.kill failed and push
                    #发送信号给所有的worker子进程,worker子进程收到信号后自动触发stop函数后退出子进程
                    os.kill( pid, signal.SIGTERM )
                    self.workerProcessPIDList.pop( pid )
                    self.logObj.info("kill subProcess(%d) and remove workerProcessPIDList" % pid )
                except IndexError as err:
                    break

    #进入daemon状态后的信号执行函数
    def __setMonitorSignal(self):
        if ( self.monitorFlag ):
            signal.signal( signal.SIGTERM, self.__stopMonitorBySignal )
            signal.signal( signal.SIGUSR1, self.__reloadMonitorBySignal)
            signal.signal( signal.SIGUSR2, self.__restartMonitorBySignal )

    #私有函数，继承不可调用
    def __startWorkerProcessList(self):
        if (self.monitorFlag):
            appListLen = len( self.workerProcessObjList )
            for i in range( appListLen ):
                self.__forkWorkerProcess( self.workerProcessObjList[ i ] )
        self.monitorProcessObj.run()

    #由信号触发
    def __restartMonitorBySignal(self, __num, __frame):
        if ( self.monitorFlag ):
            self.logObj.info('stop monitor process...!')
            self.stopMonitor()
            self.logObj.info('start monitor process...!')
            self.startMonitor()

    #由信号触发
    def __stopMonitorBySignal(self, _num, _frame ):
        if (self.monitorFlag):
            self.__stopWorkerProcessList()
            self.monitorProcessObj.stopStatus = True
            #退出主进程并删除pid文件
            self.stop()

    #由信号触发?有bug
    def __reloadMonitorBySignal(self, __num, __frame ):
        if ( self.monitorFlag ):

            self.logObj.info("------------reload begin signal(%d)-------------!" % __num )
            self.logObj.info('stop worker processlist start!')
            self.__stopWorkerProcessList()
            self.logObj.info('stop worker processlist end!')

            self.logObj.info('reload monitor process start!')

            self.monitorProcessObj.reload()
            self.logObj.info('reload monitor process end!')
            self.logObj.debug('monitor Daemon init begin!')
            self.init( self.monitorProcessObj )
            self.logObj.debug('monitor Daemon init end!')
            self.logObj.info('worker process list start begin!')
            self.monitorFlag = True
            self.__startWorkerProcessList()

            self.logObj.info('worker process list start end!')
            self.createPIDFile( self.monitorProcessObj.pidFile )
            self.monitorProcessObj.run()
            self.logObj.info("------------reload end signal(%d)-------------!" % __num )

    #主程序调用
    def startMonitor( self ):
        #启动monitor进程,monitor未运行
        self.__forkMonitorProcess()
        #由monitor进程forkworkerProcess
        if ( self.monitorFlag ):
            self.__startWorkerProcessList(  )
        #fork完workerProcess进程后monitor进程进入监控状态
        if ( self.monitorFlag ):
            self.monitorProcessObj.run()

    #pingworker进程是否正常，不正常要重启，待开发并测试
    def pingWorkerProcessList(self):
        if ( self.monitorFlag ):
            for pid,appObj in self.workerProcessPIDList.items():
                try:
                    os.kill(pid, 0 )
                except OSError as err:
                    self.workerProcessPIDList.remove( pid )
                    self.__forkWorkerProcess(appObj)
                    self.logObj.critical(str(err)+ ( "(%d) is failed and restart!" % pid ) )
