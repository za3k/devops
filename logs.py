import util
from cuisine import dir_ensure, mode_sudo

def setup():
    # Set up logging
    util.put("config/forever-log/log", "/bin/log", mode="0755", user="root")
    with mode_sudo():
        dir_ensure("/var/log/forever", mode='1777') # make sure anyone can add a site
