import wx
import wx.lib.ogl as ogl
from primitives import *
#----------------------------------------------------------------------

class DrawingBoard(ogl.ShapeCanvas):
    def __init__(self, parent, log, frame):
        ogl.ShapeCanvas.__init__(self, parent)

        self.width  = 1500
        self.height = 1500
        self.SetScrollbars(20, 20, self.width/20, self.height/20)

        self.log = log
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE") #wx.WHITE)
        self.diagram = ogl.Diagram()
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)
        self.shapes = []
        self.save_gdi = []

        rRectBrush = wx.Brush("MEDIUM TURQUOISE", wx.SOLID)
        dsBrush = wx.Brush("WHEAT", wx.SOLID)

        # self.MyAddShape(
        #     Transition(80), 
        #     100, 100, wx.Pen(wx.BLUE, 2), wx.GREEN_BRUSH, "Transition"
        #     )
            
        # self.MyAddShape(
        #     ogl.RectangleShape(85, 50), 
        #     305, 60, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, "Place"
        #     )

        # Might need this later, for popping stuff
        #ds = self.MyAddShape(
        #             DividedShape(140, 150, self), 
        #             495, 145, wx.BLACK_PEN, dsBrush, ''
        #             )

        # self.MyAddShape(
        #     DiamondShape(90, 90), 
        #     345, 235, wx.Pen(wx.BLUE, 3, wx.DOT), wx.RED_BRUSH, "Polygon"
        #     )
        #     
        #self.MyAddShape(
        #     Place(95,70), 
        #     140, 255, wx.Pen(wx.RED, 2), rRectBrush, "Place"
        #     )

        # bmp = images.getNewBitmap()
        # mask = wx.MaskColour(bmp, wx.BLUE)
        # bmp.SetMask(mask)

        # s = ogl.BitmapShape()
        # s.SetBitmap(bmp)
        # self.MyAddShape(s, 225, 150, None, None, "Bitmap")

        self.dc = wx.ClientDC(self)
        self.PrepareDC(self.dc)

        # for x in range(len(self.shapes)):
        #     fromShape = self.shapes[x]
        #     if x+1 == len(self.shapes):
        #         toShape = self.shapes[0]
        #     else:
        #         toShape = self.shapes[x+1]

        #     line = ogl.LineShape()
        #     line.SetCanvas(self)
        #     line.SetPen(wx.BLACK_PEN)
        #     line.SetBrush(wx.BLACK_BRUSH)
        #     line.AddArrow(ogl.ARROW_ARROW)
        #     line.MakeLineControlPoints(2)
        #     fromShape.AddLine(line, toShape)
        #     self.diagram.AddShape(line)
        #     line.Show(True)

        #     # for some reason, the shapes have to be moved for the line to show up...
        #     fromShape.Move(self.dc, fromShape.GetX(), fromShape.GetY())

        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)


    def MyAddShape(self, shape, x, y, pen, brush, text):
        shape.SetDraggable(True, True)
        shape.SetCanvas(self)
        shape.SetX(x)
        shape.SetY(y)
        if pen:    shape.SetPen(pen)
        if brush:  shape.SetBrush(brush)
        if text:   shape.AddText(text)
        # shape.SetShadowMode(ogl.SHADOW_RIGHT)
        self.diagram.AddShape(shape)
        shape.Show(True)

        evthandler = MyEvtHandler(self, self.diagram, self.dc, self.log, self.frame)
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        self.shapes.append(shape)
        return shape


    def OnDestroy(self, evt):
        # Do some cleanup
        for shape in self.diagram.GetShapeList():
            if shape.GetParent() == None:
                shape.SetCanvas(None)
                shape.Destroy()

        self.diagram.Destroy()


    def OnBeginDragLeft(self, x, y, keys):
        self.log.write("OnBeginDragLeft: %s, %s, %s\n" % (x, y, keys))

    def OnEndDragLeft(self, x, y, keys):
        self.log.write("OnEndDragLeft: %s, %s, %s\n" % (x, y, keys))
	self.Adjust()
	
 
    def Adjust(self):
        self.Refresh()
        self.Refresh(False, wx.Rect(self.width, self.height))

    def fix(self):
        self.SetBackgroundColour("LIGHT BLUE")
