apt-get install python-dev libffi-dev libfontconfig nodejs
sudo ln -s /usr/bin/nodesjs /usr/bin/node
useradd graphite
useradd -m statsd

statsd
    install: git clone https://github.com/etsy/statsd
             apt-get install node-generic-pool # Needed for 'repeater' backend

    files: /etc/statsd/config.js
           /etc/systemd/system/statsd.service

    user: statsd [configured]
    systemd: statsd.service

    ports: 8125 (UDP) - statsd protocol
           8126 (TCP) - admin

    data: none (stateless)

    debugging: http://blog.backslasher.net/troubleshooting-statsd.html
        note: IPv6 is OFF by default. which is dumb.
        input data: echo "test1:1|c" | nc -u -w0 localhost 8125
        check data: turn on backend 'console' in config, you will see things in the console
                    echo "stats" | nc localhost 8126

carbon-cache
    install: pip install carbon whisper
             # Install locations are WRONG on debian
             sudo cp -rv /usr/local/lib/python2.7/dist-packages/opt/graphite/lib/carbon /usr/local/bin/ && sudo cp -rv /usr/local/lib/python2.7/dist-packages/opt/graphite/lib/twisted /usr/local/bin/
             mkdir /usr/local/storage && chown graphite:graphite /usr/local/storage

    files: # May be in /opt/graphite/carbon on other systems
           /etc/carbon/carbon.conf
           /etc/carbon/storage-schemes.conf
           /etc/carbon/storage-aggregation.conf
           /etc/systemd/system/carbon-cache.service

    user: graphite [configured]
    systemd: carbon-cache.service

    data: /usr/local/storage/whisper
    ports: 2003 (TCP) - line input
           2004 (TCP) - pickle input
           7002 (TCP) - "cache query"
           2013 (TCP) - line input relay [off]
           2014 (TCP) - pickle input relay [off]
           2023 (TCP) - line input aggregator [off]
           2024 (TCP) - pickle input aggregator [off]

    debugging (somewhat): http://blog.backslasher.net/troubleshooting-statsd.html
        input data: echo "test.back.slash 4 `date +%s`" | nc -4 -q0 localhost 2003
        check data: check the contents of /opt/graphite/storage/whisper/test/back/. do you see a slash.wsp file? if so data is getting in

graphite(-API)
    install: pip install graphite-api
             sytemctl enable graphite-api

    files: /etc/graphite-api.yaml
           /etc/systemd/system/graphite-api.socket
           /etc/systemd/system/graphite-api.service

    user: graphite [configured]
    systemd: graphite-api.service

    data: /etc/local/storage/whisper
          /etc/local/storage/index

    port: 8087 (TCP) - web [configured]

    nginx+gunicorn install: http://graphite-api.readthedocs.io/en/latest/deployment.html#gunicorn-nginx
        pip install gunicorn
        systemd setup
        nginx setup

grafana
    install: sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
             curl https://packages.grafana.com/gpg.key | sudo apt-key add -
             systemctl daemon-reload
             systemctl enable grafana-server

    files: /etc/defaults/grafana-server
           /etc/grafana/grafana.ini
    systemd: grafana-server.service

    data: /var/lib/grafana.db

    port: 3000 (TCP) - web [configured]
