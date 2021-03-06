"""
Master/Slave automatic fail over module based on Redis.

Written by Chan Shik Lim. (chanshik@gmail.com)
"""
import os
import sys
import threading
import time
import socket

import redis


class MasterBase(threading.Thread):
    def __init__(self, host='localhost', port=6379, db=0, interval=5):
        threading.Thread.__init__(self)

        self.current_master_id = 0
        self.local_master_id = 0
        self.is_master = False
        self.master_key = ''
        self.master_client_key = ''
        self.app_list_key = ''
        self.unique_id = ''
        self.check_interval = interval
        self.timer = None
        self.do_running = False

        self.program_name = ''
        self.pid = 0
        self.master_callback = None
        self.slave_callback = None

        self.redis = None
        self.redis_host = host
        self.redis_port = port
        self.redis_db = db

    def register(self, program_name, master_callback, slave_callback):
        self.program_name = program_name
        self.unique_id = str(os.getpid()) + '-@' + socket.gethostname()
        self.master_key = 'MASTER:%s:ID' % self.program_name
        self.master_client_key = 'MASTER:%s:MASTER_CLIENT' % self.program_name
        self.app_list_key = 'MASTER:%s:CLIENTS:%s' % (self.program_name, self.unique_id)
        self.pid = os.getpid()
        self.master_callback = master_callback
        self.slave_callback = slave_callback

    def __repr__(self):
        return "%s (%d)" % (self.program_name, self.pid)

    def connect_redis(self):
        try:
            self.redis = redis.StrictRedis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db)
            self.redis.setex(self.app_list_key, self.check_interval * 2, 1)
        except redis.RedisError, e:
            print str(e)

            return False

    def stop(self):
        self.redis = None
        self.do_running = False

    def is_master_alive(self):
        success = self.redis.setnx(self.master_key, self.current_master_id)
        if success:
            self.take_master()

        master_id = int(self.redis.get(self.master_key))
        if self.local_master_id != 0 and master_id == self.local_master_id:
            self.is_master = True
            self.update_master()
        else:
            # Changed status from master to slave.
            if self.is_master is True:
                self.slave_callback()

            self.is_master = False
            self.current_master_id = master_id

        print '[%d] MasterID: %d | LocalID: %d | Master: %s' % (
            os.getpid(),
            master_id,
            self.local_master_id,
            self.is_master
        )

    def take_master(self):
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(self.master_key)

                    cur_master_id = pipe.get(self.master_key)
                    next_master_id = int(cur_master_id) + 1

                    pipe.multi()
                    pipe.setex(
                        self.master_key,
                        self.check_interval * 2,
                        next_master_id)
                    pipe.execute()

                    self.local_master_id = next_master_id
                    self.current_master_id = self.local_master_id
                    self.is_master = True

                    self.master_callback()
                    break
                except redis.WatchError:
                    if self.current_master_id != int(self.redis.get(self.master_key)):
                        self.is_master = False
                        break

    def update_master(self):
        self.redis.setex(
            self.master_key,
            self.check_interval * 2,
            self.local_master_id)

        self.redis.setex(
            self.master_client_key,
            self.check_interval * 2,
            self.unique_id
        )

        self.is_master = True

    def heartbeat(self):
        re_tries = 0
        while re_tries < 4:
            try:
                self.redis.setex(self.app_list_key, self.check_interval * 2, 1)

                break
            except redis.RedisError:
                re_tries += 1
                self.connect_redis()

    def run(self):
        self.do_running = True

        try:
            while self.do_running:
                self.heartbeat()
                self.is_master_alive()

                time.sleep(self.check_interval)
        except RuntimeError, e:
            print str(e)


def got_master():
    print "[%d] Master changed." % os.getpid()


def slave():
    print "[%d] Master released." % os.getpid()


if __name__ == '__main__':
    app = MasterBase()

    app.register('App', got_master, slave)
    if app.connect_redis() is False:
        print "Can't connect to Redis. Exiting."
        sys.exit(1)

    app.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        app.stop()
