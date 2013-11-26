"""
Count Characters in Cocoa Programming for MAC OS X book.

Written by Chan Shik Lim. (chanshik@gmail.com)
"""
from Cocoa import *
from Foundation import NSObject
from PyObjCTools import AppHelper


class CountCharacterController(NSWindowController):
    inputTextField = objc.IBOutlet()
    countLabel = objc.IBOutlet()

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
    def count_(self, sender):
        NSLog('count')

        self.updateDisplay()

    def updateDisplay(self):
        NSLog('updateDisplay')

        inputStr = self.inputTextField.stringValue()
        count = len(inputStr)

        if count == 0:
            self.countLabel.setStringValue_("???")
            return

        more_than_one = 's' if count > 1 else ''

        calcStr = "'%s' has %d character%s." % (
            inputStr, count, more_than_one
        )

        self.countLabel.setStringValue_(calcStr)


if __name__ == '__main__':
    app = NSApplication.sharedApplication()

    viewController = CountCharacterController.alloc().initWithWindowNibName_('CountCharacter')
    viewController.showWindow_(viewController)

    NSApp.activateIgnoringOtherApps_(True)

    AppHelper.runEventLoop()