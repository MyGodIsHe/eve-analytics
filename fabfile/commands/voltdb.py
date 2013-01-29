from operator import methodcaller
from fabric.context_managers import prefix, settings

from fabric.api import run, cd, env
from fabric.utils import fastprint
from fabric.contrib.files import exists, upload_template

from fabfile.settings import *
from fabfile.utils import *

DB_NAME = 'eve'


def voltdb_install():
    """
    VoltDB step 1
    """
    with cd('/tmp'):
        file_name = 'voltdb_3.0-1_amd64.deb'
        run('wget http://voltdb.com/downloads/technologies/server/%s' % file_name)
        sudo('dpkg -i %s' % file_name)
        run('rm %s' % file_name)

def voltdb_configure():
    """
    VoltDB step 2
    """
    run('voltdb compile --classpath="./"l -o %(db)s.jar %(db)s.sql' % {'db':DB_NAME})

def voltdb_run():
    """
    VoltDB step 3
    """
    run("""voltdb create \
          catalog %s.jar   \
          deployment deployment.xml   \
          host localhost""" % DB_NAME)