from Instruments.devGlobalFunctions import devGlobal

class CounterClass(devGlobal):
    # Human readable name for the gui, note: Needs to be unique
    name = "Counter"
    def __init__(self, *args):
        devGlobal.__init__(self, *args)

        self.func_list  = self.func_list + [
                           self.Ch1GetCounts,
                           self.Ch2GetCounts,
                           self.Ch1SetInputImp,
                           self.Ch2SetInputImp,
                           self.Ch1InputThreshold,
                           self.Ch2InputThreshold,
                           self.Ch1setManualOrAutoTrigger,
                           self.Ch2setManualOrAutoTrigger,
                           self.dispCh1plusCh2,
                           self.dispCh1divCh2,
                           self.Ch1Pause,
                           self.Ch2Pause,
                           self.Ch1SetCountTime,
                           self.Ch2SetCountTime,
                           ]
        self.label_list = self.label_list + [
                           'Ch1 Get\nCounts',         #1
                           'Ch2 Get\nCounts',         #2
                           'Ch1 Set\nInput Imp',      #3
                           'Ch2 Set\nInput Imp',      #4
                           'Ch1 Set Input\nThresh',   #5
                           'Ch2 Set Input\nThresh',   #6
                           'Ch1 Man/Auto\nTrigger',   #7
                           'Ch2 Man/Auto\nTrigger',   #8
                           'Display\nCh1 + Ch2',      #9 
                           'Display\nCh1 / Ch2',      #10
                           'Ch1 Pause',               #11
                           'Ch2 Pause',               #12
                           'Ch1 Set\nCount Time',     #13
                           'Ch2 Set\nCount Time'      #14
                           ]

    def Ch1GetCounts(self, event):
        StringInit = "Get Counts Ch1 from "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch2GetCounts(self, event):
        StringInit = "Get Counts Ch2 from "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch1SetInputImp(self, event):
        param = self.GetParamVector()
        StringInit = "Set Ch1 Input Impedance to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch2SetInputImp(self, event):
        param = self.GetParamVector()
        StringInit = "Set Ch2 Input Impedance to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch1InputThreshold(self, event):
        param = self.GetParamVector()
        StringInit = "Set Ch1 Input Threshold to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch2InputThreshold(self, event):
        param = self.GetParamVector()
        StringInit = "Set Ch2 Input Threshold to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch1setManualOrAutoTrigger(self, event):
        param = self.GetParamVector()
        StringInit = "Set Ch1 Trigger to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch2setManualOrAutoTrigger(self, event):
        param = self.GetParamVector()
        StringInit = "Set Ch2 Trigger to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def dispCh1plusCh2(self, event):
        StringInit = "Get Ch1+Ch2 from "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def dispCh1divCh2(self, event):
        StringInit = "Get Ch1/Ch2 from "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch1Pause(self, event):
        StringInit = "Pause Ch1 Counts on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch2Pause(self, event):
        StringInit = "Pause Ch2 Counts on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch1SetCountTime(self, event):
        param = self.GetParamVector()
        StringInit = "Set Ch1 Count Time to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch2SetCountTime(self, event):
        param = self.GetParamVector()
        StringInit = "Set Ch2 Count Time to " + param[2] + "on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

# IMPORTANT Don't forget this line (and remember to use the class name above)
instrument = CounterClass

