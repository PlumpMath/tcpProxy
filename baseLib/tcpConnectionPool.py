#coding=utf-8
import os,socket,sys
from itertools import chain

"""
tcp连接池
"""

#TCP最大接收数据长度
MAX_RECV=4096

class AuthenticationError(Exception):
    pass


class ConnectionError(Exception):
    pass


class ResponseError(Exception):
    pass


class InvalidResponse(Exception):
    pass


class DataError(Exception):
    pass


class PubSubError(Exception):
    pass


class WatchError(Exception):
    pass

class NoScriptError(ResponseError):
    pass


class tcpConnection(object):
    def __init__(self, host='localhost', port=6379,timeout=None ):
        self.pid = os.getpid()
        self.host = host
        self.port = port
        self.socket_timeout=timeout
        self._sock=None

    def __del__(self):
        try:
            self.disconnect()
        except:
            pass

    def connect(self):
        "Connects to the Redis server if not already connected"
        if self._sock:
            return
        try:
            sock = self._connect()
        except socket.error:
            e = sys.exc_info()[1]
            raise ConnectionError(self._error_message(e))

        self._sock = sock

    def _connect(self):
        "Create a TCP socket connection"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.socket_timeout)
        sock.connect((self.host, self.port))
        return sock

    def _error_message(self, exception):
        # args for socket.error can either be (errno, "message")
        # or just "message"
        if len(exception.args) == 1:
            return "Error connecting to %s:%s. %s.line(%d)" %\
                   (self.host, self.port, exception.args[0],sys._getframe().f_lineno )
        else:
            return "Error %s connecting %s:%s. %s.line(%d)" %\
                   (exception.args[0], self.host, self.port, exception.args[1],sys._getframe().f_lineno)

    def disconnect(self):
        if self._sock is None:
            return
        try:
            self._sock.close()
        except socket.error:
            pass
        self._sock = None

    def sendCommand(self, command):
        "Send an already packed command to the Redis server"
        if not self._sock:
            self.connect()
        try:
            self._sock.sendall(command)
        except socket.error:
            e = sys.exc_info()[1]
            self.disconnect()
            if len(e.args) == 1:
                _errno, errmsg = 'UNKNOWN', e.args[0]
            else:
                _errno, errmsg = e.args
            raise ConnectionError("Error %s while writing to socket. %s.line(%d)" %
                                  (_errno, errmsg,sys._getframe().f_lineno))
        except:
            self.disconnect()
            raise

    def readResponse(self):
        try:
            buffer = self._sock.recv(MAX_RECV)
            return buffer
        except (socket.error, socket.timeout):
            e = sys.exc_info()[1]
            raise ConnectionError("Error while reading from socket: %s.line(%d)" %
                                  (e.args,sys._getframe().f_lineno))
        if not buffer:
            raise ConnectionError("Socket closed on remote end.line(%d)"%sys._getframe().f_lineno)


class tcpConnectionPool(object):
    "Generic connection pool"
    def __init__(self, connection_class=tcpConnection, max_connections=None,
                 **connection_kwargs):
        self.pid = os.getpid()
        self.connection_class = connection_class
        self.connection_kwargs = connection_kwargs
        self.max_connections = max_connections or 2 ** 31
        self._created_connections = 0
        self._available_connections = []
        self._in_use_connections = set()

    def _checkpid(self):
        if self.pid != os.getpid():
            self.disconnect()
            self.__init__(self.connection_class, self.max_connections,
                **self.connection_kwargs)

    def get_connection(self, command_name, *keys, **options):
        "Get a connection from the pool"
        self._checkpid()
        try:
            connection = self._available_connections.pop()
        except IndexError:
            connection = self.make_connection()
        self._in_use_connections.add(connection)
        return connection
    def do(self,cmdArgs ):
        try:
            connObj = self.get_connection('')
            connObj.sendCommand( cmdArgs )
            return connObj.readResponse()
        except ConnectionError as err:
            raise err
        except ResponseError as err:
            raise err
        except InvalidResponse as err:
            raise err
        except AuthenticationError as err:
            raise err
        except NoScriptError as err:
            raise err


    def make_connection(self):
        "Create a new connection"
        if self._created_connections >= self.max_connections:
            raise ConnectionError("Too many connections%d"%sys._getframe().f_lineno)
        self._created_connections += 1
        return self.connection_class(**self.connection_kwargs)

    def release(self, connection):
        "Releases the connection back to the pool"
        self._checkpid()
        if connection.pid == self.pid:
            self._in_use_connections.remove(connection)
            self._available_connections.append(connection)

    def disconnect(self):
        "Disconnects all connections in the pool"
        all_conns = chain(self._available_connections,
            self._in_use_connections)
        for connection in all_conns:
            connection.disconnect()
