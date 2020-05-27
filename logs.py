import util

def setup(c):
    # Set up logging
    util.put_file(c, "config/forever-log/log", "/bin/log", mode="0755", user="root")
    util.put_file(c, "config/forever-log/watchdog", "/etc/cron.daily/watchdog", mode="0755", user="root")
    util.make_dir(c, "/var/log/forever", mode='1777', owner='root') # make sure anyone can add a site
