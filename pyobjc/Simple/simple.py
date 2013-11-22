"""
Very Simple OS X Cocoa Application using Python and Interface Builder

http://blog.adamw523.com/os-x-cocoa-application-python-pyobjc/

"""
from Cocoa import *
from Foundation import NSObject


class SimpleXibDemoController(NSWindowController):
    counterTextField = objc.IBOutlet()

    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)

        self.count = 0

    @objc.IBAction
    def increment_(self, sender):
        self.count += 1
        self.updateDisplay()

    @objc.IBAction
    def decrement_(self, sender):
        self.count -= 1
        self.updateDisplay()

    def updateDisplay(self):
        self.counterTextField.setStringValue_(self.count)


if __name__ == '__main__':
    app = NSApplication.sharedApplication()

    viewController = SimpleXibDemoController.alloc().initWithWindowNibName_('SimpleXibDemo')
    viewController.showWindow_(viewController)

    NSApp.activateIgnoringOtherApps_(True)

    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()