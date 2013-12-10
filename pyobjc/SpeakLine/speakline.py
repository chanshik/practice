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
    tableView = objc.IBOutlet()
    speakStr = ''

    def awakeFromNib(self):
        NSLog('awakeFromNib')
        self.voice = NSSpeechSynthesizer.defaultVoice()
        self.speech = NSSpeechSynthesizer.alloc().initWithVoice_(self.voice)
        self.voiceFullnames = NSSpeechSynthesizer.availableVoices()
        self.voices = [name[name.rindex('.') + 1:] for name in self.voiceFullnames]

    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)
        NSLog('windowDidLoad')

        self.speech.setDelegate_(self)

        self.window().makeFirstResponder_(self.speakTextField)
        self.speakButton.setEnabled_(True)
        self.stopButton.setEnabled_(False)

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

        self.speakButton.setEnabled_(False)
        self.stopButton.setEnabled_(True)
        self.tableView.setEnabled_(False)

        self.speakStr = self.speakTextField.stringValue()

        if len(self.speakStr) == 0:
            return

        NSLog('Speak: ' + self.speakStr)
        self.speech.startSpeakingString_(self.speakStr)

    @objc.IBAction
    def stop_(self, sender):
        NSLog('stop')

        self.speech.stopSpeaking()

        self.speakButton.setEnabled_(True)
        self.stopButton.setEnabled_(False)
        self.tableView.setEnabled_(False)

    def speechSynthesizer_didFinishSpeaking_(self, sender, finishedSpeaking):
        NSLog('didFinishSpeaking_')

        self.speakButton.setEnabled_(True)
        self.stopButton.setEnabled_(False)
        self.tableView.setEnabled_(True)

    # data source methods
    def numberOfRowsInTableView_(self, aTableView):
        return len(self.voices)

    def tableView_objectValueForTableColumn_row_(
            self, aTableView, aTableColumn, rowIndex):

        return self.voices[rowIndex]

    #def tableView_setObjectValue_forTableColumn_row_(
    #        self, aTableView, anObject, aTableColumn, rowIndex):
    #    pass

    # delegate methods
    def tableView_shouldSelectRow_(self, aTableView, rowIndex):
        return True

    def tableView_shouldEditTableColumn_row_(self, aTableView, aTableColumn, rowIndex):
        return False

    def tableViewSelectionDidChange_(self, notification):
        row = self.tableView.selectedRow()

        self.speech.setVoice_(self.voiceFullnames[row])

        NSLog('Selected: ' + str(row))

if __name__ == '__main__':
    app = NSApplication.sharedApplication()

    viewController = SpeakLineController.alloc().initWithWindowNibName_('SpeakLine')
    viewController.showWindow_(viewController)

    NSApp.activateIgnoringOtherApps_(True)

    AppHelper.runEventLoop()