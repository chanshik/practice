"""
SpeakLine in Cocoa Programming for MAC OS X book.

Written by Chan Shik Lim. (chanshik@gmail.com)
"""
from Cocoa import *
from Foundation import NSObject
from PyObjCTools import AppHelper
from AppKit import NSSpeechSynthesizer


class SpeakLineController(NSWindowController):
    speakTextField = objc.IBOutlet()
    speakButton = objc.IBOutlet()
    stopButton = objc.IBOutlet()
    speakStr = ''

    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)
        NSLog('windowDidLoad')

        self.voice = NSSpeechSynthesizer.defaultVoice()
        self.speech = NSSpeechSynthesizer.alloc().initWithVoice_(self.voice)

        self.window().makeFirstResponder_(self.speakTextField)

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
    def sayIt_(self, sender):
        NSLog('sayIt')

        self.speakStr = self.speakTextField.stringValue()

        if len(self.speakStr) == 0:
            return

        NSLog('Speak: ' + self.speakStr)
        self.speech.startSpeakingString_(self.speakStr)

    @objc.IBAction
    def stop_(self, sender):
        NSLog('stop')

        self.speech.stopSpeaking()


if __name__ == '__main__':
    app = NSApplication.sharedApplication()

    viewController = SpeakLineController.alloc().initWithWindowNibName_('SpeakLine')
    viewController.showWindow_(viewController)

    NSApp.activateIgnoringOtherApps_(True)

    AppHelper.runEventLoop()