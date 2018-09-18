from Instruments.devGlobalFunctions import devGlobal

from wx.lib.pubsub import pub

class DDGClass(devGlobal):
    # Human readable name for the gui, note: Needs to be unique
    name = "DDG"
    def __init__(self, *args):
        devGlobal.__init__(self, *args)

        self.label_list = self.label_list + [
            ('Set Delay\nChX-ChY', self.SetDelayChCh, ""),
            ('Set Output\nAmplitude', self.SetAmpCh, "Voltage Division"),  # 1
            ('Set Trigger\nLevel', self.SetTriggerLvl, "Trigger Level")
        ]

        # Theoretical api instead of using label list above
        # self.register(self.RunStop, 'Run\nStop')
        # self.register(self.SetVoltDiv, 'Set Voltage\nDivision (V)', name = "Voltage Division", sc = True, dc = False, parameter = True)
        # self.register(self.SetVoltDiv, 'Set Time\nDivision (μs)', name = "Time Division", parameter = True)

        for label, function, *_ in self.label_list:
            pub.subscribe(function, self.createTopic(label))

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

