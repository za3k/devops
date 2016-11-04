from fabric.api import run, settings, sudo

def has(name, user=None):
    with settings(warn_only=True):
        if user is None:
            return bool(run("which {name}".format(name=name)))
        else:
            return bool(sudo("which {name}".format(name=name), user=user))
