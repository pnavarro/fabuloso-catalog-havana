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
#   limitations under the License.

from fabric.api import *
from cuisine import *
import fabuloso.utils as utils

DESIGNATE_CONF = '/etc/designate/designate.conf'
POWERDNS_CONF = '/etc/powerdns/pdns.d/pdns.local.gmysql'


def install_packages():
    sudo('pdns-backend-mysql pdns-backend-mysql/dbconfig-install boolean false '
         '| debconf-set-selections')
    package_ensure('python-amqp')
    package_ensure('pdns-server')
    package_ensure('pdns-backend-mysql')
    package_ensure('designateclient')
    package_ensure('designate-api')
    package_ensure('designate-central')


def install():
    install_packages()


def start():
    stop()
    pdns_start()
    designate_api_start()
    designate_central_start()


def stop():
    pdns_stop()
    designate_api_stop()
    designate_central_stop()


def pdns_start():
    pdns_stop()
    sudo("service pdns start")


def pdns_stop():
    with settings(warn_only=True):
        sudo("service pdns stop")


def designate_api_start():
    designate_api_stop()
    sudo("service designate-api start")


def designate_api_stop():
    with settings(warn_only=True):
        sudo("service designate-api stop")


def designate_central_start():
    designate_central_stop()
    sudo("service designate-central start")


def designate_central_stop():
    with settings(warn_only=True):
        sudo("service designate-central stop")


def add_repos():
    """Clean and Add necessary repositories and updates"""

    package_ensure('python-software-properties')
    sudo('apt-add-repository --yes ppa:designate-ppa/havana')
    sudo('apt-get -y update')
    sudo('sudo apt-get upgrade --yes')


def set_config_file(mysql_username='designate', mysql_password='stackops',
                    mysql_host='127.0.0.1', mysql_port='3306',
                    mysql_schema_designate ='designate',
                    mysql_schema_powerdns ='powerdns', user='designate',
                    password='stackops', auth_host='127.0.0.1',
                    auth_port='35357', auth_protocol='http', tenant='service',
                    rabbit_password='guest', rabbit_host='localhost'):
    utils.set_option(DESIGNATE_CONF, 'rpc_backend',
                     'designate.openstack.common.rpc.impl_kombu')
    utils.set_option(DESIGNATE_CONF, 'rabbit_password', rabbit_password)
    utils.set_option(DESIGNATE_CONF, 'rabbit_host', rabbit_host)
    utils.set_option(DESIGNATE_CONF, 'notification_driver',
                     'designate.openstack.common.notifier.rabbit_notifier')
    utils.set_option(DESIGNATE_CONF, 'auth_strategy', 'keystone',
                     section='service:api')
    utils.set_option(DESIGNATE_CONF, 'enabled_extensions_v1',
                     'diagnostics, quotas, reports, sync',
                     section='service:api')
    utils.set_option(DESIGNATE_CONF, 'admin_tenant_name',
                     tenant, section='keystone_authtoken')
    utils.set_option(DESIGNATE_CONF, 'admin_user',
                     user, section='keystone_authtoken')
    utils.set_option(DESIGNATE_CONF, 'admin_password',
                     password, section='keystone_authtoken')
    utils.set_option(DESIGNATE_CONF, 'auth_host', auth_host,
                     section='keystone_authtoken')
    utils.set_option(DESIGNATE_CONF, 'auth_port', auth_port,
                     section='keystone_authtoken')
    utils.set_option(DESIGNATE_CONF, 'auth_protocol', auth_protocol,
                     section='keystone_authtoken')
    utils.set_option(DESIGNATE_CONF, 'auth_protocol', auth_protocol,
                     section='keystone_authtoken')
    auth_uri = 'http://' + auth_host + ':5000/v2.0'
    utils.set_option(DESIGNATE_CONF, 'auth_uri',
                     auth_uri, section='keystone_authtoken')
    utils.set_option(DESIGNATE_CONF, 'backend_driver',
                     'powerdns', section='service:central')
    utils.set_option(DESIGNATE_CONF, 'database_connection',
                     utils.sql_connect_string(mysql_host,
                                              mysql_password,
                                              mysql_port,
                                              mysql_schema_designate,
                                              mysql_username),
                     section='storage:sqlalchemy')
    utils.set_option(DESIGNATE_CONF, 'database_connection',
                     utils.sql_connect_string(mysql_host,
                                              mysql_password,
                                              mysql_port,
                                              mysql_schema_powerdns,
                                              mysql_username),
                     section='storage:sqlalchemy')
    sudo('designate-manage database-init')
    sudo('designate-manage database-sync')
    sudo('designate-manage powerdns database-init')
    sudo('designate-manage powerdns database-sync')

    #PowerDNS configuration
    sudo("sed -i 's/launch.*$/launch=%s/g' %s"
         % ('gmysql', POWERDNS_CONF))
    sudo("sed -i 's/gmysql-host.*$/gmysql-host=%s/g' %s"
         % (mysql_host, POWERDNS_CONF))
    sudo("sed -i 's/gmysql-port.*$/gmysql-port=%s/g' %s"
         % (mysql_port, POWERDNS_CONF))
    sudo("sed -i 's/gmysql-dbname.*$/gmysql-dbname=%s/g' %s"
         % (mysql_schema_powerdns, POWERDNS_CONF))
    sudo("sed -i 's/gmysql-user.*$/gmysql-user=%s/g' %s"
         % (mysql_username, POWERDNS_CONF))
    sudo("sed -i 's/gmysql-password.*$/gmysql-password=%s/g' %s"
         % (mysql_host, POWERDNS_CONF))
    sudo("sed -i 's/gmysql-dnssec.*$/gmysql-dnssec=%s/g' %s"
         % ('yes', POWERDNS_CONF))