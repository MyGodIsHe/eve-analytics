import posixpath

APP_DOMAIN = 'eve.megail.ru'
GIT_REPO = 'git@bitbucket.org:ichistyakov/eve-analytics.git'
APP_NAME = 'www'
APP_USER = 'eve'
REV_DIR  = 'revisions'
ROOT_DIR = '/home/%s/' % APP_USER
APP_DIR  = posixpath.join(ROOT_DIR, APP_NAME)
APP_PORT = 8001
PUBLIC_DIR = posixpath.join(ROOT_DIR, 'public')
SENTRY_DIR  = posixpath.join(ROOT_DIR, '.sentry')
LOG_DIR  = posixpath.join(ROOT_DIR, 'log')
FABFILE_DIR = 'fabfile'
FABFILE_ABS_DIR = posixpath.join(APP_DIR, FABFILE_DIR)
VENV_DIR  = posixpath.join(ROOT_DIR, 'venv')

SENTRY_DOMAIN = 'sentry.megail.ru'
SENTRY_PORT = 9000