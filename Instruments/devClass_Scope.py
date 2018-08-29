from Instruments.devGlobalFunctions import devGlobal

from wx.lib.pubsub import pub

class ScopeClass(devGlobal):
    # Human readable name for the gui, note: Needs to be unique
    name = "Scope"
    def __init__(self, *args):
        devGlobal.__init__(self, *args)

        self.runStop = 0
        self.write(":STOP")

        self.label_list = self.label_list + [
                           ('Run\nStop',             self.RunStop,       ""),
                           ('Set Voltage\nDivision (V)', self.SetVoltDiv,    "Voltage Division"),  #1
                           ('Set Time\nDivision (μs)',    self.SetTimeDiv,    "Time Division"),  #2
                           ('Set Trigger\nLevel',    self.SetTriggerLvl, "Trigger Level"),  #3
                           ('Measure\nFrequency',    self.MeasFreq,      ""),  #4
                           ('Measure\nVpp',          self.MeasVpp,       "")  #5
                           ]
                           
        # Theoretical api instead of using label list above
        # self.register(self.RunStop, 'Run\nStop')
        # self.register(self.SetVoltDiv, 'Set Voltage\nDivision (V)', name = "Voltage Division", sc = True, dc = False, parameter = True)
        # self.register(self.SetVoltDiv, 'Set Time\nDivision (μs)', name = "Time Division", parameter = True)

        for label, function, *_ in self.label_list:
            pub.subscribe(function, self.createTopic(label))

    def RunStop(self, msg):
        if self.runStop == 0:
            self.runStop = 1
            self.write(":RUN")
        else:
            self.runStop = 0
            self.write(":STOP")
        cmdString = "Sets the Scope to Run/Stop on "
        self.printOut(cmdString)

    def SetVoltDiv(self, msg):
        param = msg['params']
        cmdString = f"Sets Volt Division of Ch {param[0]} to {param[2]} V on "
        self.write(":CHAN{0}:SCAL {1}".format(param[0], param[2]))
        self.query(":CHAN{0}:SCAL?".format(param[0]))
        self.printOut(cmdString)

    def SetTimeDiv(self, msg):
        param = msg['params']
        cmdString = f"Sets Time Division to {param[2]} μs on "
        self.write(":TIM:MODE MAIN")
        self.write(":TIM:SCAL {0:e}".format(float(param[2]) * 10**(-6)))
        self.query(":TIM:SCAL?")
        self.printOut(cmdString)

    def SetTriggerLvl(self, msg):
        param = self.GetParamVector()
        StringInit = "Sets Trigger Level of Ch" + param[0] + " to " + param[2] + "on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def MeasFreq(self, msg):
        param = self.GetParamVector()
        StringInit = "Measures the Frequency of Waveform of Ch" + param[0] + "on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def MeasVpp(self, msg):
        param = self.GetParamVector()
        StringInit = "Measures the Vpp of Waveform of Ch" + param[0] + "on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)
                


# IMPORTANT Don't forget this line (and remember to use the class name above)
instrument = ScopeClass

