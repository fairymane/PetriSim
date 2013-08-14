import sys
import re
import os
import wx
import wx.lib.ogl as ogl
import wx.grid as gridlib
from wx import InitAllImageHandlers
from mystatusbar import CustomStatusBar
from primitives import *
from DrawingBoard import *
import images
import subprocess
import pickle


#ID_TOKEN_CHANGE = wx.NewId()
ID_EXIT         = wx.NewId()
ID_ABOUT        = wx.NewId()
ID_LOAD_LIST    = wx.NewId()
ID_SAVE_LIST    = wx.NewId()
ID_NEW_PLACE    = wx.NewId()

ID_NEW_POLYGON    = wx.NewId()
#ID_NEW_POINT    = wx.NewId()

ID_NEW_TRANSITION = wx.NewId()
ID_NEW_ARROW    = wx.NewId()
ID_MODE_CHOICE  = wx.NewId()
ID_SPIN_SCALE   = wx.NewId()
ID_NEW_PAGE     = wx.NewId()
ID_NOTEBOOK     = wx.NewId()
ID_VIEW         = wx.NewId()
ID_COMPILE      = wx.NewId()
ID_ANALYZE      = wx.NewId()

def flat(lst):
    temp = []
    for x in lst:
        for y in x:
            temp.append(y)
    return temp

class MyFrame(wx.Frame):
    '''This class is the main implementation for our interface'''
    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self, parent, ID, title, style=wx.DEFAULT_FRAME_STYLE,
                           size = wx.Size(1250,750))
        self.debug         = False                      # Set default debug to false
        self.mode          = "view"                    # default mode
        self.mode_list     = ["view", "design transition", "design place", "design arrow", "design polygon"] #"design points"]
        self.mode_dict     = self.make_modes()
        self.places        = []
        self._places       = dict()
        self._transitions   = dict()
        self._PLACE    = dict()
        self._TRANSITION   = dict()
        self.transback = dict()
        self._POLYGON = dict()
        self._LINE = dict()
        self.PRIM = dict()
        self.POLYCOUNT = 1

        self.transitions   = []
        self.tlist = dict()
        self.selected      = None
        self.ScaleList     = {}
        self.ScaleDefault  = 1.0
        self.pagecount     = 1
        self.iopage    = 1
        self.CurrentArea   = None

     
        self.InitMisc()   
        self.InitBars()
        self.InitWindows()
        self.InitControls()
        self.InitEvents()
        self.Maximize()
        self.Layout()

    def InitMisc(self):
        ogl.OGLInitialize()
        InitAllImageHandlers()

    def InitBars(self):
        self.StatusBar = CustomStatusBar(self)
        self.SetStatusBar(self.StatusBar)
        self.tb = self.CreateToolBar( wx.TB_HORIZONTAL | wx.TB_FLAT)
        self.tb.AddSimpleTool(ID_LOAD_LIST, images.getOpenBitmap(),
            "Load a Petri net...",
        "Open a saved Petri net from file")
        self.tb.AddSimpleTool(ID_SAVE_LIST, images.getDiskBitmap(),
            "Save the current Petri net...",
        "Save the current Petri net to file")
        self.tb.AddSeparator()
        self.tb.AddControl(wx.StaticText(self.tb,-1,"Current Mode: "))
        self.mode_choice = wx.ComboBox(self.tb, ID_MODE_CHOICE, "",
                           choices=self.mode_list, size=(100,-1), style=wx.CB_DROPDOWN)
        self.mode_choice.SetSelection(self.mode_dict[self.mode])
        self.tb.AddControl(self.mode_choice) 
        self.tb.AddSeparator()
        self.tb.AddControl(wx.StaticText(self.tb,-1,"Current Scale: "))
        self.ScaleCtrl = wx.TextCtrl(self.tb, -1, str(self.ScaleDefault), None, (60, -1))
        self.tb.AddControl(self.ScaleCtrl) 
        self.spin = wx.SpinButton(self.tb, ID_SPIN_SCALE, None,None, wx.SP_VERTICAL)
        self.tb.AddControl(self.spin)
        self.tb.Realize()
        filemenu = wx.Menu()
        self.menu_load = filemenu.Append(-1,"&Load a Petri net","Load the prebuilt Petri net.")
        self.menu_save = filemenu.Append(-1,"&Save current Petri net as...",
                                  "Save your design of Petri Net for future use")
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXIT, "E&xit", "Terminate PetriSim")

        settingmenu = wx.Menu()
        ID_SET_INTERVAL = settingmenu.Append(-1,"Set &zoom", "Set the zoom scale")
        ID_DEBUG_MENU = settingmenu.Append(-1,"Toggle &debug mode", "Toggle the debug mode")

        helpmenu = wx.Menu()
        helpmenu.Append(ID_ABOUT, "A&bout",
                    "More information about PetriSim")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        menuBar.Append(settingmenu,"&Setting")
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)
        
    def InitWindows(self):
        self.win = wx.Panel(self, -1)
        
        self.LeftPanTop = wx.Panel(self.win,-1,style=wx.NO_BORDER, size = wx.Size(120, 250))
        self.LeftPanBottom = wx.Panel(self.win,-1,style=wx.NO_BORDER, 

                                size = wx.Size(120,250))
        self.notebook = wx.Notebook(self.win, ID_NOTEBOOK)
        self.StatusPan = wx.Panel(self.win, -1, style=wx.NO_BORDER, 
                                size = wx.Size(140, -1))
        self.StatusPanSizer = wx.GridBagSizer(1,2)
        
        self.gbs = wx.GridBagSizer(1,2)
        self.gbs.Add(self.LeftPanTop, (0,0))
        self.gbs.Add(self.LeftPanBottom, (1,0))
        self.gbs.Add(self.notebook, (0,1),(2,1), wx.EXPAND)
        self.gbs.Add(self.StatusPan, (0,2), (2,1), wx.EXPAND )
        
        self.gbs.AddGrowableCol(1)
        self.gbs.AddGrowableRow(0)
        self.gbs.AddGrowableRow(1)
        
        self.win.SetSizerAndFit(self.gbs)

    def InitControls(self):
        # Help text
        helper1 = wx.StaticText(self.LeftPanTop, -1, "Click on the \nprimitives below:", (5,10))
        helper1.SetForegroundColour("Blue")
        helper2 = wx.StaticText(self.LeftPanBottom, -1, "Click on the \n operations below:", (5,10))
        helper2.SetForegroundColour("Blue")
        #helper3 = wx.StaticText(self.StatusPan, -1, "Initialize Tokens below:", (5,10))
        #helper3.SetForegroundColour("Blue")
        #self.StatusPanSizer.Add(helper3, (0,0), flag = wx.ALIGN_LEFT, border = 5)
        
        # Buttons
        self.t_button = wx.Button(self.LeftPanTop, ID_NEW_TRANSITION, "Transition", (5,50))
        self.p_button = wx.Button(self.LeftPanTop, ID_NEW_PLACE, "Place", (5,80))

        self.a_button = wx.Button(self.LeftPanTop, ID_NEW_ARROW, "Arrow", (5,140))
        self.po_button = wx.Button(self.LeftPanTop, ID_NEW_POLYGON, "Polygon", (5,110))

        self.addpage_button = wx.Button(self.LeftPanBottom, ID_NEW_PAGE, "New work area", (5, 50))
        self.v_button = wx.Button(self.LeftPanBottom, ID_VIEW, "Edit/Move", (5, 80))        
        self.c_button = wx.Button(self.LeftPanBottom, ID_COMPILE, "Compile", (5, 110))
        self.d_button = wx.Button(self.LeftPanBottom, ID_ANALYZE, "Run", (5, 140))
        
        # List Control
        #self.TokenCtrl = gridlib.Grid(self.StatusPan, -1)
        #self.TransitionCtrl = gridlib.Grid(self.StatusPan, -1)                  
        #self.InitList()      

        #self.StatusPanSizer.Add(self.TokenCtrl, (1,0), flag = wx.ALIGN_CENTRE|wx.EXPAND, 
        #                        border = 0)
        #self.StatusPanSizer.Add(self.TransitionCtrl, (2,0), flag = wx.ALIGN_CENTRE|wx.EXPAND, 
        #                        border = 0)
        #self.StatusPanSizer.AddGrowableRow(1)
        #self.StatusPanSizer.AddGrowableRow(2)
        #self.StatusPanSizer.AddGrowableCol(0)
        
        #self.StatusPan.SetSizerAndFit(self.StatusPanSizer)
        
        self.NewPage()
        
    #def InitList(self):
        #self.TokenCtrl.CreateGrid(1,2)
        #self.TransitionCtrl.CreateGrid(1,2)
        
        #self.TokenCtrl.SetColLabelSize(20)
        #self.TokenCtrl.SetRowLabelSize(20)
        #self.TokenCtrl.SetMargins(0,0)
        #self.TokenCtrl.AutoSizeColumns(False)
        #self.TokenCtrl.SetDefaultColSize(60, 1)
        #self.TokenCtrl.SetColLabelValue(0, "Place")

        #self.TokenCtrl.SetColLabelValue(1, "Point")

        #self.TokenCtrl.SetColLabelValue(1, "Tokens")
        
        #self.TransitionCtrl.SetColLabelSize(20)
        #self.TransitionCtrl.SetRowLabelSize(20)
        #self.TransitionCtrl.SetMargins(0,0)
        #self.TransitionCtrl.AutoSizeColumns(False)
        #self.TransitionCtrl.SetDefaultColSize(60, 1)
        #self.TransitionCtrl.SetColLabelValue(0, "Transition")
        #self.TransitionCtrl.SetColLabelValue(1, "Type")
        
    def InitEvents(self):
        self.Bind(wx.EVT_MENU, self.OnAbout, id = ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.TimeToQuit, id = ID_EXIT)
        self.Bind(wx.EVT_MENU, self.Save, self.menu_save)
        self.Bind(wx.EVT_MENU, self.Load, self.menu_load)

        wx.EVT_BUTTON(self, ID_NEW_TRANSITION, self.NewTransition)
        wx.EVT_BUTTON(self, ID_NEW_PLACE, self.NewPlace)
        wx.EVT_BUTTON(self, ID_NEW_POLYGON, self.NewPolygon)

    #wx.EVT_BUTTON(self, ID_NEW_POINT, self.NewPoint)

        wx.EVT_BUTTON(self, ID_NEW_ARROW, self.NewArrow)
        wx.EVT_BUTTON(self, ID_NEW_PAGE, self.NewPage)
        wx.EVT_BUTTON(self, ID_VIEW, lambda event,self=self: self.SetMode("view"))
        wx.EVT_BUTTON(self, ID_COMPILE, self.CompileGraph)
        wx.EVT_BUTTON(self, ID_ANALYZE, self.OnAnalyze)
        
        wx.EVT_MENU(self, ID_LOAD_LIST, self.Load)
        wx.EVT_MENU(self, ID_SAVE_LIST, self.Save)

        wx.EVT_UPDATE_UI(self, -1, self.UpdateCursor)
        self.Bind(wx.EVT_COMBOBOX, self.OnCombo, id = ID_MODE_CHOICE)
        wx.EVT_SPIN_UP(self, ID_SPIN_SCALE, self.ScaleSpinUp)
        wx.EVT_SPIN_DOWN(self, ID_SPIN_SCALE, self.ScaleSpinDown)
        wx.EVT_NOTEBOOK_PAGE_CHANGED(self, ID_NOTEBOOK, self.On_NB_Changed)

    def parseGraphStructure(self):
        for shape in self.CurrentArea.diagram.GetShapeList():
            if isinstance(shape, Place):
                self._PLACE[str(shape.name)] = [shape.GetX(), shape.GetY()]
            if isinstance(shape, Transition):
                self._TRANSITION[str(shape.name)] = [shape.GetX(), shape.GetY(), shape.type]
            if isinstance(shape, Diamond):
                self._POLYGON[str(shape.name)] = [shape.GetX(), shape.GetY()]
            if isinstance(shape, Arrow):
                if self._LINE.has_key(str(shape.GetFrom().name)):
                    self._LINE[str(shape.GetFrom().name)].append([str(shape.GetTo().name), str(shape.name), shape.GetEnds()])
                else:
                    self._LINE[str(shape.GetFrom().name)] = [[str(shape.GetTo().name), str(shape.name), shape.GetEnds()]]
            

           
  

    def SaveGraph(self, path):
        graph_file = open(path, 'wb')
        pickle.dump([self._PLACE, self._TRANSITION, self._POLYGON, self._LINE, self.transback], graph_file)
        graph_file.close()

    def Save(self, event):
        self.parseGraphStructure()
        dlg = wx.FileDialog( self, message="Save graph as...", defaultDir=os.getcwd(),
                            defaultFile=".draw", style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.SaveGraph(path)
        dlg.Destroy()

    def Load(self, event):
        dlg = wx.FileDialog(
            self, message = "Choose the input graph", defaultDir=os.getcwd(),
            defaultFile="", style=wx.OPEN|wx.CHANGE_DIR
            )
     
        if dlg.ShowModal() == wx.ID_OK:
            ingraph = dlg.GetPath()

            graph_struct = pickle.load(open (ingraph, 'rb'))
            self.reDraw(graph_struct)
        else:
            return
        dlg.Destroy()

    ##Redraw the graph according to the loaded file 
    def reDraw(self, graph_struct):
        places = graph_struct[0]        
        transitions = graph_struct[1]
        polygons = graph_struct[2]
        lines = graph_struct[3]
        if graph_struct[4]:
            transback = graph_struct[4]

        if self.CurrentArea.diagram.GetShapeList():
            newWin = wx.App
            frame = GUI.MyFrame(None, -1, "PetriSim!")
            frame._Draw(places, transitions, polygons, lines)
            if graph_struct[4]:
                frame.transback = transback
                for key in transback.keys():

                    frame._transitions[key] =dict()
                    frame._transitions[key][transback[key][0]] = transback[key][1]
            frame.Show(True)
            return True
        else:
        
            self._Draw(places, transitions, polygons, lines)
            if graph_struct[4]:
            	self.transback = transback
            	for key in transback.keys():
                	self._transitions[key] =dict()
                	self._transitions[key][transback[key][0]] = transback[key][1]

            return self.CurrentArea

            
        
    ## Redraw all the primitives and arrows
    ## This  helper function do most implementation
    def _Draw(self, places, transitions, polygons, lines):
        for place_key in places.keys():
            brush = wx.Brush("LIGHT GREY", wx.SOLID)
            shape = Place(40, place_key)
            self.CurrentArea.MyAddShape(shape, places[place_key][0], places[place_key][1], wx.Pen(wx.RED, 1), brush, place_key )
            shape.Move(self.CurrentArea.dc, shape.GetX(), shape.GetY())
            self.places
            self.places.append(shape)
            self.PRIM[place_key] = shape

        for t_key in transitions.keys():
            if transitions[t_key][2] == 0:
                brush = wx.Brush("AQUAMARINE", wx.SOLID)
            if transitions[t_key][2] == 1:
                brush = wx.Brush("GREEN YELLOW", wx.SOLID)
        
            shape = Transition(60, 30, t_key, transitions[t_key][2])
            self.tlist[t_key] = str(transitions[t_key][2])
            self.CurrentArea.MyAddShape(shape, transitions[t_key][0], transitions[t_key][1], wx.Pen(wx.RED, 1), brush, t_key )
            shape.Move(self.CurrentArea.dc, shape.GetX(), shape.GetY())
            self.transitions.append(shape)
            self.PRIM[t_key] = shape

        for poly_key in polygons.keys():
            brush = wx.Brush("LIGHT GREY", wx.SOLID)
            shape = Diamond(24, 30,  poly_key)
            self.CurrentArea.MyAddShape(shape, polygons[poly_key][0], polygons[poly_key][1], wx.Pen(wx.RED, 1), brush, poly_key )
            shape.Move(self.CurrentArea.dc, shape.GetX(), shape.GetY())
            self.PRIM[poly_key] = shape

        for l_key in lines.keys():
            for value in lines[l_key]:
                self._DrawLine(l_key, value[0], value[2], value[1])

        #self.flowControl(pfrom, pto, weight)

        self.CurrentArea.Adjust()
    ## for each line, set entds points, connecting to
    ## related primitives and restore the connectition logic
    ## dictionary
    def _DrawLine(self, pfrom, pto, Ends, weight=None ):
    #print 'type Ends', type(Ends)
        line = Arrow(weight)

        line.SetCanvas(self)
        line.SetPen(wx.BLACK_PEN)
        line.SetBrush(wx.BLACK_BRUSH)
        line.AddArrow(ogl.ARROW_ARROW, name = weight)   
        line.MakeLineControlPoints(2)
        line.SetDraggable(True, True)

        if weight:
            shape_font = wx.Font(5, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)           
            line.SetFont(shape_font, regionId = 2)      
            line.AddText(weight)


        """
    line.SetEnds(Ends[0],Ends[1],Ends[2],Ends[3])
        line.SetFrom(self.PRIM[pfrom])
        line.SetAttachmentFrom(self.PRIM[pfrom])
        
    line.SetTo(self.PRIM[pto])
    line.SetAttachmentTo(self.PRIM[pto])
        line.SetDraggable(True, True)
        """
        self.flowControl(self.PRIM[pfrom], self.PRIM[pto], weight)
        
        self.PRIM[pfrom].AddLine(line, self.PRIM[pto])

        #print 'line.GetFrom()', line.GetFrom() 
    #print 'line.To()', line.GetTo()    
        self.CurrentArea.diagram.AddShape(line)        
        line.Show(True)
    
    def flowControl(self, pfrom, pto, weight):

        if (isinstance(pfrom, Place) and isinstance(pto, Transition)):
        #print 'from Place to Transition', pfrom.name, pto.name       
            if self._places.has_key(str(pfrom.name)):
        
                self._places[str(pfrom.name)][str(pto.name)] = int(weight)
                if not self._transitions.has_key (str(pto.name)):
                    self._transitions[str(pto.name)] = dict()
            else:
                self._places[str(pfrom.name)] = dict()  
                self._places[str(pfrom.name)][str(pto.name)] = int(weight)
                if not self._transitions.has_key (str(pto.name)):
                    self._transitions[str(pto.name)] = dict()   
        if (isinstance(pfrom, Transition) and isinstance(pto, Place)):

            #print 'from Transition to Place',pfrom.name,pto.name
    
            if self._transitions.has_key(str(pfrom.name)):
                self._transitions[str(pfrom.name)][str(pto.name)] = int(weight)
                if not self._places.has_key (str(pto.name)):
                    self._places[str(pto.name)] = dict()
            else:
                self._transitions[str(pfrom.name)] = dict()     
                self._transitions[str(pfrom.name)][str(pto.name)] = int(weight)
                if not self._places.has_key (str(pto.name)):
                    self._places[str(pto.name)] = dict()
        #if (isinstance(pfrom, Transition) and isinstance(pto, Diamond)):
        
    #    print 'from Transition to Diamond',pfrom.name,pto.name
        
            
        
       
    def OnAbout(self,event):
        dlg = wx.MessageDialog(self, "This project is "\
                                     "created by:\n\n- Prof. Ramavarapu S. Sreenivas, rsree@uiuc.edu\n\n"\
                                     "- Shuo Yang, "\
                                     "bigjhnny@gmail.com",
                                    "About PetriSim", wx.OK | wx.ICON_INFORMATION)    
        dlg.ShowModal()
        dlg.Destroy()

    def TimeToQuit(self,event):
        self.Close(True)

    def NewTransition(self, event):
        self.SetMode("design transition")
    
    def NewPlace(self, event):
        self.SetMode("design place")

    def NewPolygon(self, event):
        self.mode = "design polygon"
        #self.mode_choice.SetSelection(self.mode_dict[self.mode])
        #self.UpdateCursor()

    #def NewPoint(self, event):
        #self.SetMode("design point")

    def SetMode(self, mode):
        self.mode = mode
        self.mode_choice.SetSelection(self.mode_dict[self.mode])
        self.UpdateCursor()
        
    def NewArrow(self, event):
        self.mode = "design arrow"
        self.mode_choice.SetSelection(self.mode_dict[self.mode])
        self.UpdateCursor()

    def NewPage(self, event = None):
        # TODO: Fix the type error of self.CurrentArea
        DrawBoard = DrawingBoard(self.notebook, sys.stdout, self)
        self.ScaleList[id(DrawBoard)] = self.ScaleDefault
        self.notebook.AddPage(DrawBoard, "Work area %d" % self.pagecount, 1)
        DrawBoard.fix()
        DrawBoard.Bind(wx.EVT_LEFT_DOWN, self.OnDraw)
        DrawBoard.Bind(wx.EVT_KEY_DOWN, self.ProcessKeys)
        self.CurrentArea = DrawBoard
        self.pagecount += 1
        return self.CurrentArea

    def OnDraw(self, event):
        if self.mode == "design transition":
            self.DrawTransition(event)
            
        elif self.mode == "design place":
            self.DrawPlace(event)

        elif self.mode == "design polygon":
            self.DrawPolygon(event)

        #elif self.mode == "design point":
         #   self.DrawPoint(event)
               
        elif self.mode == "design arrow":
            event.Skip()
        #self.DrawArrow(event)
        else:
            event.Skip()
        
        #self.UpdateLists()
        
    #def UpdateLists(self):
        #if self.TokenCtrl.GetNumberRows():
        #    self.TokenCtrl.DeleteRows(0, self.TokenCtrl.GetNumberRows())
        #if self.TransitionCtrl.GetNumberRows():
        #    self.TransitionCtrl.DeleteRows(0, self.TransitionCtrl.GetNumberRows())
        
        #for v in self.places:
        #    self.TokenCtrl.InsertRows()
        #    self.TokenCtrl.SetCellValue(0, 0, v.name)
        #    self.TokenCtrl.SetCellValue(0, 1, str(v.NumTokens))

        
        #for v in self.transitions:
        #    self.TransitionCtrl.InsertRows()
        #    self.TransitionCtrl.SetCellValue(0, 0, v.name)
        #    if v.SuperTransition:
        #        self.TransitionCtrl.SetCellValue(0, 1, '%s,%s' %   (v.SuperStart.name, v.SuperEnd.name))
        #    else:
        #        self.TransitionCtrl.SetCellValue(0, 1, 'Regular')

                
    def DrawPlace(self,event):
    #print "draw place"
        name = self.GetName("place")
        if not name: return
        if name in [x.name for x in self.places]:
            self.ShowMessage("Duplicate name.")
            self.CurrentArea.Adjust()
        return
        
        brush = wx.Brush("LIGHT GREY", wx.SOLID)
        shape = Place(40, name)
        self.places.append(shape)
    
        self.CurrentArea.MyAddShape(
            shape,
            event.GetX(), event.GetY(), wx.Pen(wx.RED, 1), brush, name )
        
        shape.Move(self.CurrentArea.dc, shape.GetX(), shape.GetY())
        self.CurrentArea.Adjust()
    """
    def DrawArrow(self,event):
        name = self.GetName("arrow")
        if not name: return
        brush = wx.Brush("LIGHT GREY", wx.SOLID)
        shape = Arrow(name)
        
        self.CurrentArea.MyAddShape(
            shape,
            event.GetX(), event.GetY(), wx.Pen(wx.RED, 1), brush, name )
        
        shape.Move(self.CurrentArea.dc, shape.GetX(), shape.GetY())
    self.CurrentArea.Adjust()
     """
#-----------------------------------------
#Add on 3/5/13, to simulate the draggable line
    def DrawPolygon(self,event):
    
        name = self.GetName("polygon")
        brush = wx.Brush("LIGHT GREY", wx.SOLID)
        shape = Diamond(24, 30, str(self.POLYCOUNT))
        
        self.CurrentArea.MyAddShape(
            shape,
            event.GetX(), event.GetY(), wx.Pen(wx.RED, 1), brush, str(self.POLYCOUNT) )
        self.POLYCOUNT = self.POLYCOUNT+1
        shape.Move(self.CurrentArea.dc, shape.GetX(), shape.GetY())
        self.CurrentArea.Adjust()

#-------------------------

    def DrawTransition(self,event):
        name = self.GetName("transition")


        # If user cancel, then pass
        if not name: return
        namelist = name.split();
        _name = str(namelist[0])
        if len (namelist) <2:
            self.ShowMessage("Please provide the status of transition, 0 or 1\n followed by transition name, e.g. t1 1")
            return
        if _name in [x.name for x in self.transitions]:
            self.ShowMessage("Duplicate name.")
            return
        if int(namelist[1])!=0 and int(namelist[1])!=1:
            self.ShowMessage("The status could only be 0 or 1")
            return      
            
        shape = Transition(60, 30, _name, int(namelist[1]))
        self.transitions.append(shape)
        if self.tlist.has_key(_name):
            self.ShowMessage("Duplicate namekey.")
            return
            
        self.tlist[_name] = str(namelist[1]);
       
        if int(namelist[1]) ==0:  
            brush = wx.Brush("AQUAMARINE", wx.SOLID)
        #print 'aha, brush', brush
        elif int(namelist[1]) ==1:  
            brush = wx.Brush("GREEN YELLOW", wx.SOLID)
        #print 'aha, brush', brush
        self.CurrentArea.MyAddShape(
            shape,
            event.GetX(), event.GetY(), wx.Pen(wx.BLUE, 1), brush, _name)
        #print 'event.GetX()', event.GetX()
    #print 'event.GetY()', event.GetY()
        
        
        shape.Move(self.CurrentArea.dc, shape.GetX(), shape.GetY())
        self.CurrentArea.Adjust()
            
    def RefreshStatusPan(self):
        pass

    def OnCombo(self, event):
        self.mode = event.GetString()
        if self.debug: print "switched mode to %s" % self.mode
        self.UpdateCursor()

    def UpdateCursor(self, event=None):
        if self.mode == "view":
            self.CurrentArea.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        else:
            self.CurrentArea.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

    def GetName(self, primitive):
        dlg = None
        if primitive == "place":
            dlg = wx.TextEntryDialog(self, 'Please provide a name:',"What's the place's name")

        if primitive == "arrow":
            dlg = wx.TextEntryDialog(self, 'Please provide a weight:',"What's the arrow's weight",'weight')
        return

        if primitive == "transition":
            dlg = wx.TextEntryDialog(self, 'Please provide a name:',"What's the transition's name")

        if primitive == "polygon":
            dlg = wx.TextEntryDialog(self, 'Please provide a name:',"What's the polygon's name", 'polygon')
        return
    
        if dlg.ShowModal() == wx.ID_OK:
            return dlg.GetValue()
        else:
            return None

    def make_modes(self):
        dict = {}
        for i,v in enumerate(self.mode_list):
            dict[v] = i
        return dict
    
    def ScaleSpinUp(self, event):
        self.ScaleList[id(self.CurrentArea)] *= 1.25
        self.ScaleSpinRefresh()

    def ScaleSpinDown(self, event):
        self.ScaleList[id(self.CurrentArea)] *= 0.8
        self.ScaleSpinRefresh()
        
    def ScaleSpinRefresh(self):
        scale = self.ScaleList[id(self.CurrentArea)]
        self.ScaleCtrl.SetValue(str(scale))
        self.CurrentArea.SetScale(scale,scale)
        self.CurrentArea.Adjust()
         
    def On_NB_Changed(self, event):
        # old = event.GetOldSelection()
        new = event.GetSelection()
        self.CurrentArea = self.notebook.GetPage(new) 

    def ProcessKeys(self, event):
        # If exit key pressed
        if event.GetKeyCode() == 27:
            self.SetMode("view")
            
    def CompileGraph(self, event):
        wildcard = "Petri Sim compiled text (*.txt)|*.txt|" \
                    "All files (*.*)|*.*"
        dlg = wx.FileDialog( self, message="Save compiled text as...", defaultDir=os.getcwd(),
                            defaultFile=".input", wildcard = wildcard, style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.SaveGraphTo(path)

        dlg.Destroy()
        
    def SaveGraphTo(self, path):
        fd = open(path, 'w')
        #self.ParseGraph(fd)
        self._ParseGraph(fd)
        fd.close()
    def _ParseGraph(self, fd):

        Tlen = len(self._transitions)
        Plen = len(self._places)    
        fd.write('%d %d  \n' % (Plen, Tlen))
        row = 0
        col = 0
    
        for key in sorted(self._transitions.iterkeys()):

        #self.InPutgrid.SetColLabelValue(col, str(key))
            col = col+1

        col = 0
    
        for key, value in sorted(self._places.iteritems()):

        #self.InPutgrid.SetRowLabelValue(row, str(key))
        
            for tkey in sorted(self._transitions.iterkeys()):

                if value.has_key(tkey): #and len(self._places[key]) >0 :
                    fd.write('%6d' % value[tkey])
                    #self.InPutgrid.SetCellValue(row, col, str(value[tkey]) )
                    col = col +1
                else:
                    fd.write('     0')
                #self.InPutgrid.SetCellValue(row, col, '0' )
                    col = col +1

            row = row+1
            col = 0
            fd.write('\n')
        row = 0
        col = 0

    #fd.write ('\n\n\n---------------------OUTPUT-----------------------\n')
    #fd.write('      ')
        for key in sorted(self._transitions.iterkeys()):
            col = col +1
        fd.write('\n')
        col =0

        for key in sorted(self._places.iterkeys()):
        
            for tkey, tvalue in sorted(self._transitions.iteritems()):

                if tvalue.has_key(key):# or tvalue.has_key('zz'): #and len(self._transitions[tkey]) >0:

                    fd.write('%6d' % tvalue[key])
                    #self.OutPutgrid.SetCellValue(row, col, str(tvalue[key]) )
                    col = col+1

            
            else:
                fd.write('     0')
           #self.OutPutgrid.SetCellValue(row, col, '0' )
                col = col +1

        	row = row+1
        	col = 0
        	fd.write('\n')  
    	row = 0
    	col = 0
    	for tkey in sorted (self.tlist.iterkeys()):
    	    fd.write (' %2d' % int(self.tlist[tkey]))
       
    def ShowMessage(self, msg):
        dlg = wx.MessageDialog(self, msg, 'Petri Sim Message', wx.OK | wx.ICON_INFORMATION)
        
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnAnalyze(self, event):

        wildcard = "Petri sim analyzer (*.exe)|*.exe|" "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message = "Choose the executable engine", defaultDir=os.getcwd(),
            defaultFile="", style=wx.OPEN|wx.CHANGE_DIR
            )
            
        if dlg.ShowModal() == wx.ID_OK:
            prog = dlg.GetPath()
            #print 'path', prog
        else:
            return

        dlg.Destroy()

        #wildcard = "Petri sim compiled text (*.txt)|*.txt|" \
         #          "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message = "Choose the input file", defaultDir=os.getcwd(),
            defaultFile="", style=wx.OPEN|wx.CHANGE_DIR
            )
     
        if dlg.ShowModal() == wx.ID_OK:
            infile = dlg.GetPath()
            path, filename = os.path.split(infile)
        else:
            return


        dlg.Destroy()

        dlg = wx.TextEntryDialog(self, 'Please enter the outputfile name:', "output file", filename+'.lesp')        
        if dlg.ShowModal() == wx.ID_OK:
            ofname = str(dlg.GetValue())

        offile = os.path.join(path, ofname)
    #print 'offile', offile

        p = subprocess.Popen([prog, infile, '%s' % offile], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, bufsize=1)




    """
        wildcard = "Petri sim analyzer (*.exe)|*.exe|" \
                   "All files (*.*)|*.*"
                   
        dlg = wx.FileDialog(
            self, message = "Choose the executable analyzer", defaultDir=os.getcwd(),
            defaultFile="", wildcard=wildcard, style=wx.OPEN|wx.CHANGE_DIR
            )
            
        if dlg.ShowModal() == wx.ID_OK:
            prog = dlg.GetPath()
        else:
            return

        dlg.Destroy()
        
        wildcard = "Petri sim compiled text (*.txt)|*.txt|" \
                   "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message = "Choose the petri sim compiled text file", defaultDir=os.getcwd(),
            defaultFile="", wildcard=wildcard, style=wx.OPEN|wx.CHANGE_DIR
            )
     
        if dlg.ShowModal() == wx.ID_OK:
            input = dlg.GetPath()
        else:
            return

        dlg.Destroy()

        wildcard = "Petri sim output file (*.txt)|*.txt|" \
                   "All files (*.*)|*.*"
                   
        dlg = wx.FileDialog(
            self, message = "Choose the output file", defaultDir=os.getcwd(),
            defaultFile="", wildcard=wildcard, style=wx.OPEN|wx.CHANGE_DIR
            )
     
        if dlg.ShowModal() == wx.ID_OK:
            output = dlg.GetPath()
        else:
            return

        dlg.Destroy()
            
        # Execute the program here
        os.execv(prog,['foo',input,output])
        
        self.ShowMessage("Output written to %s." % output)
        """
