"""
DotView example.

http://pythonhosted.org/pyobjc/examples/Cocoa/AppKit/DotView/index.html
"""

from Cocoa import *
from PyObjCTools import AppHelper

ZOOM = 2.0


class DotView(NSView):
    colorWell = objc.IBOutlet()
    sizeSlider = objc.IBOutlet()

    def initWithFrame_(self, frame):
        self.center = (50.0, 50.0)
        super(DotView, self).initWithFrame_(frame)
        self.radius = 10.0
        self.color = NSColor.redColor()

        return self

    def awakeFromNib(self):
        self.colorWell.setColor_(self.color)
        self.sizeSlider.setFloatValue_(self.radius)

        scrollView = self.superview().superview()
        scrollView.setHasHorizontalRuler_(1)
        scrollView.setHasVerticalRuler_(1)

    @objc.IBAction
    def zoomIn_(self, sender):
        (x, y), (bw, bh) = self.bounds()
        (x, y), (fw, fh) = self.frame()

        self.setBoundsSize_((bw / ZOOM, bh / ZOOM))
        self.setFrameSize_((fw * ZOOM, fh * ZOOM))
        self.setNeedsDisplay_(True)

    @objc.IBAction
    def zoomOut_(self, sender):
        (x, y), (bw, bh) = self.bounds()
        (x, y), (fw, fh) = self.frame()

        self.setBoundsSize_((bw * ZOOM, bh * ZOOM))
        self.setFrameSize_((fw * ZOOM, fh * ZOOM))
        self.setNeedsDisplay_(True)

    @objc.IBAction
    def setRulersVisible_(self, button):
        scrollView = self.superview().superview()

        scrollView.setRulersVisible_(button.state())

    def isOpaque(self):
        return True

    def mouseDown_(self, event):
        eventLocation = event.locationInWindow()

        if event.modifierFlags() & NSCommandKeyMask:
            clipView = self.superview()

            self.originalPoint = eventLocation
            self.originalOffset = clipView.bounds()[0]
        else:
            self.center = self.convertPoint_fromView_(eventLocation, None)
            self.setNeedsDisplay_(True)
            self.autoscroll_(event)

    def mouseDragged_(self, event):
        if event.modifierFlags() & NSCommandKeyMask:
            clipView = self.superview()
            eventLocation = event.locationInWindow()
            ox, oy = self.originalPoint
            x, y = eventLocation
            dx, dy = x - ox, y - oy
            x, y = self.originalOffset

            clipView.scrollToPoint_((ox, oy))
            clipView.superview().reflectScrolledClipView_(clipView)
        else:
            self.mouseDown_(event)

    def drawRect_(self, rect):
        NSColor.whiteColor().set()
        NSRectFill(self.bounds())
        origin = (self.center[0] - self.radius, self.center[1] - self.radius)
        size = (2 * self.radius, 2 * self.radius)
        dotRect = (origin, size)

        self.color.set()
        NSBezierPath.bezierPathWithOvalInRect_(dotRect).fill()

    @objc.IBAction
    def setRadius_(self, sender):
        self.radius = sender.floatValue()
        self.setNeedsDisplay_(True)

    @objc.IBAction
    def setColor_(self, sender):
        self.color = sender.color()
        self.setNeedsDisplay_(True)


if __name__ == '__main__':
    AppHelper.runEventLoop()