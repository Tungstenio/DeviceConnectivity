import wx        # Library used for the interface components

from panelIntroV1      import mainIntroPanel
from panelGeneralModel import deviceGeneralPanel
from macroPanel        import macroGeneralPanel
from recorder import Recorder

from wx.lib.pubsub import pub

# Defines the "Frame" class that will contain all the functions associated to buttons contained in the interface.
# It could be considered as the top module of the source code.
class GeneralFrame(wx.Frame):
    # __init__ is the initialization routine of the Frame class. Once the class is called in "main", the __init__
    # is responsible for actually creating the interface
    def __init__(self, parent, title):
        super(GeneralFrame, self).__init__(parent, title=title)

        pub.subscribe(self.showPage,  'AssigningDone')
        pub.subscribe(self.killPage,  'AssignCleared')
        pub.subscribe(self.macroPage, 'MacroOpen')
##        pub.subscribe(self.switchPages, 'DevPanelCreated')

        self.devicePanel = []
        self.macroPanel  = []

        ##Version
        self.version = ' v0.1'

        self.CreateStatusBar() # A StatusBar in the bottom of the window

        # Setting up the menu.
        filemenu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets.
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit  = filemenu.Append(wx.ID_EXIT,  "&Exit", " Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)         # Adding the MenuBar to the Frame content.

        self.recorder = Recorder()

        # Set events.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit,  menuExit)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.nb         = wx.Notebook(self)
        self.IntroPanel = mainIntroPanel(self.nb)
        self.nb.AddPage(self.IntroPanel, "Panel Intro")

        self.frameSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.frameSizer.Add(self.nb, 0, wx.ALL|wx.EXPAND, 5)

        self.SetTitle( ''.join(['Lab Automation Interface', self.version]) )

        self.SetSizerAndFit(self.frameSizer)
        self.Move(wx.Point(0,0))
        
    def OnAbout(self,event):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "Lab Automation Interface", "About", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy()   # finally destroy it when finished.

    def OnExit(self,event):
        self.Close(True)  # Close the frame.

    def OnClose(self, event):
        if not self.IntroPanel:
            self.Destroy()
        elif not self.IntroPanel.openedResList:
            self.Destroy()
        else:
            for devs in self.IntroPanel.openedResList:
                print('closing')
                # TODO: We should remove this line at some point (it causes a crash if the device was unplugged
                print(devs)
                devs.close()
            self.Destroy()

    def showPage(self, msg):

        self.devicePanel = deviceGeneralPanel(self.nb, msg)
        
        self.nb.AddPage(self.devicePanel, "Data Acquisition")
        newSizer = wx.BoxSizer(wx.HORIZONTAL)
        newSizer.Add(self.nb,0,wx.ALL|wx.EXPAND,5)

        index = self.nb.GetPageCount() - 1 # get the index of the final page.
        self.nb.SetSelection(index)        # set the selection to the final page
        # self.nb.SetSelection(index-1)
        # self.nb.SetSelection(index)

        self.SetSizerAndFit(newSizer)

    def killPage(self, msg):

        killIndex = self.nb.GetPageCount() - 1
        if killIndex != 0:
            self.nb.DeletePage(killIndex)

    def macroPage(self, msg):
        self.macroPanel = macroGeneralPanel(self.nb, self.recorder)

        self.nb.AddPage(self.macroPanel, "Macro")
        newSizer = wx.BoxSizer(wx.HORIZONTAL)
        newSizer.Add(self.nb, 0, wx.ALL | wx.EXPAND, 5)

        # index = self.nb.GetPageCount() - 1  # get the index of the final page.
        # self.nb.SetSelection(index)  # set the selection to the final page
        # self.nb.SetSelection(index - 1)
        # self.nb.SetSelection(index)

        self.SetSizerAndFit(newSizer)

        
#############
# Main Code #
#############
app   = wx.App(False)
frame = GeneralFrame(None, title = '')

frame.Show()
app.MainLoop()
