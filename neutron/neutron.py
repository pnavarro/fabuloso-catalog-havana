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
from fabric.api import settings, sudo
from cuisine import package_clean, package_ensure
from fabuloso import fabuloso

import fabuloso.utils as utils

NEUTRON_API_PASTE_CONF = '/etc/neutron/api-paste.ini'

OVS_PLUGIN_CONF = '/etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini'

NEUTRON_CONF = '/etc/neutron/neutron.conf'


def neutron_server_stop():
    with settings(warn_only=True):
        sudo("service neutron-server stop")


def neutron_server_start():
    neutron_server_stop()
    sudo("service neutron-server start")


def stop():
    neutron_server_stop()


def start():
    neutron_server_start()


def uninstall_ubuntu_packages():
    """Uninstall openvswitch and neutron packages"""
    package_clean('python-amqp')
    package_clean('neutron-server')
    package_clean('neutron-plugin-openvswitch')
    package_clean('python-pyparsing')
    package_clean('python-mysqldb')


def install(cluster=False):
    """Generate neutron configuration. Execute on both servers"""
    """Configure openvwsitch and neutron packages"""
    package_ensure('python-amqp')
    package_ensure('neutron-server')
    package_ensure('neutron-plugin-openvswitch')
    package_ensure('python-pyparsing')
    package_ensure('python-mysqldb')
    if cluster:
        stop()


def set_config_file(user='neutron', password='stackops', auth_host='127.0.0.1',
                    auth_port='35357', auth_protocol='http', tenant='service'):
    utils.set_option(NEUTRON_API_PASTE_CONF, 'admin_tenant_name',
                     tenant, section='filter:authtoken')
    utils.set_option(NEUTRON_API_PASTE_CONF, 'admin_user',
                     user, section='filter:authtoken')
    utils.set_option(NEUTRON_API_PASTE_CONF, 'admin_password',
                     password, section='filter:authtoken')
    utils.set_option(NEUTRON_API_PASTE_CONF, 'auth_host', auth_host,
                     section='filter:authtoken')
    utils.set_option(NEUTRON_API_PASTE_CONF, 'auth_port',
                     auth_port, section='filter:authtoken')
    utils.set_option(NEUTRON_API_PASTE_CONF, 'auth_protocol',
                     auth_protocol, section='filter:authtoken')
    auth_uri = 'http://' + auth_host + ':5000/v2.0'
    utils.set_option(NEUTRON_API_PASTE_CONF, 'auth_uri',
                     auth_uri, section='filter:authtoken')
    utils.set_option(NEUTRON_CONF, 'notification_driver',
                     'neutron.openstack.common.notifier.rabbit_notifier')
    utils.set_option(NEUTRON_CONF, 'notification_topics',
                     'notifications,monitor')
    utils.set_option(NEUTRON_CONF, 'default_notification_level', 'INFO')
    # Configurtin LBAAS service
    utils.set_option(NEUTRON_CONF, 'service_plugins',
                     'neutron.plugins.services.'
                     'agent_loadbalancer.plugin.LoadBalancerPlugin')
    cp = 'neutron.plugins.openvswitch.ovs_neutron_plugin.OVSNeutronPluginV2'
    utils.set_option(NEUTRON_CONF, 'core_plugin', cp)


def configure_ovs_plugin_vlan(vlan_start='1', vlan_end='4094',
                              mysql_username='neutron',
                              mysql_password='stackops',
                              mysql_host='127.0.0.1',
                              mysql_port='3306', mysql_schema='neutron'):
    utils.set_option(OVS_PLUGIN_CONF, 'sql_connection',
                     utils.sql_connect_string(mysql_host, mysql_password,
                                              mysql_port, mysql_schema,
                                              mysql_username),
                     section='DATABASE')
    utils.set_option(OVS_PLUGIN_CONF, 'reconnect_interval', '2',
                     section='DATABASE')
    utils.set_option(OVS_PLUGIN_CONF, 'tenant_network_type', 'vlan',
                     section='OVS')
    utils.set_option(OVS_PLUGIN_CONF, 'network_vlan_ranges', 'physnet1:%s:%s'
                     % (vlan_start, vlan_end), section='OVS')
    utils.set_option(OVS_PLUGIN_CONF, 'root_helper',
                     'sudo /usr/bin/neutron-rootwrap '
                     '/etc/neutron/rootwrap.conf',
                     section='AGENT')


def validate_database(database_type, username, password, host, port,
                      schema, drop_schema=None, install_database=None):
    fab = fabuloso.Fabuloso()
    fab.validate_database(database_type, username, password, host, port,
                          schema, drop_schema, install_database)


def validate_credentials(user, password, tenant, endpoint, admin_token):
    fab = fabuloso.Fabuloso()
    fab.validate_credentials(user, password, tenant, endpoint, admin_token)


def validate_rabbitmq(service_type, host, rport=None, ruser=None,
                      rpassword=None, virtual_host=None):
    fab = fabuloso.Fabuloso()
    fab.send_rabbitMQ(service_type, host, rport, ruser, rpassword,
                      virtual_host)
