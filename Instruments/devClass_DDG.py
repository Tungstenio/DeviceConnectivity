from Instruments.devGlobalFunctions import devGlobal

from wx.lib.pubsub import pub

class DDGClass(devGlobal):
    # Human readable name for the gui, note: Needs to be unique
    name = "DDG"
    def __init__(self, *args):
        devGlobal.__init__(self, *args)

        self.register(self.SetDelayChCh, 'Set Delay\nChX-ChY')
        self.register(self.SetAmpCh, 'Set Output\nAmplitude', parameters = ["Voltage Division"])
        self.register(self.SetTriggerLvl, 'Set Trigger\nLevel', parameters = ["Trigger Level"])


    def SetDelayChCh(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Delay between Ch" + param[0] + " and Ch" + param[1] + " to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def SetAmpCh(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Amplitude of Ch" + param[0] + " to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def SetTriggerLvl(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Trigger Level to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)
                
# IMPORTANT Don't forget this line (and remember to use the class name above)
instrument = DDGClass

