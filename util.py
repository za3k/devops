import fabric.api

def put(source, destination, user, **kwargs):
    ret = fabric.api.put(source, destination, use_sudo=True, **kwargs)
    fabric.api.sudo('chown -R {user}:{user} {folder}'.format(user=user, folder=destination + "/" + source.split("/")[-1]))
    return ret
