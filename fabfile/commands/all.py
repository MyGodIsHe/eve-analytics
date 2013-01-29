# Fabric deployment script

from operator import methodcaller
from fabric.context_managers import prefix

from fabric.api import run, cd, env
from fabric.utils import fastprint
from fabric.contrib.files import exists, upload_template

from fabfile.settings import *
from fabfile.utils import *



def deploy_head(*args):
    cmd = 'git ls-remote %s | head -n 1 | cut -f 1,1' % GIT_REPO
    # because `run` will return the _full_ i/o log
    # including the password prompt
    revision = run(cmd).strip().split('\n')[-1]

    deploy(revision, *args)


def deploy(revision, *args):
    default_options = [
        'db',
        'deps',
        'all',
        ]

    if not args:
        fastprint("Options: %s or none (fab deploy:)" % ','.join(default_options))
        return

    if len(args) == 1 and not args[0]:
        options = []
    else:
        options = map(methodcaller('lower'), args)
        if 'all' in options:
            options = default_options

    abs_path = posixpath.join(ROOT_DIR, REV_DIR, revision)

    if not exists(abs_path):
        install_repo(abs_path)
    else:
        update_repo(abs_path)

    if 'deps' in options:
        update_deps(abs_path)

    prod_config(abs_path)
    collect_static(abs_path)

    if 'db' in options:
        sync_db(abs_path)
        migrate_db(abs_path)

    # What is better, migrate DB before or after dir change?
    update_link(abs_path)


def update_link(path):
    run('ln -Tfs %s %s' % (path, APP_DIR))


def prod_config(path):
    prod = posixpath.join(path, FABFILE_DIR, 'production_settings.py')
    orig = posixpath.join(path, 'eve', 'settings', 'local.py')
    run('cp -f %s %s' % (prod, orig))


def collect_static(path):
    if not exists(PUBLIC_DIR):
        run('mkdir %s' % PUBLIC_DIR)
    run('ln -Tfs %s %s' % (PUBLIC_DIR, posixpath.join(path, 'public')))

    with cd(path):
        with prefix(env.activate):
            run('python manage.py collectstatic --noinput')


### DB stuff
def migrate_db(path):
    with cd(path):
        with prefix(env.activate):
            run('python manage.py migrate')


def sync_db(path):
    with cd(path):
        with prefix(env.activate):
            run('python manage.py syncdb --noinput')


### Dependencies:
def update_deps(path):
    if not exists(VENV_DIR):
        run("virtualenv %s --system-site-packages" % VENV_DIR)
    with cd(path):
        with prefix(env.activate):
            run('pip install -r requirements.txt')


### Git stuff
def update_repo(path):
    with cd(path):
        run('git pull')
        run('git submodule update')


def install_repo(dest):
    run('git clone %s %s' % (GIT_REPO, dest))

    with cd(dest):
        run('git submodule init')
        run('git submodule update')


def start_all():
    service_redis()
    service_nginx()
    service_supervisor()

def install_system_tools():
    sudo('apt-get install gcc make git python-setuptools python-dev libzmq-dev g++ libevent-dev')
    sudo('easy_install pip')
    sudo('pip install virtualenv')


def install_nginx():
    """
    Nginx step 1
    """
    sudo('apt-get install nginx')

def configure_nginx():
    """
    Nginx step 2
    """
    conf_locate = '/etc/nginx/conf.d/eve.conf'
    sudo_upload_template("%s%s" % (FABFILE_DIR, conf_locate), conf_locate, dict(
        server_name=APP_DOMAIN,
        public_dir=PUBLIC_DIR,
        port=APP_PORT,
    ))

    conf_locate = '/etc/nginx/conf.d/sentry.conf'
    sudo_upload_template("%s%s" % (FABFILE_DIR, conf_locate), conf_locate, dict(
        server_name=SENTRY_DOMAIN,
        port=SENTRY_PORT,
        sentry_path='/home/eve/venv/local/lib/python2.7/site-packages/sentry',
    ))

def service_nginx(action='start'):
    """
    Nginx step 3
    """
    sudo('service nginx %s' % action)


def install_redis(version='2.4.13'):
    """
    Redis step 1
    """
    sudo('apt-get install redis-server')

def service_redis(action='start'):
    """
    Redis step 4
    """
    sudo('service redis-server %s' % action)


def configure_sentry(email_user, email_password):
    """
    Sentry run after django
    """
    if not exists(SENTRY_DIR):
        run('mkdir %s' % SENTRY_DIR)
    conf_name = 'sentry.conf.py'
    upload_template(
        "%s/%s.tpl" % (FABFILE_DIR, conf_name),
        posixpath.join(SENTRY_DIR, conf_name), dict(
            email_user=email_user,
            email_password=email_password,
            domain=SENTRY_DOMAIN,
            port=SENTRY_PORT,
        ))
    with prefix(env.activate):
        run('sentry upgrade')



def getssetting(name):
    """
    Get remote setting from django.conf.settings
    """
    return run('python -W ignore::DeprecationWarning ./manage.py getsetting %s' % name)


def install_supervisor():
    """
    Supervisor step 1
    """
    sudo('apt-get install supervisor')

def configure_supervisor():
    """
    Supervisor step 2
    """
    conf_locate = '/etc/supervisor/conf.d/eve.conf'
    sudo_upload_template("%s%s" % (FABFILE_DIR, conf_locate), conf_locate, dict(
        app_dir=APP_DIR,
        venv=VENV_DIR,
        user=APP_USER,
        sentry_dir=SENTRY_DIR,
        log=LOG_DIR,
        port=APP_PORT,
    ))

def service_supervisor(action='start'):
    """
    Supervisor step 3
    """
    sudo('service supervisor %s' % action)

def status_supervisor():
    """
    Supervisor extend
    """
    sudo('supervisorctl status')


def manage_supervisor(program, action):
    sudo('supervisorctl %s eve:%s' % (action, program))


def install_mysql():
    """
    Supervisor step 1
    """
    sudo('apt-get install mysql-server libmysqlclient-dev')

def configure_mysql():
    """
    Supervisor step 2
    """
    run("mysql -u root -e 'CREATE DATABASE eve CHARACTER SET utf8'")
    run("mysql -u root -e 'CREATE DATABASE sentry CHARACTER SET utf8'")


def first_deploy():
    run('mkdir %s'%  LOG_DIR)

def fill_empty():
    """
    Fill empty names in db
    """
    with cd(APP_DIR):
        with prefix(env.activate):
            run('./manage.py fill_empty')