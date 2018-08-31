import wx        # Library used for the interface components
import visa      # Library for device interfacing. In this case, GPIB access
import saveSession
from threading import Thread

from Instruments import instrument_names

import os
from wx.lib.pubsub import pub

import tkinter
from tkinter import filedialog

ID_DEVICE_FOUND = wx.NewId()
ID_DEVICE_NOT_FOUND = wx.NewId()

def getDeviceInfo(rm, address):
    entry = ''
    device = {}
    try:
        inst = rm.open_resource(address)
        try:
            nameInst = inst.query("*IDN?")
            # remove newlines
            nameInst = nameInst.replace('\n', ' ')
            entry = f"Model: {nameInst} Address: {address}"
            device = {"idn": nameInst, "address": address}

            inst.close()
        except Exception as e:
            print(e)
            inst.close()
    except Exception as e:
        print(e)
        wx.MessageDialog(None, f"Could not open device at address {address}").ShowModal()
        
    return entry, device

class btnIntroPanel(wx.Panel):

    def __init__(self, parent, devNameList):
        wx.Panel.__init__(self,parent)

        btnWidth  = 150
        btnHeight = 40

        self.button = []
        button_sizer  = wx.BoxSizer(wx.VERTICAL)
        for i in range(len(devNameList)):
            self.button.append(wx.Button(self, label = devNameList[i], size = (btnWidth, btnHeight)))
            button_sizer.Add(self.button[i],      0, wx.ALL, 1)
            button_sizer.Add(wx.StaticLine(self), 0, wx.ALL, 1)

        #==============================================================================================================================================================
        # Every interface requires flavour text that allows the user to use it more easily. These flavour texts can come as
        # "input/output" text slots or "labels"
        self.txtAssignResult = wx.TextCtrl(self,   size = ( 390, 60), style = wx.TE_MULTILINE)
        button_sizer.Add(self.txtAssignResult, 0, wx.ALL, 5)
        button_sizer.Add(wx.StaticLine(self),  0, wx.ALL|wx.EXPAND, 5)

        self.buttonClear = wx.Button(self,      label = "& Clear Assignments", size = (200,60))
        self.buttonDone  = wx.Button(self,      label = "& Done!",             size = (200,60))

        horizSizerClearDone = wx.BoxSizer(wx.HORIZONTAL)
        horizSizerClearDone.Add(self.buttonDone,  0, wx.ALL, 0)
        horizSizerClearDone.Add(self.buttonClear, 0, wx.ALL, 0)
        button_sizer.Add(horizSizerClearDone,     0, wx.ALL, 5)
        button_sizer.Add(wx.StaticLine(self),     0, wx.ALL|wx.EXPAND, 5)
        #==============================================================================================================================================================

        # create a normal bitmap button
        bmpSave = wx.Bitmap("saveIcon.png", wx.BITMAP_TYPE_ANY)
        bmpOpen = wx.Bitmap("openIcon.png", wx.BITMAP_TYPE_ANY)
        bmpRefr = wx.Bitmap("refrIcon.png", wx.BITMAP_TYPE_ANY)
        self.bmapBtnSave = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmpSave, size=(bmpSave.GetWidth()+10, bmpSave.GetHeight()+10))
        self.bmapBtnOpen = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmpOpen, size=(bmpSave.GetWidth()+10, bmpSave.GetHeight()+10))
        self.bmapBtnRefr = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmpRefr, size=(bmpSave.GetWidth()+10, bmpSave.GetHeight()+10))
        genHorizSizer = wx.BoxSizer(wx.HORIZONTAL)
        genHorizSizer.Add(self.bmapBtnSave,0,wx.ALL,1)
        genHorizSizer.Add(self.bmapBtnOpen,0,wx.ALL,1)
        genHorizSizer.Add(self.bmapBtnRefr,0,wx.ALL,1)

        # self.txtFileName = wx.TextCtrl(self, size = ( 390, 60))

        button_sizer.Add(genHorizSizer,   0,wx.ALL,1)
        # button_sizer.Add(self.txtFileName,0,wx.ALL,1)

        # button_sizer.Add(wx.StaticLine(self), 0, wx.ALL | wx.EXPAND, 5)
        # self.staticAssign = wx.StaticText(self, 1, "Macro Setup:", size=(150, 20))
        # button_sizer.Add(self.staticAssign, 0, wx.CENTER, 0)

        # bmpMacroOpen = wx.Bitmap("openIcon.png", wx.BITMAP_TYPE_ANY)
        # bmpMacroRefr = wx.Bitmap("refrIcon.png", wx.BITMAP_TYPE_ANY)
        # self.bmapMacroBtnOpen = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmpMacroOpen,
                                           # size=(bmpMacroOpen.GetWidth() + 10, bmpMacroOpen.GetHeight() + 10))
        # self.bmapMacroBtnRefr = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmpMacroRefr,
                                           # size=(bmpMacroOpen.GetWidth() + 10, bmpMacroOpen.GetHeight() + 10))
        # genMacroHorizSizer = wx.BoxSizer(wx.HORIZONTAL)
        # genMacroHorizSizer.Add(self.bmapMacroBtnOpen, 0, wx.ALL, 1)
        # genMacroHorizSizer.Add(self.bmapMacroBtnRefr, 0, wx.ALL, 1)

        # button_sizer.Add(genMacroHorizSizer)

        self.SetSizerAndFit(button_sizer)

class listIntroPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self,parent)

        list_sizer    = wx.BoxSizer(wx.VERTICAL)

        self.onlyFiles = []
        self.foundDevices = {}

        list_sizer.Add(wx.StaticLine(self),   0, wx.ALL|wx.EXPAND, 5)
        self.staticDevices = wx.StaticText(self,1,"Devices Found:", size=(150,20))
        list_sizer.Add(self.staticDevices,    0, wx.CENTER, 0)
        self.listFiles = wx.ListBox(self, size = (400,400), choices = ["Looking for devices..."], style = wx.LB_SINGLE)
        list_sizer.Add(self.listFiles,        0, wx.ALL, 5)
        self.btnAddress = wx.Button(self, label = "Open by Address")
        list_sizer.Add(self.btnAddress,       0, wx.CENTER | wx.EXPAND | wx.LEFT | wx.RIGHT, 100)
        self.Bind(wx.EVT_BUTTON, self.loadAddress, self.btnAddress)
        
        self.SetSizerAndFit(list_sizer)
        
        self.rm = visa.ResourceManager()
        t = Thread(target=self.findDevices)
        t.start()

        
    def findDevices(self):
        for i in self.rm.list_resources():
            entry, device = getDeviceInfo(self.rm, i)
            if entry:
                self.onlyFiles.append(entry)
                self.foundDevices[entry] = device
                self.listFiles.Insert(entry, self.listFiles.GetCount() - 1)
                
        self.listFiles.Delete(self.listFiles.GetCount() - 1)
        
    
    def loadAddress(self, event = None):
        with customAddressPopup(self) as addrPop:
            if addrPop.ShowModal() == wx.ID_OK:
                address = addrPop.address.GetLineText(0)
                entry, device = getDeviceInfo(self.rm, address)
                if entry:
                    self.onlyFiles.append(entry)
                    self.foundDevices[entry] = device
                    self.listFiles.Insert(entry, self.listFiles.GetCount() - 1)

class assignIntroPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self,parent)

        assign_sizer  = wx.BoxSizer(wx.VERTICAL)
        
        self.assignedDevices = {}

        assign_sizer.Add(wx.StaticLine(self),   0, wx.ALL|wx.EXPAND, 5)
        self.staticAssign = wx.StaticText(self,1,"Assignments:", size=(150,20))
        assign_sizer.Add(self.staticAssign,   0, wx.CENTER, 0)
        self.listAssignment = wx.ListBox(self, size = (400,400), choices = [], style = wx.LB_SINGLE)
        assign_sizer.Add(self.listAssignment, 0, wx.ALL, 5)

        self.SetSizerAndFit(assign_sizer)
        
class missingDevicePopup(wx.Dialog):
    def __init__(self, parent, error, availableDevices):
        wx.Dialog.__init__(self, parent)
        self.Centre(direction = wx.HORIZONTAL)
        
        self.errorMes = wx.StaticText(self, 1, "{0}\nPlease select a corresponding device from the list below\nIf you can't see it check to ensure that it's correctly connected".format(error))
        self.listHeader = wx.StaticText(self, 1, "Available devices")
        self.listFiles = wx.ListBox(self, size = (400,400), choices = availableDevices, style = wx.LB_SINGLE)
        self.buttonDone  = wx.Button(self, id = ID_DEVICE_FOUND, label = "Done")
        self.buttonNotDone  = wx.Button(self, id = ID_DEVICE_NOT_FOUND, label = "I don't see it")
        self.Bind(wx.EVT_BUTTON, self.not_found,  self.buttonNotDone)
        
        self.SetAffirmativeId(ID_DEVICE_FOUND)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.errorMes, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.listHeader, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.listFiles, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.buttonDone, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.buttonNotDone, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizerAndFit(main_sizer)
        
    def not_found(self, event):
        self.EndModal(ID_DEVICE_NOT_FOUND)
        
class customAddressPopup(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent)
        self.Centre()
        
        self.listHeader = wx.StaticText(self, 1, "Device Address: ")
        self.address = wx.TextCtrl(self, size = (400,20))
        self.buttonDone  = wx.Button(self, id = wx.ID_OK, label = "Done")
        self.buttonNotDone  = wx.Button(self, id = wx.ID_CANCEL, label = "No thanks")
        self.Bind(wx.EVT_BUTTON, self.onDone,  self.buttonDone)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.listHeader, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.address, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.buttonDone, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.buttonNotDone, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizerAndFit(main_sizer)
        
    def onDone(self, event):
        if self.address.GetLineLength(0) == 0:
            wx.MessageDialog(self, 'Please input an address or press "No thanks"').ShowModal()
        else:
            self.EndModal(wx.ID_OK)
        

class mainIntroPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self,parent)

        self.openedResList   = []

        self.devInfoList     = []
        self.devNameList     = []
        self.macros = []
        self.devNameListInit = instrument_names()

        self.btnPanel    = btnIntroPanel(self, self.devNameListInit)
        self.listPanel   = listIntroPanel(self)
        self.assignPanel = assignIntroPanel(self)

        self.configPath = os.path.abspath("Config Files")
        self.macroPath  = os.path.abspath("macros")
        self.autosaveFile = os.path.join(self.macroPath, 'lastsession.ses')
        self.macros = []

        # ==============================================================================================================
        # Binding buttons to their respective functions is extremely important. Once again, even though the names are
        # arbitrary, it is good practice to name buttons and functions with similar names if they are to be bound together.
        for i in range(len(self.btnPanel.button)):
            self.Bind(wx.EVT_BUTTON, self.onDevBtn, self.btnPanel.button[i])

        self.Bind(wx.EVT_BUTTON, self.onDone,  self.btnPanel.buttonDone)
        self.Bind(wx.EVT_BUTTON, self.onClear, self.btnPanel.buttonClear)

        self.Bind(wx.EVT_BUTTON, self.onSave, self.btnPanel.bmapBtnSave)
        self.Bind(wx.EVT_BUTTON, self.onOpen, self.btnPanel.bmapBtnOpen)
        self.Bind(wx.EVT_BUTTON, self.onRefr, self.btnPanel.bmapBtnRefr)

        # self.Bind(wx.EVT_BUTTON, self.onOpenMacro, self.btnPanel.bmapMacroBtnOpen)
        # self.Bind(wx.EVT_BUTTON, self.onRefrMacro, self.btnPanel.bmapMacroBtnRefr)
        # ==============================================================================================================

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.btnPanel,    0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.listPanel,   0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.assignPanel, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizerAndFit(main_sizer)

    def onDevBtn(self, event):
        label = event.GetEventObject().GetLabel()

        selec = self.listPanel.listFiles.GetSelection()
        if selec < 0:
            stringResult = "Please select a device from the panel on the right before assigning a name"
            self.btnPanel.txtAssignResult.SetValue(stringResult)
            
        stringName    = self.listPanel.listFiles.GetString(selec)
        
        device = self.listPanel.foundDevices.get(stringName, False)
        
        if device == False:
            raise Exception(f"Device {stringName} not found in listPanel.foundDevices, this should be impossible")

        self.devInfoList.append(device)
        self.devNameList.append(label)

        stringResult = f"Device with IDN {device['idn']} assigned to a {label} Unit"
        self.btnPanel.txtAssignResult.SetValue(stringResult)

        self.listPanel.listFiles.Delete(selec)
        del self.listPanel.foundDevices[stringName]
        self.assignPanel.assignedDevices[stringName] = device
        devIndex = self.devNameList.index(label)
        stringAssign = "{0} {1} --> {2}".format(label, devIndex, stringName)
        self.assignPanel.listAssignment.InsertItems([stringAssign], 0)

    def onDone(self, event):
        mixedList = [self.devInfoList, self.devNameList]

        self.openedResList = []

        for i in self.devInfoList:
            self.openedResList.append(self.listPanel.rm.open_resource(i["address"]))

        mixedList.append(self.openedResList)

        # Write the autosave file
        saveSession.saveSession(self.devInfoList, self.devNameList, self.macros, filename = self.autosaveFile)

        pub.sendMessage('RecorderLoad', msg = (self.devInfoList, self.devNameList, self.macros))
        pub.sendMessage('AssigningDone', msg = mixedList)
        pub.sendMessage('MacroOpen', msg={"macros": self.macros, "devInfo": self.devInfoList, "devName": self.devNameList})

    def onClear(self, event):
        a = self.listPanel.listFiles.GetCount()
        b = self.assignPanel.listAssignment.GetCount()

        for i in range(a):
            self.listPanel.listFiles.Delete(0)
        for i in range(b):
            self.assignPanel.listAssignment.Delete(0)
            
        self.listPanel.foundDevices = {}
        self.listPanel.foundDevices = self.assignPanel.assignedDevices
        self.assignPanel.assignedDevices = {}

        self.devInfoList = []
        self.devNameList = []

        try:
            self.listPanel.listFiles.InsertItems(self.listPanel.onlyFiles, 0)
        except:
            print("No Devices Connected.")

        stringResult = "All assignments cleared"
        self.btnPanel.txtAssignResult.SetValue(stringResult)

        pub.sendMessage('AssignCleared', msg=[])

    def onSave(self, event):
        # UserName = self.btnPanel.txtFileName.GetValue()
        saveSession.saveSession(self.devInfoList, self.devNameList)
        
    def loadPrevious(self):
        found = False
        
        newInfoList = []
        newNameList = []
        
        for devInfo, devName in zip(self.devInfoList, self.devNameList):
            found = False
            count = 0
            for panelName, device in self.listPanel.foundDevices.items():
                if devInfo["idn"] == device["idn"]:
                    found = True
                    self.listPanel.listFiles.Delete(count)
                    del self.listPanel.foundDevices[panelName]
                    self.assignPanel.assignedDevices[panelName] = device
                    devIndex = self.devNameList.index(devName)
                    stringAssign = "{0} {1} --> {2}".format(devName, devIndex, panelName)
                    self.assignPanel.listAssignment.InsertItems([stringAssign], 0)
                    newInfoList.append(device)
                    newNameList.append(devName)
                    break # Not necessary but we might as well quit early
                count += 1
            
            if not found:
                errorMes = f"Could not find {devName}\nIDN: {devInfo['idn']}\nAddress: {devInfo['address']}"
                bail = False
                with missingDevicePopup(self, errorMes, self.listPanel.listFiles.GetItems()) as pop:
                    returnId = pop.ShowModal()
                    if returnId == ID_DEVICE_FOUND: # Great, Add the device
                        selec = pop.listFiles.GetSelection()
                        if selec < 0:
                            bail = True
                        stringName = pop.listFiles.GetString(selec)
                        
                        device = self.listPanel.foundDevices.get(stringName, False)
        
                        if device == False:
                            raise Exception(f"Device {stringName} not found in listPanel.foundDevices, this should be impossible")

                        self.listPanel.listFiles.Delete(selec)
                        del self.listPanel.foundDevices[stringName]
                        self.assignPanel.assignedDevices[stringName] = device
                        devIndex = self.devNameList.index(devName)
                        stringAssign = "{0} {1} --> {2}".format(devName, devIndex, stringName)
                        self.assignPanel.listAssignment.InsertItems([stringAssign], 0)
                        
                        newInfoList.append(device)
                        newNameList.append(devName)
                    elif returnId == ID_DEVICE_NOT_FOUND: # Let's give a custom address
                        with customAddressPopup(self) as addrPop:
                            if addrPop.ShowModal() == wx.ID_OK:
                                address = addrPop.address.GetLineText(0)
                                entry, device = getDeviceInfo(self.listPanel.rm, address)
                                stringAssign = "{0} {1} --> {2}".format(devName, 0, entry)
                                self.assignPanel.listAssignment.InsertItems([stringAssign], 0)
                                newInfoList.append(device)
                                newNameList.append(devName)
                            else: # User doesn't have an address, bail early
                                bail = True
                    else: # Bail early
                        bail = True
                
                if bail: # User wants to skip this device
                    print("Skipping!")
                
        self.devInfoList = newInfoList
        self.devNameList = newNameList
                
        stringResult = "Finished loading previous assignment"
        self.btnPanel.txtAssignResult.SetValue(stringResult)

    def onOpen(self, event):
        tkinter.Tk().withdraw() # Close the root window
        self.devInfoList, self.devNameList, self.macros = saveSession.loadSession()

        self.loadPrevious()
        
        self.onDone(event)

    def onRefr(self, event):
        self.devInfoList, self.devNameList, self.macros = saveSession.loadSession(filename = self.autosaveFile)

        self.loadPrevious()
        
        mixedList = [self.devInfoList, self.devNameList]

        for i in self.devInfoList:
            self.openedResList.append(self.listPanel.rm.open_resource(i["address"]))

        mixedList.append(self.openedResList)

        pub.sendMessage('RecorderLoad', msg = (self.devInfoList, self.devNameList, self.macros))
        pub.sendMessage('AssigningDone', msg = mixedList)
        pub.sendMessage('MacroOpen', msg={"macros": self.macros, "devInfo": self.devInfoList, "devName": self.devNameList})

    def onOpenMacro(self, event):
        self.onOpen(event)

        pub.sendMessage('MacroOpen', msg={"macros": self.macros})

    def onRefrMacro(self, event):
        self.onRefr(event)

        pub.sendMessage('MacroOpen', msg={"macros": self.macros, "devInfo": self.devInfoList, "devName": self.devNameList})

