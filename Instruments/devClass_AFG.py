from Instruments.devGlobalFunctions import devGlobal

class AFGClass(devGlobal):
    # Human readable name for the gui, note: Needs to be unique
    name = "AFG"
    def __init__(self, *args):
        devGlobal.__init__(self, *args)

        self.func_list  = self.func_list + [
                           self.Ch1OnOff,
                           self.Ch2OnOff,
                           self.SyncChannels,
                           self.Ch1TrigIntExt,
                           self.Ch2TrigIntExt,
                           self.Ch1setWaitTime,
                           self.Ch2setWaitTime,
                           self.Ch1Ena10MExtRef,
                           self.Ch2Ena10MExtRef
                          ]
        self.label_list = self.label_list + [
                           'Ch1 Output\nOn/Off',         #1
                           'Ch2 Output\nOn/Off',         #2
                           'Sync\nCh1 and Ch2',          #3
                           'Ch1 Trigger\nInt/Ext',       #4
                           'Ch2 Trigger\nInt/Ext',       #5
                           'Ch1 Set\nWait Time',         #6
                           'Ch2 Set\nWait Time',         #7
                           'Ch1 Enable\n10MHz Ext Ref',  #8
                           'Ch2 Enable\n10MHz Ext Ref'   #9
                          ]

    def Ch1OnOff(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Ch1 Output to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch2OnOff(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Ch2 Output to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def SyncChannels(self, event):
        StringInit = "Sync Ch1 and Ch2 on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch1TrigIntExt(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Ch1 Trigger to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch2TrigIntExt(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Ch2 Trigger to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch1setWaitTime(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Ch1 Wait Time to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch2setWaitTime(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Ch2 Wait Time to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch1Ena10MExtRef(self, event):
        StringInit = "Enable Ch1 10 MHz External Reference on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch2Ena10MExtRef(self, event):
        StringInit = "Enable Ch2 10 MHz External Reference on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

# IMPORTANT Don't forget this line (and remember to use the class name above)
instrument = AFGClass

