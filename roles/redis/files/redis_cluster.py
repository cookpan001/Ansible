#! /usr/bin/python

# find $REDIS_HOME/src/ -perm 755 | xargs -i cp {} $REDIS_HOME/bin/

__author__ = "cookpan001"
__date__ = "$2015-6-12 14:36:11$"

import sys
import os
import re
import string
import ConfigParser
class StartRedis(object):
    def __init__(self, filename):
        self.parser = ConfigParser.ConfigParser()
        self.parser.read(filename)
	ifconfig = os.popen('ifconfig').readlines()
	self.ips = []
	for line in ifconfig:
	    line = line.strip()
	    m = re.match(r"inet\s*[a-zA-Z]*[:]*(\d+\.\d+\.\d+\.\d+)", line)
	    if m:
		self.ips.append(m.group(1))
    def stop(self):
	sections = self.parser.sections()
        for name in sections:
	    host = self.parser.get(name, 'bind')
	    try:
		self.ips.index(host)
	    except:
		print "skip " + host
		continue
            port = self.parser.get(name, 'port')
	    cmd = "$REDIS_HOME/bin/redis-cli -h " + host + " -p " + port + " shutdown nosave"
	    os.system(cmd)
    def create(self):
	sections = self.parser.sections()
	cmd = "$REDIS_HOME/bin/redis-trib.rb create --replicas 1 "
	data = {}
        for section in sections:
	    index = string.find(section, "_")
            if index > -1:
                name = section[0:index]
		host = self.parser.get(section, 'bind')
		port = self.parser.get(section, 'port')
		if not data.has_key(name):
		    data[name] = ""
		data[name] += " " + host + ":" + port
	for subcmd in data:
	    print cmd + data[subcmd]
	    os.system(cmd + data[subcmd])
    def start(self):
        sections = self.parser.sections()
	if len(sys.argv) > 3:
	    self.dataPath = "/data/" + sys.argv[3] + "/"
	else:
	    self.dataPath = "/data/"
        for name in sections:
	    host = self.parser.get(name, 'bind')
	    try:
		self.ips.index(host)
	    except:
		print "skip " + host
		continue
            cmd = "$REDIS_HOME/bin/redis-server $REDIS_HOME/redis.conf --daemonize yes --dbfilename " + name + ".rdb --dir /data/" + name + " --pidfile /var/run/redis-" + name + ".pid"
	    if not os.path.exists(self.dataPath + name):
		os.mkdir(self.dataPath + name)
            for key, value in self.parser.items(name):
                if key == 'alias':
                    continue
                cmd += " --" + key + " " + value
            os.system(cmd)
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        filename = "$REDIS_HOME/ini/redis_list.cfg"
	print "Usage: " + sys.argv[0] + " <file_path> [start [groupname]|create]\n" ;
	exit(1)
    filename = sys.argv[1]
    cmd = sys.argv[2]
    app = StartRedis(filename)
    if hasattr(app, cmd):
        result = getattr(app, cmd)()
    else:
	print "Unknown command.\n"
