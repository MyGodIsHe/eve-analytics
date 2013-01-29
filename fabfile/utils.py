from fabric.operations import sudo as orig_sudo
from fabric.context_managers import settings
from fabric.contrib.files import upload_template
from fabric.api import env


# fix for sudo_user
def sudo(*args, **kwargs):
    with settings(user=env.sudo_user):
        orig_sudo(*args, **kwargs)

def sudo_upload_template(*args, **kwargs):
    kwargs["use_sudo"] = True
    with settings(user=env.sudo_user):
        upload_template(*args, **kwargs)