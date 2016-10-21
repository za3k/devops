from cuisine import dir_ensure, group_ensure, group_user_ensure, package_ensure, select_package, user_ensure
import systemd, util
from fabric.api import run
def ensure():
    select_package("apt")
    package_ensure(["znc"]) # On debian will automatically be enabled

    user_ensure('znc')
    group_ensure('znc')
    group_user_ensure('znc', 'znc')
    dir_ensure("/var/znc", mode='755')
    dir_ensure("/var/znc/configs", mode='755')
    run("chown znc:znc /var/znc")
    util.put("/srv/znc.conf", "/var/znc/configs", user="znc", mode="600")
    util.put("config/keys/znc.pem", "/var/znc", user="znc", mode="600")
    util.put("config/znc/modules", "/var/znc", user="znc", mode="755")
    run("cp /var/znc/modules/*.so /usr/lib/znc")
    systemd.add_unit("config/systemd/znc.service")
    run("systemctl enable znc")
    run("systemctl restart znc")
