from client import testClient
from appLib import workerProcessList
import os
import redis.connection as redisParser


clientObj1 = testClient.testClient( os.sys.argv[1] )
socketFileList = workerProcessList.getClientSocketFileList( clientObj1.getConf() )
redisObj = redisParser.Connection()
for i in range( len( socketFileList ) ):
    #clientObj = testClient.testClient( os.sys.argv[1],socketFileList[i] )
    clientObj = testClient.testClient( os.sys.argv[1],"/tmp/localhost-6379.sock" )
    redisCMD = redisObj.pack_command('set','a',1)
    #print redisCMD
    print "/tmp/localhost-6379.sock"
    clientObj.send(redisCMD)
    print clientObj.getRecivedData()
    clientObj.close()
    os.sys.exit(1)
