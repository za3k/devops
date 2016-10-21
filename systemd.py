from fabric.api import put, run
def add_unit(path):
    put(path, "/etc/systemd/system")
    run("systemctl daemon-reload")
