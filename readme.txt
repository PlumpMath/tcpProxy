

appLib:
    应用相关类
baseLib
    基础类，可以复用
conf
    配置文件

启动tcpProxy：
sh ./shell/tcpProxy.sh start

配置文件：
./conf/confi.ini

查看日志：
tail -f /var/log/tcpProxy.log

客户端测试：
python ./testClient.py ./conf/conf.ini