import sys
from threading import Timer
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class TimedEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.notify_func = self.complete_event
        self.timer = None
        self.complete_callback = self.complete_event

    def complete_event(self):
        print "All changes completed."

        self.timer = None

    def on_any_event(self, event):
        print '-' * 60
        print 'event_type: ' + event.event_type
        print 'is_directory: ' + str(event.is_directory)
        print 'src_path: ' + event.src_path

        if self.timer is not None and self.timer.is_alive():
            self.timer.cancel()
            self.timer = None

        self.timer = Timer(5.0, self.complete_callback)
        self.timer.start()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    observer = Observer()
    observer.schedule(TimedEventHandler(), path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
