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

#import utils


def stop():
    with settings(warn_only=True):
        sudo("nohup service nginx stop")


def start():
    stop()
    sudo("nohup service nginx start")


def configure_ubuntu_packages():
    """Configure nginx packages"""
    package_ensure('python-software-properties')
    sudo('add-apt-repository  -y ppa:nginx/stable') 
    sudo('apt-get update')
    package_ensure('nginx')


def uninstall_ubuntu_packages():
    """Uninstall nginx packages"""
    package_clean('nginx')


def install():
    configure_ubuntu_packages()


def configure(ec2_internal_host="127.0.0.1",
              compute_internal_host="127.0.0.1",
              keystone_internal_host="127.0.0.1",
              glance_internal_host="127.0.0.1",
              cinder_internal_host="127.0.0.1",
              neutron_internal_host="127.0.0.1",
              portal_internal_host="127.0.0.1",
              activity_internal_host="127.0.0.1",
              chargeback_internal_host="127.0.0.1",
              common_name='127.0.0.1'):
    """Generate apache configuration. Execute on both servers"""
    ec2_internal_url="http://" + ec2_internal_host + ":8773/services/Cloud"
    compute_internal_url="http://" + compute_internal_host + ":8774/v1.1"
    keystone_internal_url="http://" + keystone_internal_host + ":5000/v2.0"
    glance_internal_url="http://" + glance_internal_host + ":9292/v1"
    cinder_internal_url="http://" + cinder_internal_host + ":8776/v1"
    neutron_internal_url="http://" + neutron_internal_host + ":9696/v2.0"
    portal_internal_url="http://" + portal_internal_host + ":8080/portal"
    activity_internal_url="http://" + activity_internal_host + \
                          ":8080/activity"
    chargeback_internal_url="http://" + chargeback_internal_host + \
                            ":8080/chargeback"
     #configure_ubuntu_packages()
    sudo('mkdir -p /var/log/nova')
    configure_nginx(ec2_internal_url, compute_internal_url,
                     keystone_internal_url, glance_internal_url,
                     cinder_internal_url, neutron_internal_url,
                     portal_internal_url, activity_internal_url,
                     chargeback_internal_url, None, common_name)
    configure_nginx_ssl(ec2_internal_url, compute_internal_url,
                         keystone_internal_url, glance_internal_url,
                         cinder_internal_url, neutron_internal_url,
                         portal_internal_url, activity_internal_url,
                         chargeback_internal_url,
                         None, common_name)
    create_certs(common_name)
    stop()
    start()


def configure_nginx(ec2_internal_url="http://127.0.0.1:8773/services/Cloud",
                     compute_internal_url="http://127.0.0.1:8774/v1.1",
                     keystone_internal_url="http://127.0.0.1:5000/v2.0",
                     glance_internal_url="http://127.0.0.1:9292/v1",
                     cinder_internal_url="http://127.0.0.1:8776/v1",
                     neutron_internal_url="http://127.0.0.1:9696/v2.0",
                     portal_internal_url="http://127.0.0.1:8080/portal",
                     activity_internal_url="http://127.0.0.1:8080/activity",
                     chargeback_internal_url="http://127.0.0.1:8080/"
                                             "chargeback",
                     nginx_conf=None, common_name='127.0.0.1'):
    if nginx_conf is None:
        nginx_conf = text_strip_margin('''
        |
	|server {
        |listen 80;
        |server_name %s;
    	|access_log /var/log/nginx/stackops_access_log;
        |error_log /var/log/nginx/stackops_error_log;
        |root /var/lib/tomcat7/webapps/;
        |rewrite  ^ https://$server_name$request_uri? permanent;
        |
	|
        |location / {
        |        deny all;
        |}
	|
	|location /services/ {
        |proxy_pass %s;
        |}
	|
	|location /compute/v1.1/ {
        |proxy_pass %s;
        |}
	|
	|location /keystone/v2.0/ {
        |proxy_pass %s;
        |}
	|
	|location /glance/ {
        |proxy_pass %s;
        |}
	|
	|location /volume/v1 {
        |proxy_pass %s;
        |}
	|
	|location /network {
	|proxy_pass %s;
	|}
	|
	|location /portal/ {
        |index index.jsp;
        |proxy_set_header X-Forwarded-Host $host;
        |proxy_set_header X-Forwarded-Server $host;
        |proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        |proxy_pass %s;
	|
        |proxy_buffering off;
        |proxy_store     off;
	|
        |proxy_connect_timeout 120;
        |proxy_send_timeout    120;
        |proxy_read_timeout    120;
    	|}
	|
	| location /activity/ {
        |proxy_pass %s;
        |}
	|
	|location /accounting {
        |proxy_pass %s;
        |}
	|
	|location /chargeback {
        |proxy_pass %s;
        |}
	|''' % (common_name, ec2_internal_url,
                compute_internal_url, keystone_internal_url,
                glance_internal_url, cinder_internal_url,
                neutron_internal_url, portal_internal_url,
                activity_internal_url, activity_internal_url,
                chargeback_internal_url))
    sudo('''echo '%s' > /etc/nginx/sites-available/default''' % nginx_conf)


def configure_nginx_ssl(ec2_internal_url="http://127.0.0.1:8773/services"
                                          "/Cloud",
                         compute_internal_url="http://127.0.0.1:8774/v1.1",
                         keystone_internal_url="http://127.0.0.1:5000/v2.0",
                         glance_internal_url="http://127.0.0.1:9292/v1",
                         cinder_internal_url="http://127.0.0.1:8776/v1",
                         neutron_internal_url="http://127.0.0.1:9696/v2.0",
                         portal_internal_url="http://127.0.0.1:8080/portal",
                         activity_internal_url="http://127.0.0.1:8080"
                                               "/activity",
                         chargeback_internal_url="http://127.0.0.1:8080"
                                                 "/chargeback",
                         nginx_conf=None, common_name='127.0.0.1'):
    if nginx_conf is None:
        nginx_conf = text_strip_margin('''
        |
        |server {
   	|listen              443 ssl;
    	|ssl_certificate     /etc/ssl/certs/sslcert.crt;
    	|ssl_certificate_key /etc/ssl/private/sslcert.key;
	|server_name %s;
    	|access_log /var/log/nginx/stackops_access_log;
        |error_log /var/log/nginx/stackops_error_log;
        |root /var/lib/tomcat7/webapps/;
	|
        |location / {
        |        deny all;
        |}
	|
	|location /services/ {
        |proxy_pass %s;
        |}
	|
	|location /compute/v1.1/ {
        |proxy_pass %s;
        |}
	|
	|location /keystone/v2.0/ {
        |proxy_pass %s;
        |}
	|
	|location /glance/ {
        |proxy_pass %s;
        |}
	|
	|location /volume/v1 {
        |proxy_pass %s;
        |}
	|
	|location /network {
	|proxy_pass %s;
	|}
	|
	|location /portal/ {
        |index index.jsp;
        |proxy_set_header X-Forwarded-Host $host;
        |proxy_set_header X-Forwarded-Server $host;
        |proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        |proxy_pass %s;
	|
        |proxy_buffering off;
        |proxy_store     off;
	|
        |proxy_connect_timeout 120;
        |proxy_send_timeout    120;
        |proxy_read_timeout    120;
    	|}
	|
	| location /activity/ {
        |proxy_pass %s;
        |}
	|
	|location /accounting {
        |proxy_pass %s;
        |}
	|
	|location /chargeback {
        |proxy_pass %s;
        |}
	|}
        |''' % (common_name, ec2_internal_url,
                compute_internal_url, keystone_internal_url,
                glance_internal_url, cinder_internal_url, 
                neutron_internal_url, portal_internal_url,
                activity_internal_url, activity_internal_url,
                chargeback_internal_url))
    sudo('''echo '%s' > /etc/nginx/sites-available/default-ssl'''
         % nginx_conf)
    sudo('ln -s /etc/nginx/sites-available/default-ssl /etc/nginx/sites-enabled/default-ssl')


def configure_iptables(public_ip):
    package_ensure('iptables-persistent')
    sudo('service iptables-persistent flush')
    iptables_conf = text_strip_margin('''
    |
    |# Generated by iptables-save v1.4.4
    |*filter
    |:INPUT ACCEPT [0:0]
    |:FORWARD ACCEPT [0:0]
    |:OUTPUT ACCEPT [0:0]
    |-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
    |-A INPUT -d %s/32 -p tcp -m tcp --dport 80 -j ACCEPT
    |-A INPUT -d %s/32 -p tcp -m tcp --dport 6080 -j ACCEPT
    |-A INPUT -d %s/32 -p tcp -m tcp --dport 443 -j ACCEPT
    |-A INPUT -d %s/32 -p icmp -m icmp --icmp-type echo-request -j ACCEPT
    |-A INPUT -d %s/32 -j DROP
    |COMMIT
    |''' % (public_ip, public_ip, public_ip, public_ip, public_ip))
    sudo('echo "%s" > /etc/iptables/rules.v4' % iptables_conf)
    sudo('service iptables-persistent start')


def create_certs(common_name='127.0.0.1'):
    nonsecurekey = text_strip_margin('''
    |-----BEGIN RSA PRIVATE KEY-----
    |MIIEowIBAAKCAQEAtO4zZwNYOzux+ymvrW7kMojJ9diI7WxmPvESa1FNdY45TN5Z
    |WYSYcgYKDT/OuHDi9+49LlRPksV35scGNIJbqV9Cr4L0vHXfb9E9EdOIIkv3jOG9
    |QhhwIPxKrpJQP1hkPyxybWkH/IVHY06OxLIWPJO3NC74sQQvXZ2mMUoOW5KcQwiK
    |GfWf3mJKCccocNv3MXP4cb6ay7DQtbgQigjZaoQxffkJvq083h3y5lSQpnI56yBE
    |XHtHam8XCPnu7Axj0v5AGGaTYOa4RAzkG8PKpcvL8TRjPL3TMiiKJM2rQVrHdjcK
    |qBSOCr+fSNlr7E5KVBN8pfrsmly+NoflhA7hdQIDAQABAoIBAQCyz2rrlsmfGJsI
    |TyV48MwECV4XYt3IT0YpVFTQzPQRhvKoPmLtbna+0asjdvkVHTOitcevPtG5iwC5
    |id5fDKoMFMIx9OlsS837kz2YnYa/5nYLvJkvdjly0AP6zU0TnYbNTF72NEQZU5q+
    |0UeVqy8AxTfdEcLkJu+sxH4X3kmcQvhz2q7L2pbSgZ0JeL1Nfxmy0cjsSKEVy3qY
    |0tLVm4xHStoYNBpzgXyBqhz/wAhOcctUyl5qvpNzgR+ihASNRKYKIGcpjgjaSryk
    |0Gp8WmwrSuy1qQ8iqKRkSa5SSWqwl1umWlb1V8+7m4ic0A/GJEhzJ5pfXPMaOQuF
    |eHG60JNNAoGBAOyA1R1US5mjoaIZmahR2Rl6nYFQQy3HNqQy1AZU5hB4uTrMA2eW
    |sSxt1RMBjlE9C0sUOFB95w48/gZNI6JPdMFGgcux5WrndDruY8txiVl3rw2Dw7Ih
    |JMxNBsJRO0AZgijUm11HPBp/tJ4HjppZiqE0exjoNFGOLc/l4VOZ1PbDAoGBAMPY
    |j0dS7eHcsmu+v6EpxbRFwSyZG0eV51IiT0DFLfiSpsfmtHdA1ZQeqbVadM1WJSLu
    |ZJ8uvGNRnuLgz2vwKdI6kJFfWYZSS5jfnl874/OF6riNQDseX5CvB5zQvTFVmae+
    |Mld4x2NYFxQ1vIWnGITGQKhcZonBMyAjaQ9tAnNnAoGASvTOFpyX1VryKHEarSk7
    |uIKPFuP8Vq7z13iwkE0qGYBZnJP6ZENzZdRtmrd8hqzlPmdrLb+pkm6sSAz8xT2P
    |kI4rJwb74jT3NpJFmL4kPPHczli7lmJAymuDP+UE9VzgTtaLYzXni7J76TYV8T99
    |23fJp+w4YLzCMkj2cEuqHocCgYBb2KEBMwwqw4TNcOyP2XZFn/0DPF6FyPBuHXcL
    |ii2QCL68ux5hWv+O8n5mdaCXd9H8us5ntNRWw71+6y17kmsak6qe8peandekPyMX
    |yI+T8nbszBmWYB0zTlKEoYRIsbtY5qLXUOY5WeOg776U85NVGWDTVFomOnwOk2y+
    |9kGS+wKBgD3cL/zabIv/kK7KY84EdWdVH4sal3bRsiNn4ezj7go/ObMgR59O4Lr4
    |fYqT1igILotduz/knlkleY2fsqltStWYzRrG+/zNryIBco2+cIX8T120AnpbAvlP
    |gj0YVjuLJXSC9w/URFG+ZGg0kX0Koy1yS6fuxikiA4f5Lw9znjaD
    |-----END RSA PRIVATE KEY-----
    |''')
    file_write('nonsecure.key', nonsecurekey, sudo=True)
    sudo(
        'openssl req -nodes -newkey rsa:2048 -keyout /tmp/nonsecure.key -out '
        '/tmp/server.csr -subj "/C=US/ST=TX/L=Austin/O=STACKOPS '
        'TECHNOLOGIES INC./OU=STACKOPS 360/CN=%s"' % common_name)
    sudo('openssl rsa -in /tmp/nonsecure.key -out /tmp/ssl.key')
    sudo('openssl x509 -req -days 365 -in /tmp/server.csr -signkey '
         '/tmp/ssl.key -out /tmp/ssl.crt')
    sudo('cp /tmp/ssl.crt /etc/ssl/certs/sslcert.crt')
    sudo('cp /tmp/ssl.key /etc/ssl/private/sslcert.key')
