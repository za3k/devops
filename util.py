import fabric.api

def put_file(source, destination, user, mode):
    ret = fabric.api.put(source, destination, use_sudo=True, mode=mode)
    fabric.api.sudo('[ -f {file} ] && chown {user}:{user} {file}'.format(user=user, file=destination))
    return ret

def put_dir(source, destination, user, mode):
    ret = fabric.api.put(source, destination, use_sudo=True, mode=mode)
    fabric.api.sudo('[ -d {folder} ] && chown -R {user}:{user} {folder}'.format(user=user, folder=destination))
    return ret

def make_dir(directory, user, mode):
    return fabric.api.sudo('mkdir "{directory}"; chown {user}:{user} "{directory}" && chmod {mode} "{directory}"'.format(user=user, directory=directory, mode=mode))
