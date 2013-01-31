from fabfile.settings import *
from fabric.api import env

env.activate = 'source %s' % posixpath.join(VENV_DIR, 'bin/activate')
env.orig_user = env.user
env.user = APP_USER
env.use_ssh_config = True
if not env.host_string:
    env.host_string = '176.9.220.203'

from fabfile.commands import *