"""
Random number generator in Cocoa Programming for MAC OS X book.

Written by Chan Shik Lim. (chanshik@gmail.com)
"""
import random
import time

from Cocoa import *
from Foundation import NSObject
from PyObjCTools import AppHelper


class RandomGeneratorController(NSWindowController):
    numberTextField = objc.IBOutlet()

    def windowDidLoad(self):
        NSLog('windowDidLoad')
        NSWindowController.windowDidLoad(self)

        self.number = 0
        self.updateDisplay()

    def windowShouldClose_(self, sender):
        NSLog('windowShouldClose')
        return True

    def windowWillClose_(self, notification):
        NSLog('windowWillClose')
        AppHelper.stopEventLoop()

    def applicationShouldTerminateAfterLastWindowClosed_(self, sender):
        NSLog('applicationShouldTerminateAfterLastWindowClosed')
        return True

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
        NSLog('updateDisplay')
        self.numberTextField.setStringValue_(str(self.number))


if __name__ == '__main__':
    app = NSApplication.sharedApplication()

    viewController = RandomGeneratorController.alloc().initWithWindowNibName_('RandomGenerator')
    viewController.showWindow_(viewController)

    NSApp.activateIgnoringOtherApps_(True)

    AppHelper.runEventLoop()