import os
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
        if master_id == self.local_master_id:
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
            except redis.WatchError, e:
                self.is_master = False

    def update_master(self):
        self.redis.setex(
            self.master_key,
            self.check_interval * 2,
            self.local_master_id)
        self.is_master = True

    def heartbeat(self):
        self.redis.setex(self.app_list_key, self.check_interval * 2, 1)

    def run(self):
        self.do_running = True

        try:
            while self.do_running:
                self.is_master_alive()
                self.heartbeat()

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
    app.connect_redis()
    app.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        app.stop()
