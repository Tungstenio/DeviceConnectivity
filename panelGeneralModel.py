import math      # Library for some important (unusual) mathematical functions (ln, sin, etc..)

# The matplotlib and the following imports are necessary for generating the figure inside the interface
# They also allow manipulation of ploting functionalities
import matplotlib
matplotlib.use('WXAgg')
import numpy as np

# from devClass_Counter   import CounterClass
# from devClass_Scope     import ScopeClass
# from devClass_SuperFast import SuperFastClass
# from devClass_DDG       import DDGClass
# from devClass_TDC       import TDCClass
# from devClass_Laser     import LaserClass
# from devClass_AFG       import AFGClass
# from devClass_LockIn    import LockInClass

from Instruments import load_instruments

# This source code provides the class "wxMatplotLib" and its functionalities. Most important would be the
# "setData" function, which is used to update the graph with the new measurements and is called in "UpdateFig"
from UI_GRAPH import *

import wx.lib.scrolledpanel as scrolled
from operator import itemgetter

from wx.lib.pubsub import pub

class recordSubPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self,parent)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        bmpRecord = wx.Bitmap("recordIcon.png", wx.BITMAP_TYPE_ANY)
        bmpPause  = wx.Bitmap("pauseIcon.png", wx.BITMAP_TYPE_ANY)
        self.bmapBtnRecord = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmpRecord,
                                             size=(bmpPause.GetWidth() + 10, bmpPause.GetHeight() + 10))
        self.bmapBtnPause  = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmpPause,
                                             size=(bmpPause.GetWidth() + 10, bmpPause.GetHeight() + 10))

        button_sizer.Add(self.bmapBtnRecord,0,wx.ALIGN_RIGHT,1)
        button_sizer.Add(self.bmapBtnPause, 0,wx.ALIGN_RIGHT,1)

        self.SetSizerAndFit(button_sizer)

class generalSubBtnPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self,parent)

        button_sizer = wx.BoxSizer(wx.VERTICAL)

        btnWidth  = 90
        btnHeight = 40
        blankBtnLabel = "&Blank"

        #==============================================================================================================================================================
        # Buttons are created with labels, sizes, and positions. The names of the buttons are arbitrary but
        # it is a good practice to name them according to their function.
        ##Creating Buttons

        self.button = []
        rowSizer = wx.BoxSizer(wx.HORIZONTAL)
        rowCounter = 0
        buttonsInARow = 5
        buttonsInACol = 3
        for i in range(buttonsInARow*buttonsInACol):
            btnIndexCol = i%buttonsInARow + 1
            btnIndexRow = int(math.floor(i/buttonsInARow)) + 1
            self.button.append(wx.Button(self, label = blankBtnLabel + "\n(" + str(btnIndexRow) + "," + str(btnIndexCol) + ")", size = (btnWidth, btnHeight)))
            self.button[i].SetBackgroundColour("RED")
            rowSizer.Add(self.button[i], 0, wx.ALL, 1)

            if btnIndexCol == buttonsInARow:
                button_sizer.Add(wx.StaticLine(self), 0, wx.ALL, 1)
                button_sizer.Add(rowSizer,            0, wx.ALL, 0)
                rowSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.SetSizerAndFit(button_sizer)

class generalPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self,parent,style = wx.SUNKEN_BORDER)

        main_sizer    = wx.BoxSizer(wx.VERTICAL)

        self.btnPanel = generalSubBtnPanel(self)
        W,H           = self.btnPanel.GetSize()

        self.figBox = wxMatplotLib(self,( (W-90)/80.0,math.ceil(H/80.0) ))
        line        = wx.StaticLine(self)

        self.txtParamLbl1 = wx.StaticText(self, size = ( (W-20)/4, 20), label = "      Channel: " )
        self.txtParamLbl2 = wx.StaticText(self, size = ( (W-20)/4, 20), label = "      Channel: " )
        self.txtParamLbl3 = wx.StaticText(self, size = ( (W-20)/2, 20), label = "      Command Input Value: " )
        self.txtParamLbl4 = wx.StaticText(self, size = ( (W-20)/2, 20), label = " Command Output Value: " )
        paramLabelSizer   = wx.BoxSizer(wx.HORIZONTAL)
        paramLabelSizer.Add(self.txtParamLbl1,0,wx.ALL,1)
        paramLabelSizer.Add(self.txtParamLbl2,0,wx.ALL,1)
        paramLabelSizer.Add(self.txtParamLbl3,0,wx.ALL,1)

        self.txtParam1 = wx.TextCtrl(self, size = ( (W-20)/4, 20) )
        self.txtParam2 = wx.TextCtrl(self, size = ( (W-20)/4, 20) )
        self.txtParam3 = wx.TextCtrl(self, size = ( (W-20)/2, 20) )
        self.txtParam4 = wx.TextCtrl(self, size = ( (W-20)  , 40), style = wx.TE_MULTILINE|wx.TE_READONLY )
        paramSizer     = wx.BoxSizer(wx.HORIZONTAL)
        paramSizer.Add(self.txtParam1, 0, wx.ALL, 1)
        paramSizer.Add(self.txtParam2, 0, wx.ALL, 1)
        paramSizer.Add(self.txtParam3, 0, wx.ALL, 1)

        self.paramVector = []
        self.paramVector.append(self.txtParam1)
        self.paramVector.append(self.txtParam2)
        self.paramVector.append(self.txtParam3)
        
        self.output = self.txtParam4
        # self.paramVector.append(self.txtParam4)
        
        main_sizer.Add(self.btnPanel,     0, wx.LEFT,          1)
        main_sizer.Add(paramLabelSizer,   0, wx.ALL|wx.CENTER, 1)
        main_sizer.Add(paramSizer,        0, wx.ALL|wx.CENTER, 1)
        main_sizer.Add(self.txtParamLbl4, 0, wx.CENTER,        1)
        main_sizer.Add(self.txtParam4,    0, wx.ALL,           1)
        main_sizer.Add(line,              0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(self.figBox,       1, wx.ALL,           1)

        self.SetSizerAndFit(main_sizer)
        #==============================================================================================================================================================

    def UpdateFig(self, x, y):  #
        a = threading.Thread(target=self.figBox.setData(x, y, x_axis=None, y_axis=None, graph_type='Plot'))

class deviceGeneralPanel(scrolled.ScrolledPanel):

    def __init__(self, parent, devices):
        scrolled.ScrolledPanel.__init__(self, parent)

        pub.subscribe(self.PrintData, 'PrintData')

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.recPanel = recordSubPanel(self)
        main_sizer.Add(self.recPanel,0,wx.ALL,1)

        self.Bind(wx.EVT_BUTTON, self.onRec,   self.recPanel.bmapBtnRecord)
        self.Bind(wx.EVT_BUTTON, self.onPause, self.recPanel.bmapBtnPause)

        # Stores the information and name of each device in a tuple.
        # Then, sorts based on the name such that devices in the same class are
        # included together.
        deviceInfo  = []
        for i in range(len(devices[0])):
            deviceInfo.append([devices[0][i],devices[1][i],devices[2][i]])
        sortedDeviceInfo = sorted(deviceInfo, key=itemgetter(1))

        self.notebookList = []
        # List of added panels. Each entry holds the pointer to the added panel.
        self.panelList = []
        # List of Horizontal sizers in the general panel.
        horizSizerList = []
        # List of added devices. Each entry holds the pointer to the class.
        # The list is formed such that panel i in "self.panelList[i]" is associated to the
        # device class in "self.devClassPointer[i].
        self.devClassPointer = []

        # Maximum number of device panels per horizontal sizer.
        breakLineMax = 4
        # List containing the index where a linebreak occurred.
        breakLineVec = []
        # List with the class name of the added devices.
        devNameList  = []

        # Counter for the horizSizerList
        horizSizerCount   = 0
        # Counter for the self.panelList
        generalPanelCount = 0
        # Counter for the sortedDeviceInfo List
        addedDevs         = 0

        # Creates the first horizontal sizer and append it to the list of horizontal sizers.
        # Also, increment the horizontal sizer counter.
        horizSizerList.append(wx.BoxSizer(wx.HORIZONTAL))
        horizSizerCount = horizSizerCount + 1

        # Runs through all the devices in the sorted device information list.
        # The loop finishes when the number of added devices matches the length of the device list.
        # Inside the main loop, there is a secondary loop that adds devices in the same class together
        # and to the same horizontal sizer (except if there is a linebreak).
        #111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
        while addedDevs < len(sortedDeviceInfo):

            # Determines the number of devices within the class set by the current device.
            numPanelsCurrentDev = devices[1].count(sortedDeviceInfo[addedDevs][1])
            # Each new device class corresponds to a new breakline.
            breakLineVec.append(horizSizerCount-1)
            # Appends the device list to the device name list so that the labels can be set
            # when adding the horizontal sizers into the main sizer.
            devNameList.append(sortedDeviceInfo[addedDevs][1])

            #22222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222
            for i in range(numPanelsCurrentDev):
                # Appends a new general panel to the panel list and increments its respective counter.
                generalPanelCount += 1
                self.notebookList.append(wx.Notebook(self))
                self.panelList.append([])

                tabCount = 1
                self.panelList[generalPanelCount-1].append(generalPanel(self.notebookList[generalPanelCount-1]))
                self.notebookList[generalPanelCount-1].AddPage(self.panelList[generalPanelCount-1][tabCount-1], "P 1")

                # Append a new class to the class pointer list using the "self.findClass" function and
                # the device's label. Also, increment the respective counter.
                paramVec = self.panelList[generalPanelCount-1][tabCount-1].paramVector
                output = self.panelList[generalPanelCount-1][tabCount-1].output
                self.devClassPointer.append(self.findClass(sortedDeviceInfo[addedDevs][1], "GPIB", sortedDeviceInfo[addedDevs][0], paramVec, output, sortedDeviceInfo[addedDevs][2], generalPanelCount-1))
                addedDevs += 1

                # Loops through the functions of the new device class, changes the labels on the general
                # panel's buttons and binds buttons to device class functions.
                #333333333333333333333333333333333333333333333333
                # for j in range(btnLabelLength):
                device = self.devClassPointer[addedDevs-1]
                j = 0
                for label, _, *param in device.label_list:
                    if j%15 == 0 and j != 0:
                        j = 0
                        tabCount = tabCount + 1
                        self.panelList[generalPanelCount-1].append(generalPanel(self.notebookList[generalPanelCount-1]))
                        self.notebookList[generalPanelCount - 1].AddPage(self.panelList[generalPanelCount-1][tabCount-1], "P"+str(tabCount))

                    self.panelList[generalPanelCount-1][tabCount-1].btnPanel.button[j].SetLabel(label)
                    self.panelList[generalPanelCount-1][tabCount-1].btnPanel.button[j].SetBackgroundColour(wx.NullColour)

                    self.Bind(wx.EVT_BUTTON, self.publish(device, label, param), self.panelList[generalPanelCount-1][tabCount-1].btnPanel.button[j])
                    j += 1
                #333333333333333333333333333333333333333333333333

                for tab in self.devClassPointer[generalPanelCount-1].additionalPanels:
                    className, label = tab
                    tabCount += 1
                    self.panelList[generalPanelCount - 1].append(className(self.notebookList[generalPanelCount - 1],self.devClassPointer[addedDevs-1]))
                    self.notebookList[generalPanelCount - 1].AddPage(self.panelList[generalPanelCount - 1][tabCount - 1], label)

                # Checks if the number of added panels reached the maximum allowed per horizontal sizer.
                #333333333333333333333333333333333333333333333333
                if i != 0 and i % breakLineMax == 0:
                    # In case it did, add a new horizontal sizer and increment the counter.
                    horizSizerList.append(wx.BoxSizer(wx.HORIZONTAL))
                    horizSizerCount = horizSizerCount + 1
                #333333333333333333333333333333333333333333333333
                    
                # Adds the new general panel already associated to a device class to the horizontal sizer.
                horizSizerList[horizSizerCount-1].Add(self.notebookList[generalPanelCount-1],0,wx.ALL,1)
            #2222222222222222222222222222222222222222222222222222222222222222222222222222222222222
                
            horizSizerList.append(wx.BoxSizer(wx.HORIZONTAL))
            horizSizerCount = horizSizerCount+1
                
        #111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        # After all the devices have been added and associated to device classes, add the horizontal sizer to the main sizer.
        # This process must respect the line breaks where new device classes are being added and, also, cases where the number
        # of devices in a class saturated the maximum number of panels per horizontal sizer.
        breakLineCount = 0
        #111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
        for i in range(horizSizerCount):
            #22222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222
            if breakLineCount < len(breakLineVec):
                #333333333333333333333333333333333333333333333333
                if i == breakLineVec[breakLineCount]:
                    main_sizer.Add(wx.StaticLine(self),0,wx.ALL|wx.EXPAND,1)
                    breakLineCount = breakLineCount + 1

                    text = wx.StaticText(self, -1, "&"+devNameList[breakLineCount-1]+"s", size=(150,30))
                    font = wx.Font(14, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
                    text.SetFont(font)
                    main_sizer.Add(text,0,wx.CENTER,1)
                #333333333333333333333333333333333333333333333333

            #22222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222
                    
            main_sizer.Add(horizSizerList[i],0,wx.ALL,1)
        #111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
        
        self.SetSizerAndFit(main_sizer)
        self.SetupScrolling()

    def findClass(self, devName, comType, devInfo, paramVec, output, devCommPointer, panelId):
    # def findClass(self, devName, comType, devAddr, paramVec, devCommPointer, panelId):
        instruments = load_instruments()

        inst = instruments.get(devName, False)

        if inst:
            return inst(comType, devInfo, paramVec, output, devCommPointer, panelId)
        else: # Should never reach this case
            raise Exception("It looks like {0} was deleted, please double check the Instrument files and restart this program".format(inst))

    def PrintData(self, msg):

        y   = msg[1].tolist()
        xNP = np.linspace(1,len(y),len(y))
        x   = xNP.tolist()

        self.panelList[msg[0]].UpdateFig(x,y)

    def publish(self, device, label, param):
        def onClick(event):
            # In the future you could just pass a specific ID or something
            # That ties this to a specific class
            # TODO: Note the above function "findClass"
            param_name, *used = param
            params = device.GetParamVector()
            if param_name and not any(params):
                wx.MessageDialog(self, f"{label} requires parameters!").ShowModal()
            else:
                msg = {"params": params, "param_name": param_name}
                pub.sendMessage(device.createTopic(label), msg = msg)

        return onClick

    def onRec(self,event):
        print("Record Pressed")
        pub.sendMessage('RecorderStart',msg = {})

    def onPause(self,event):
        pub.sendMessage('RecorderStop',msg = {})