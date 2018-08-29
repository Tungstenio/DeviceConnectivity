import wx.lib.scrolledpanel as scrolled
import wx

from wx.lib.pubsub import pub

class macroCtrlSubPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self,parent)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        bmpPlay  = wx.Bitmap("playIcon.png", wx.BITMAP_TYPE_ANY)
        bmpPause = wx.Bitmap("pauseIcon.png", wx.BITMAP_TYPE_ANY)
        self.bmapBtnPlay = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmpPlay,
                                             size=(bmpPause.GetWidth() + 10, bmpPause.GetHeight() + 10))
        self.bmapBtnPause  = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmpPause,
                                             size=(bmpPause.GetWidth() + 10, bmpPause.GetHeight() + 10))

        button_sizer.Add(self.bmapBtnPlay,0,wx.ALIGN_RIGHT,1)
        button_sizer.Add(self.bmapBtnPause, 0,wx.ALIGN_RIGHT,1)

        self.SetSizerAndFit(button_sizer)

class macroEntry(wx.Panel):

    def __init__(self, parent, macroList, devName, instName, paramValue, paramName, depth, reps):
        wx.Panel.__init__(self,parent)

        macro_sizer = wx.BoxSizer(wx.VERTICAL)

        instSimp = instName.replace('\n', ' ')
        
        paramString = str(paramValue) if paramName else ''

        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.hierarchyCB = wx.ComboBox(self, value=str(depth), choices=macroList)
        self.deviceName  = wx.TextCtrl(self, wx.ID_ANY, devName, style=wx.TE_READONLY|wx.NO_BORDER, size=(300,20))
        self.instName    = wx.StaticText(self, 1, instSimp, size=(300, 20))
        self.paramInput  = wx.TextCtrl(self, value = paramString, size=(150, 20))
        self.reps        = wx.TextCtrl(self, value=str(reps), size=( 50, 20))
        input_sizer.Add(self.hierarchyCB, 0, wx.ALL|wx.EXPAND, 5)
        input_sizer.Add(self.deviceName,  0, wx.ALL|wx.EXPAND, 5)
        input_sizer.Add(self.instName,    0, wx.ALL|wx.EXPAND, 5)
        input_sizer.Add(self.paramInput,  0, wx.ALL|wx.EXPAND, 5)
        input_sizer.Add(self.reps,        0, wx.ALL|wx.EXPAND, 5)
        
        if not paramName: # No name supplied in the device class
            self.paramInput.Disable()

        label_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.hRBLabel      = wx.StaticText(self, 1, 'Depth',                 size=( 40,20))
        self.devNameLabel  = wx.StaticText(self, 1, 'Device IDN',            size=(300,20))
        self.instNameLabel = wx.StaticText(self, 1, 'Instruction String',    size=(300,20))
        self.paramLabel    = wx.StaticText(self, 1, paramName, size=(150,20))
        self.repsLabel     = wx.StaticText(self, 1, 'Repetitions',           size=( 60,20))
        label_sizer.Add(self.hRBLabel,      0, wx.ALL|wx.EXPAND, 5)
        label_sizer.Add(self.devNameLabel,  0, wx.ALL|wx.EXPAND, 5)
        label_sizer.Add(self.instNameLabel, 0, wx.ALL|wx.EXPAND, 5)
        label_sizer.Add(self.paramLabel,    0, wx.ALL|wx.EXPAND, 5)
        label_sizer.Add(self.repsLabel,     0, wx.ALL|wx.EXPAND, 5)

        macro_sizer.Add(label_sizer, 0, wx.ALL|wx.EXPAND, 0)
        macro_sizer.Add(input_sizer, 0, wx.ALL|wx.EXPAND, 0)

        self.SetSizerAndFit(macro_sizer)

class macroGeneralPanel(scrolled.ScrolledPanel):

    def __init__(self, parent, recorder):
        scrolled.ScrolledPanel.__init__(self, parent)

        self.recorder = recorder

        self.macroPanelList  = []
        self.horizMacroSizer = []
        self.macroCtrlPanel  = macroCtrlSubPanel(self)

        self.page_sizer      = wx.BoxSizer(wx.VERTICAL)
        self.page_sizer.Add(self.macroCtrlPanel,0,wx.ALL,1)
        self.Bind(wx.EVT_BUTTON, self.onPlay,  self.macroCtrlPanel.bmapBtnPlay)
        self.Bind(wx.EVT_BUTTON, self.onPause, self.macroCtrlPanel.bmapBtnPause)
        self.page_sizer.Add(wx.StaticLine(self), 0, wx.ALL | wx.EXPAND, 1)


        self.macroList_sizer = wx.GridBagSizer(hgap=1, vgap=1)
        self.page_sizer.Add(self.macroList_sizer, 1, wx.EXPAND|wx.ALL, 10)

        self.SetSizerAndFit(self.page_sizer)
        
        self.refresh()
        pub.subscribe(self.refresh, 'MacroPanelRefresh')
        
    def refresh(self):
        print("Refreshing Macro List")
        
        self.macroList_sizer.Clear(delete_windows = True)
        
        self.macroPanelList = []
        self.horizMacroSizer = []
        
        self.cmdListSplit = self.recorder.get_macros()
        
        numInstr = len(self.cmdListSplit)
        cbList   = [str(i) for i in range(1,numInstr+1)]
        counter = 0
        for cmd in self.cmdListSplit:
            devName    = cmd[0]
            instName   = cmd[1]
            paramValue = cmd[2]["msg"]["params"][2]
            paramInput = cmd[2]["msg"]["param_name"]
            depth = cmd[3]["depth"]
            reps = cmd[3]["repeat"]
            self.macroPanelList.append(macroEntry(self, cbList, devName, instName, paramValue, paramInput, depth, reps))
            self.horizMacroSizer.append(wx.BoxSizer(wx.HORIZONTAL))
            counter = counter + 1
            self.horizMacroSizer[counter - 1].Add(self.macroPanelList[counter - 1], 0, wx.ALL, 0)
            self.macroList_sizer.Add(self.horizMacroSizer[counter - 1], pos = (counter * 1,0), flag = wx.ALL, border = 5)

            self.Bind(wx.EVT_COMBOBOX, self.tabMacro,  self.macroPanelList[counter - 1].hierarchyCB)
            self.Bind(wx.EVT_TEXT,     self.paramMacro, self.macroPanelList[counter - 1].paramInput)
            self.Bind(wx.EVT_TEXT,     self.repsMacro, self.macroPanelList[counter - 1].reps)
        
        self.reTabMacros() # Needs to be called after SetSizerAndFit (never before)
        
    def paramMacro(self, event):
        # Don't update if the repeats box is now empty
        if not event.GetString(): return
        for panel, cmd in zip(self.macroPanelList, self.cmdListSplit):
            if panel.paramInput == event.GetEventObject():
                print(event.GetEventObject().GetParent())
                cmd[2]["msg"]["params"][2] = event.GetString()
                break

        self.updateMacroList()

    def repsMacro(self, event):
        # Don't update if the repeats box is now empty
        if not event.GetString(): return
        for panel, cmd in zip(self.macroPanelList, self.cmdListSplit):
            if panel.reps == event.GetEventObject():
                cmd[3]["repeat"] = int(event.GetString())
                break

        self.updateMacroList()

    # It's possible this will be slow with a lot of macros, it can be adjusted to only update changed macros at that point
    def tabMacro(self, event):
        for panel, cmd in zip(self.macroPanelList, self.cmdListSplit):
            if panel.hierarchyCB == event.GetEventObject():
                cmd[3]["depth"] = int(event.GetString())
                break
        
        self.reTabMacros()
        self.updateMacroList()
        
    def reTabMacros(self):
        for panel, sizer, cmd in zip(self.macroPanelList, self.horizMacroSizer, self.cmdListSplit):
            tabSpace = 40 * (cmd[3]["depth"] - 1)
            while not sizer.IsEmpty():
                sizer.Remove(0)
            sizer.AddSpacer(tabSpace)
            sizer.Add(panel, 0, wx.ALL, 0)
            # panel.SetBackgroundColour(self.getRGBfromI(128128128))
        
        self.GetSizer().Layout()

    def updateMacroList(self):
        self.recorder.set_macros(self.cmdListSplit)

    def onPlay(self,event):
        pub.sendMessage('RecorderPlay')

    def onPause(self,event):
        pub.sendMessage('RecorderPause')

    def getRGBfromI(self,RGBint):
        blue = RGBint & 255
        green = (RGBint >> 8) & 255
        red = (RGBint >> 16) & 255
        return red, green, blue

