import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler


class FileNotifier(FileSystemEventHandler):
    def on_any_event(self, event):
        print 'event_type: ' + event.event_type
        print 'is_directory: ' + str(event.is_directory)
        print 'src_path: ' + event.src_path

    def on_created(self, event):
        print 'FileNotifier::on_created ' + str(event)


if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO,
    #                    format='%(asctime)s - %(message)s',
    #                    datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    #event_handler = LoggingEventHandler()

    observer = Observer()
    observer.schedule(FileNotifier(), path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
