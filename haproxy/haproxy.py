#   Copyright 2012-2013 STACKOPS TECHNOLOGIES S.L.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.from fabric.api import *
import MySQLdb

from fabric.api import *
from cuisine import *



def stop():
    with settings(warn_only=True):
        sudo("service haproxy stop")


def start():
    stop()
    sudo("service haproxy start")


def uninstall():
    """Uninstall haproxy packages"""
    package_clean('haproxy')


def install():
    package_ensure('haproxy')


def configure():
    
    haproxy_conf = text_strip_margin('''
	|global
        |log 127.0.0.1   local0
        |#log global
        |#log loghost    local0 info
        |maxconn 4096
        |#chroot /usr/share/haproxy
        |user haproxy
        |group haproxy
        |daemon
        |#debug
        |#quiet
	|
	|defaults
        |log  global
        |maxconn  8000
        |option  redispatch
        | retries  3
        | timeout  http-request 10s
        | timeout  queue 1m
        | timeout  connect 10s
        | timeout  client 60s
        | timeout  server 60s
        | timeout  check 10s
	|
	|listen galera-cluster 10.15.18.241:3306
	|mode tcp
	|balance  roundrobin
	|option  tcplog
	|option tcpka
	|option mysql-check user haproxy
	|server  backend-3-7e2d03107a5a 10.15.18.118:3306 check
	|server  backend-3-625f3a73b3a6 10.15.18.109:3306 check
	|server  backend-3-f0f9806b8f28 10.15.18.7:3306  check backup
	|
	|listen rabbitmq_cluster 10.15.18.241:4369
	|mode tcp
	|balance roundrobin
	|#balance roundrobin
	|server  backend-3-7e2d03107a5a 10.15.18.118:4369 check inter 5000 downinter 500
	|server  backend-3-625f3a73b3a6 10.15.18.109:4369 check inter 5000 downinter 500
	|server  backend-3-f0f9806b8f28 10.15.18.7:4369   backup check inter 5000
	|
	|listen rabbitmq_cluster_openstack 10.15.18.241:5672
	|
	|timeout  connect 0s
	|timeout  client 0s
	|timeout  server 0s
	|timeout  check 0s
	|
	| mode tcp
	| balance roundrobin
	| option tcpka
	| option  forwardfor
	| server  backend-3-7e2d03107a5a 10.15.18.118:5672 check inter 5000 downinter 500  rise 2 fall 3
	| server  backend-3-625f3a73b3a6 10.15.18.109:5672 check inter 5000 downinter 500  rise 2 fall 3
	| server  backend-3-f0f9806b8f28 10.15.18.7:5672   backup check inter 5000
        |''' 
        )
    sudo('''echo '%s' > /etc/haproxy/haproxy.cfg''' % haproxy_conf)




