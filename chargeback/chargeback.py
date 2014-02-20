#   Copyright 2012-2013 STACKOPS TECHNOLOGIES S.L.
from fabric.api import settings, sudo
from cuisine import package_ensure, package_clean


def stop():
    with settings(warn_only=True):
        sudo("nohup service tomcat7 stop")


def start():
    stop()
    sudo("nohup service tomcat7 start")


def configure_ubuntu_packages():
    """Configure java, tomcat and mysql client packages"""
    package_ensure('openjdk-7-jdk')
    package_ensure('tomcat7')
    package_ensure('mysql-client')


def uninstall_ubuntu_packages():
    """Uninstall accounting and chargeback packages"""
    package_clean('stackops-chargeback')


def configure_chargeback(mysql_chargeback_username='chargeback',
                         mysql_chargeback_password='stackops',
                         mysql_chargeback_host='localhost',
                         mysql_chargeback_port='3306',
                         mysql_chargeback_schema='chargeback',
                         mysql_activity_schema='activity',
                         mysql_chargeback_root_password='stackops',
                         service_chargeback_user='chargeback',
                         service_chargeback_password='stackops',
                         admin_token='password',
                         auth_host='127.0.0.1',
                         auth_port='35357',
                         auth_protocol='http',
                         auth_uri='/v2.0', install_db='True'):
    """Generate chargeback configuration. Execute on both servers"""
    sudo('echo stackops-chargeback stackops-chargeback/mysql-install boolean %s '
         '| debconf-set-selections' % install_db)
    sudo('echo stackops-chargeback stackops-chargeback/mysql-usr string '
         '%s | debconf-set-selections' % mysql_chargeback_username)
    sudo('echo stackops-chargeback stackops-chargeback/mysql-password '
         'password %s | debconf-set-selections' % mysql_chargeback_password)
    sudo('echo stackops-chargeback stackops-chargeback/mysql-schema string '
         '%s | debconf-set-selections' % mysql_chargeback_schema)
    sudo('echo stackops-chargeback stackops-chargeback/mysql-activity-schema '
         'string %s | debconf-set-selections' % mysql_activity_schema)
    sudo('echo stackops-chargeback stackops-chargeback/mysql-host string %s '
         '| debconf-set-selections' % mysql_chargeback_host)
    sudo('echo stackops-chargeback stackops-chargeback/mysql-port string %s '
         '| debconf-set-selections' % mysql_chargeback_port)
    sudo('echo stackops-chargeback stackops-chargeback/mysql-admin-password '
         'password %s | debconf-set-selections' %
         mysql_chargeback_root_password)
    sudo('echo stackops-chargeback stackops-chargeback/mysql-purgedb boolean '
         'true | debconf-set-selections')
    sudo('echo stackops-chargeback stackops-chargeback/'
         'present-stackops-license boolean true | debconf-set-selections')
    sudo('echo stackops-chargeback stackops-chargeback/keystone-usr string %s '
         '| debconf-set-selections' % service_chargeback_user)
    sudo('echo stackops-chargeback stackops-chargeback/keystone-password '
         'password %s | debconf-set-selections' % service_chargeback_password)
    sudo('echo stackops-chargeback stackops-chargeback/keystone-url string '
         '%s://%s:%s%s | debconf-set-selections' % (auth_protocol,
                                                    auth_host,
                                                    auth_port, auth_uri))
    sudo('echo stackops-chargeback stackops-chargeback/keystone-admin-token '
         'string %s | debconf-set-selections' % admin_token)
    package_ensure('stackops-chargeback')


def configure_chargeback_without_db(mysql_chargeback_username='chargeback',
                         mysql_chargeback_password='stackops',
                         mysql_chargeback_host='localhost',
                         mysql_chargeback_port='3306',
                         mysql_chargeback_schema='chargeback',
                         mysql_activity_schema='activity',
                         mysql_chargeback_root_password='stackops',
                         service_chargeback_user='chargeback',
                         service_chargeback_password='stackops',
                         admin_token='password',
                         auth_host='127.0.0.1',
                         auth_port='35357',
                         auth_protocol='http',
                         auth_uri='/v2.0'):
    configure_chargeback(mysql_chargeback_username, mysql_chargeback_password,
                         mysql_chargeback_host, mysql_chargeback_port,
                         mysql_chargeback_schema, mysql_activity_schema,
                         mysql_chargeback_root_password,
                         service_chargeback_user, service_chargeback_password,
                         admin_token, auth_host, auth_port, auth_protocol,
                         auth_uri, 'False')