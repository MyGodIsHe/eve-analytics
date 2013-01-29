from fabric.api import run
from fabfile.utils import *


def percona_install(ubuntu_version):
    """
    Percona step 1

    http://www.percona.com/doc/percona-server/5.5/installation/apt_repo.html
    """
    sudo('gpg --keyserver  hkp://keys.gnupg.net --recv-keys 1C4CBDCDCD2EFD2A; gpg -a --export CD2EFD2A | sudo apt-key add -')
    for postfix in ['', '-src']:
        sudo('echo "deb%s http://repo.percona.com/apt %s main" >> sudo /etc/apt/sources.list' % (postfix, ubuntu_version))
    sudo('apt-get update')
    sudo('apt-get install percona-server-server percona-server-client')

def percona_set_engine(db, *tables):
    """
    Supervisor step 2
    """
    for table in tables:
        run("mysql -u root -e 'ALTER TABLE %s ENGINE=xtradb;' %s" % (table, db))