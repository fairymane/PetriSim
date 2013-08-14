import wx
import wx.lib.ogl as ogl
#import shlex,subprocess
import GUI

ID_DELETE_PRIMITIVE = wx.NewId()
#ID_EDIT_TOKEN       = wx.NewId()
#ID_SUPER_TRANSITION = wx.NewId()
ID_NEW_WINDOW 	    = wx.NewId()
ID_CHANGE_NAME      = wx.NewId()

#----------------------------------------------------------------------
class Transition(ogl.RectangleShape):
    def __init__(self, w=0.0, h=0.0, name="", t_type= None):
        ogl.RectangleShape.__init__(self, w, h)
        self.SetCornerRadius(-0.2)
        self.name            = name
	self.type = t_type
        #self.outputs         = []
        #self.SuperTransition = False
        #self.SuperStart      = None
        #self.SuperEnd        = None

#----------------------------------------------------------------------

class Place(ogl.CircleShape):
    def __init__(self, radius,name=None):
        ogl.CircleShape.__init__(self, radius)
        self.name        = name
        #self.outputs     = []
        #self.NumTokens   = 0

#----------------------------------------------------------------------

class Arrow(ogl.LineShape):
    def __init__(self,name=" "):
        ogl.LineShape.__init__(self)
        self.name        = name
        #self.outputs     = []
       

#----------------------------------------------------------------------
#Add on 3/5/13, to simulate the draggable line
#class Polygon(ogl.PolygonShape):
#    def __init__(self, name = ""):
 #       ogl.PolygonShape.__init__(self)
        #self.name        = name
  #      self.outputs     = []

class Diamond(ogl.PolygonShape):
    def __init__(self, w=0.0, h=0.0,  name = ""):
        ogl.PolygonShape.__init__(self)
	self.name = name
        if w == 0.0:
            w = 240.0
        if h == 0.0:
            h = 30.0
        #self.outputs     = []
	self.name        = name
        points = [ (0.0,    -h/2.0),
                   (w/2.0,  0.0),
                   (0.0,    h/2.0),
                   (-w/2.0, 0.0),
                   ]
  
        self.Create(points)

#----------------------------------------------------------------------
class DividedShape(ogl.DividedShape):
    def __init__(self, width, height, canvas):
        ogl.DividedShape.__init__(self, width, height)

        region1 = ogl.ShapeRegion()
        region1.SetText('DividedShape')
        region1.SetProportions(0.0, 0.2)
        region1.SetFormatMode(ogl.FORMAT_CENTRE_HORIZ)
        self.AddRegion(region1)

        region2 = ogl.ShapeRegion()
        region2.SetText('This is Region number two.')
        region2.SetProportions(0.0, 0.3)
        region2.SetFormatMode(ogl.FORMAT_CENTRE_HORIZ|ogl.FORMAT_CENTRE_VERT)
        self.AddRegion(region2)

        region3 = ogl.ShapeRegion()
        region3.SetText('Region 3\nwith embedded\nline breaks')
        region3.SetProportions(0.0, 0.5)
        region3.SetFormatMode(ogl.FORMAT_NONE)
        self.AddRegion(region3)

        self.SetRegionSizes()
        self.ReformatRegions(canvas)


    def ReformatRegions(self, canvas=None):
        rnum = 0

        if canvas is None:
            canvas = self.GetCanvas()

        dc = wx.ClientDC(canvas)  # used for measuring

        for region in self.GetRegions():
            text = region.GetText()
            self.FormatText(dc, text, rnum)
            rnum += 1


    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        self.base_OnSizingEndDragLeft(pt, x, y, keys, attch)
        self.SetRegionSizes()
        self.ReformatRegions()
        self.GetCanvas().Refresh()

#---------------------------------------------------
class SubPetriNet(wx.App):
    def __init__(self, name, binary):
    #def OnInit(self, name, binary):
	
	self._name= name
	self.inname = self._name+'-in'
	self.outname = self._name+'-out'
	self._binary = int(binary)
        self.frame = GUI.MyFrame(None, -1, "PetriSim!")
	self.frame.tlist[self.inname] = str(self._binary)
	self.frame.tlist[self.outname] = str(self._binary)
        shape1 = Transition(60, 30, self.inname, self._binary)
	shape2 = Transition(60, 30, self.outname, self._binary)
	if self._binary == 0:
	    brush = wx.Brush("AQUAMARINE", wx.SOLID)
	if self._binary == 1:
	    brush = wx.Brush("GREEN YELLOW", wx.SOLID)	
        self.frame.CurrentArea.MyAddShape(shape1,
            510, 30, wx.Pen(wx.BLUE, 1), brush, self.inname )

        self.frame.CurrentArea.MyAddShape(shape2,
            510, 480, wx.Pen(wx.BLUE, 1), brush, self.outname )

        self.frame.Show(True)
        #self.SetTopWindow(self.frame)
        

#----------------------------------------------------------------------

class MyEvtHandler(ogl.ShapeEvtHandler):
    def __init__(self, parent, diagram, dc, log, frame):
        ogl.ShapeEvtHandler.__init__(self)
        self.log          = log
        self.statbarFrame = frame
        self.base         = frame 				# This refers to our base frame
        self.canvas = parent
        self.diagram = diagram
        self.dc = dc
        #self.canvas = parent

    def UpdateStatusBar(self, shape):
        x,y = shape.GetX(), shape.GetY()
        width, height = shape.GetBoundingBoxMax()
        # self.statbarFrame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d)" %
        #                               (x, y, width, height))
        self.statbarFrame.SetStatusText("Press the \"Exit\" button to exit Design mode")


    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
    	print 'ano'
        shape = self.GetShape()

	
        #print 'shape:', shape.__class__, shape.GetClassName()
        canvas = shape.GetCanvas()
        print 'aha'
        shape.GetCanvas().Refresh()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)

        if shape.Selected():
            shape.Select(False, dc)
            canvas.Redraw(dc)
        else:
            redraw = False
            shapeList = canvas.GetDiagram().GetShapeList()
            toUnselect = []

            for s in shapeList:
                if s.Selected():
                    # If we unselect it now then some of the objects in
                    # shapeList will become invalid (the control points are
                    # shapes too!) and bad things will happen...
                    toUnselect.append(s)

            shape.Select(True, dc)

            if toUnselect:
                for s in toUnselect:
                    s.Select(False, dc)

                canvas.Redraw(dc)

        self.UpdateStatusBar(shape)


    #def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
     #   shape = self.GetShape()
      #  self.base_OnEndDragLeft(x, y, keys, attachment)

        #if not shape.Selected():
        #    self.OnLeftClick(x, y, keys, attachment)

        self.UpdateStatusBar(shape)
        self.canvas.Adjust()

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        self.base_OnSizingEndDragLeft(pt, x, y, keys, attch)
        self.UpdateStatusBar(self.GetShape())
	self.canvas.Adjust()


    #def OnMovePost(self, dc, x, y, oldX, oldY, display):
        #self.base_OnMovePost(dc, x, y, oldX, oldY, display)
        #self.UpdateStatusBar(self.GetShape())

    def OnRightClick(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        ##print shape.__class__, shape.GetClassName()
        canvas = shape.GetCanvas()
        shape.GetCanvas().Refresh()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)

        # This part takes care of the arrow making
        # ------------------------------------------------------------
        if self.base.mode == "design arrow":

           if self.base.selected:
	       #print 'from', self.base.selected.name	
               if (isinstance(self.base.selected, Place) and isinstance(shape, Transition)) or \
                  (isinstance(self.base.selected, Transition) and isinstance(shape, Place)) or \
		  (isinstance(self.base.selected, Place) and isinstance(shape, Diamond))	or \
		  (isinstance(self.base.selected, Transition) and isinstance(shape, Diamond))  or \
		  (isinstance(self.base.selected, Diamond) and isinstance(shape,Place ))	or \
		  (isinstance(self.base.selected, Diamond) and isinstance(shape, Transition)) :

		   dlg = wx.TextEntryDialog(None, 'Please provide a weight for the arrow:')
        	   if dlg.ShowModal() == wx.ID_OK:
            	       weight = dlg.GetValue()
		       weight.replace(" ", "")
		 
			
		   dlg.Destroy()
		   if (isinstance(self.base.selected, Place) and isinstance(shape, Transition)):
		       #self.base._places[self.base.selected.name]  = [shape.name, weight]
		       if self.base._places.has_key(str(self.base.selected.name)):
		           self.base._places[str(self.base.selected.name)][str(shape.name)] = int(weight)
			   if not self.base._transitions.has_key (str(shape.name)):
			       self.base._transitions[str(shape.name)] = dict()
		       else:
			   self.base._places[str(self.base.selected.name)] = dict() 	
			   self.base._places[str(self.base.selected.name)][str(shape.name)] = int(weight)
			   if not self.base._transitions.has_key (str(shape.name)):
			       self.base._transitions[str(shape.name)] = dict()
		
		   if (isinstance(self.base.selected, Transition) and isinstance(shape, Place)):
		       if self.base._transitions.has_key(self.base.selected.name):
		           self.base._transitions[self.base.selected.name][shape.name] = int(weight)
			   if not self.base._places.has_key (str(shape.name)):
			       self.base._places[str(shape.name)] = dict()
		       else:
		       		self.base._transitions[self.base.selected.name] = dict() 	
		       		self.base._transitions[self.base.selected.name][shape.name] = int(weight)
		       		if not self.base._places.has_key (str(shape.name)):
			      		 self.base._places[str(shape.name)] = dict()	

		   if (isinstance(self.base.selected, Transition) and isinstance(shape, Diamond)):
		       dlg2 = wx.TextEntryDialog(None, 'Please specify which place should be pointed back:')
		       if dlg2.ShowModal() == wx.ID_OK:
		           pname = dlg2.GetValue()	
			   pname.replace(" ", "")
		       dlg2.Destroy()

		       self.base._transitions[str(self.base.selected.name)] = dict()
		       self.base.transback[str(self.base.selected.name)] = [str(pname), int(weight)]

		       self.base._transitions[str(self.base.selected.name)][str(pname)] = int(weight)

                   line = Arrow(weight)

                   line.SetCanvas(self.canvas)
                   line.SetPen(wx.BLACK_PEN)
                   line.SetBrush(wx.BLACK_BRUSH)

		   line.AddArrow(ogl.ARROW_ARROW, name = weight) 	
                   line.MakeLineControlPoints(2)
		   line.SetDraggable(True, True)

		   shape_font = wx.Font(5, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
		   #line.SetFont(model.shape_font)
		   line.SetFont(shape_font, regionId = 2) 			
		   line.AddText(weight)
		   #print 'first shape', shape
                   self.base.selected.AddLine(line, shape)
		   #shape.AddText(weight)
                   self.diagram.AddShape(line)
                   line.Show(True)
                   
                   # Now add to output
                   #self.base.selected.outputs.append(shape)
                   
                   self.base.selected.Move(self.dc, self.base.selected.GetX(), self.base.selected.GetY())

	       if (isinstance(self.base.selected, Diamond) and isinstance(shape, Diamond)):
		   #line = ogl.LineShape()
		   line = Arrow()
                   line.SetCanvas(self.canvas)
                   line.SetPen(wx.BLACK_PEN)
                   line.SetBrush(wx.BLACK_BRUSH)
		   line.AddArrow(ogl.ARROW_ARROW)
		   line.MakeLineControlPoints(2)
                   #shape.name = self.base.selected.name
		   #print 'second shape', shape
		   self.base.selected.AddLine(line, shape)
		   self.diagram.AddShape(line)
		   line.Show(True)
                   #self.base.selected.outputs.append(shape)
                   
                   self.base.selected.Move(self.dc, self.base.selected.GetX(), self.base.selected.GetY())
		    
		
               self.base.selected = None
               self.canvas.Adjust()
           else:
               self.base.selected = shape
        elif self.base.mode == "view":
            # If in view mode, and right click, then pop menu
            menu = wx.Menu()
            menu.Append(ID_DELETE_PRIMITIVE, "Delete")
            self.base.win.Bind(wx.EVT_MENU, self.OnDeletePrimitive, id = ID_DELETE_PRIMITIVE)
            #menu.Append(ID_CHANGE_NAME, "Change primitive name")
            #self.base.win.Bind(wx.EVT_MENU, self.OnChangeName, id = ID_CHANGE_NAME)

            if isinstance(shape, Place):
                #menu.Append(ID_EDIT_TOKEN, "Assign tokens")
                #self.base.win.Bind(wx.EVT_MENU, self.OnAssignToken, id = ID_EDIT_TOKEN)
                menu.Append(ID_CHANGE_NAME, "Change primitive name")
                self.base.win.Bind(wx.EVT_MENU, self.OnChangeName, id = ID_CHANGE_NAME)
            if isinstance(shape, Transition):
                #menu.Append(ID_SUPER_TRANSITION, "Make SuperTransition")
                #self.base.win.Bind(wx.EVT_MENU, self.OnSuperTransition, id = ID_SUPER_TRANSITION)
                menu.Append(ID_NEW_WINDOW, "New window")
                self.base.win.Bind(wx.EVT_MENU, self.NewWindow, id = ID_NEW_WINDOW)
                menu.Append(ID_CHANGE_NAME, "Change primitive name")
                self.base.win.Bind(wx.EVT_MENU, self.OnChangeName, id = ID_CHANGE_NAME)
            
            self.base.win.PopupMenu(menu, (x,y))

        self.UpdateStatusBar(shape)


    def OnDeletePrimitive(self, event):
        shape = self.GetShape()

	canvas = shape.GetCanvas()

        lines = shape.GetLines()
	while lines:
            for line in lines:

	
	        if isinstance(shape, Place): 
		    if (isinstance(line.GetFrom(), Place) ):
    	                if self.base._places.has_key(str(line.GetFrom().name)):
 		            del self.base._places[str(line.GetFrom().name)]

		    elif self.base._transitions.has_key(str(line.GetFrom().name)):
		        if self.base._transitions[str(line.GetFrom().name)].has_key(str(line.GetTo().name)):
		            del self.base._transitions[str(line.GetFrom().name)][str(line.GetTo().name)]


	        if isinstance(shape, Transition): 
		    if (isinstance(line.GetFrom(), Transition) ): 
		        if self.base._transitions.has_key(str(line.GetFrom().name)):
 		            del self.base._transitions[str(line.GetFrom().name)]

                    elif self.base._places.has_key(str(line.GetFrom().name)):
		        if self.base._places[str(line.GetFrom().name)].has_key(str(line.GetTo().name)):
		            del self.base._places[str(line.GetFrom().name)][str(line.GetTo().name)]

	        shape.RemoveLine(line)
                line.RemoveFromCanvas(self.canvas)

	if isinstance(shape, Place):
            self.base.places.remove(shape)
	    if self.base._places.has_key(str(shape.name)):
	        del self.base._places[str(shape.name)] 
	    for key in self.base._transitions:
		if self.base._transitions[key].has_key(str(shape.name)):
		    del self.base._transitions[key][str(shape.name)]    
            

	#print 'self.base.transitions', self.base.transitions
	if isinstance(shape, Transition):
            self.base.transitions.remove(shape)
	    del self.base.tlist[str(shape.name)]
	    if self.base._transitions.has_key(str(shape.name)):
	        del self.base._transitions[str(shape.name)] 
	    for key in self.base._places:
		if self.base._places[key].has_key(str(shape.name)):
		    del self.base._places[key][str(shape.name)]    

	
        shape.Detach()
        shape.DeleteControlPoints()
        shape.RemoveFromCanvas(self.canvas)
        del(shape)
        self.canvas.Adjust()
    """    
    def OnAssignToken(self, event):
    	shape = self.GetShape()
        tokens = self.GetToken()
    	if not tokens:
                shape.NumTokens = 0
        else:
                shape.NumTokens = tokens
        self.base.UpdateLists()
    
    def OnSuperTransition(self, event):
        dlg = wx.TextEntryDialog(self.base, "Please enter the names of 2 existing transitions:",
                                '', '')
                                
        if dlg.ShowModal() == wx.ID_OK:
            self.MakeSuperTransition(dlg.GetValue())
            
        dlg.Destroy()
        
        self.base.UpdateLists()
    """
    def NewWindow(self, event):
        shape  = self.GetShape()	
	_name = str(shape.name)
	binary = str(self.base.tlist[_name])
	SubPetriNet(_name, binary)
        


    """"
    def MakeSuperTransition(self, msg):
        transitions = [x.strip() for x in msg.split(',')]
        if not len(transitions) == 2:
            self.base.ShowMessage("Invalid number of transitions")
            return
        
        shape = self.GetShape()
        
        for i in transitions:
            if not i in [x.name for x in self.base.transitions]:
                self.base.ShowMessage("Non-existant transition given.")
                return
        
        start = None
        end   = None         
        for i in self.base.transitions:
            if i.name == transitions[0]:
                start = i
                
        for i in self.base.transitions:
            if i.name == transitions[1]:
                end = i 
                  
        shape.SuperTransition = True
        shape.SuperStart = start
        shape.SuperEnd = end
        
        self.base.UpdateLists()
    
    def GetToken(self):
        dlg = wx.TextEntryDialog(self.base, "Please enter the number of tokens for this place:",
				'','')
	if dlg.ShowModal() == wx.ID_OK:
            token = int(dlg.GetValue())

        dlg.Destroy()
        return token
    """	

    def OnChangeName(self, event):
        shape = self.GetShape()
        name = self.GetName()
        if not name or name in [x.name for x in self.base.places + self.base.transitions]:
	    #self.ShowMessage("Duplicate name.")
            pass
        if name in [x.name for x in self.base.places + self.base.transitions]:
	    dlg = wx.MessageDialog(None, "Duplicate name.")
	    dlg.ShowModal()
            dlg.Destroy()
            pass
        else:
            shape.name = name
            shape.ClearText()
            shape.AddText(name)
            shape.GetCanvas().Adjust()
            #self.base.UpdateLists()
    """
    def ShowMessage(self, msg):
        dlg = wx.MessageDialog(self, msg, 'Petri Sim Message', wx.OK | wx.ICON_INFORMATION)
        
        dlg.ShowModal()
        dlg.Destroy()
    """
    def GetName(self):
        dlg = wx.TextEntryDialog(self.base, "Please enter a new name for this primitive:",
				'','')
        if dlg.ShowModal() == wx.ID_OK:
            name = str(dlg.GetValue())
        
        dlg.Destroy()
        return name
