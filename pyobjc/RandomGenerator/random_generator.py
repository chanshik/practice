import sys
print "\n".join(sys.path)


from Cocoa import *
from Foundation import NSObject
import random
import time


class RandomGeneratorController(NSWindowController):
    numberTextField = objc.IBOutlet()

    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)

        self.number = 0
        self.updateDisplay()

        self.delegate = AppDelegate().alloc().init()

    @objc.IBAction
    def seed_(self, sender):
        NSLog('seed')
        random.seed(time.time())

        self.updateDisplay()

    @objc.IBAction
    def generate_(self, sender):
        NSLog('generate')
        self.number = random.randint(1, 100)

        self.updateDisplay()

    def updateDisplay(self):
        self.numberTextField.setStringValue_(str(self.number))


if __name__ == '__main__':
    app = NSApplication.sharedApplication()

    viewController = RandomGeneratorController.alloc().initWithWindowNibName_('RandomGenerator')
    viewController.showWindow_(viewController)

    NSApp.activateIgnoringOtherApps_(True)

    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()