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

