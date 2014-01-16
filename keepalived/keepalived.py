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

from fabric.api import settings, sudo, put, local, puts
from cuisine import package_ensure, package_clean
from fabuloso import fabuloso


def stop():
    with settings(warn_only=True):
        sudo("service keepalived stop")


def start():
    stop()
    sudo("service keepalived start")


def uninstall():
    """Uninstall keepalived packages"""
    package_clean('keepalived')


def install():
    package_ensure('keepalived')


def configure():
    sudo('echo "net.ipv4.ip_nonlocal_bind=1" >> /etc/sysctl.conf')
    sudo('sysctl -p')
    
    keepalived_conf = text_strip_margin('''
	    |# Configuration File for keepalived
	    |global_defs {
	    |# each load balancer should have a different ID
	    |# this will be used in SMTP alerts, so you should make
	    |# each router easily identifiable
	    |lvs_id LB1
	    |}
	    |
	    |#health-check for keepalive
	    |vrrp_script chk_nginx { # Requires keepalived-1.1.13
	    |	#script "killall -0 nginx" # cheaper than pidof
	    |	script ''"pidof nginx"'' 
	    |	interval 2 # check every 2 seconds
	    |	weight 2 # add 2 points of prio if OK
	    |}
	    |
	    |vrrp_instance VI_1 {
	    |	state MASTER
	    |	interface eth0
	    |	  
	    |	# each virtual router id must be unique per instance name#
	    |	virtual_router_id 51
	    |	# MASTER and BACKUP state are determined by the priority
	    |	# even if you specify MASTER as the state, the state will
	    |	# be voted on by priority (so if your state is MASTER but 
	    |	# your priority is lower than the router with BACKUP, you 
	    |	# will lose the MASTER state)
	    |   priority 101
	    |
	    |	#check if we are still running
	    |	track_script {
	    |		chk_nginx
	    |	}
	    |	
	    |	# these are the IP addresses that keepalived will setup on 
	    |	# this without this block, keepalived will not setup and 
	    |	# takedown the IP addresses
	    |	virtual_ipaddress {
	    |	172.22.23.200
	    |	}
	    |}
	    |''' 
            )
    sudo('''echo '%s' > /etc/keepalived/keepalived.conf''' % keepalived_conf)




