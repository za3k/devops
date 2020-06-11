import util

def setup():
    # Set up logging
    util.put_file("config/forever-log/log", "/bin/log", mode="0755", user="root")
    util.put_file("config/forever-log/watchdog", "/etc/cron.daily/watchdog", mode="0755", user="root")
    util.make_dir("/var/log/forever", mode='1777', user='root') # make sure anyone can add a site
