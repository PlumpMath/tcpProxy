<?php
define('CUR_FILE_PATH', dirname(__FILE__)."/");
$confFilePath = CUR_FILE_PATH.'../conf/conf.ini';

#指令重复次数
define( 'CMD_REPEAT_COUNT', 100000 );


function getSocketObj( $socket="127.0.0.1:6379" )
{
    $redisObj = new Redis();
    $socketInfo = explode( ":", $socket );
    if ( count( $socketInfo ) > 1 )
        $redisObj->connect( $socketInfo[0], $socketInfo[1] );
    else
        $redisObj->connect( $socket );
    return $redisObj;
}

$socketFile = "/tmp/localhost-6379.sock";

$socket= isset( $_REQUEST['socket'] )?$_REQUEST['socket']:'127.0.0.1:6379';
$redisObj = getSocketObj( $socket );
print_r( $redisObj );
$redisObj->set('a', '1');
$redisObj->close();
$endTime = time();
echo "socket:".$socket."\n";
echo "set:endTime-beginTime=".($endTime-$beginTime)."\n";
?>
