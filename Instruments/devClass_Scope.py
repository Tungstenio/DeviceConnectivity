from Instruments.devGlobalFunctions import devGlobal

from wx.lib.pubsub import pub

class ScopeClass(devGlobal):
    # Human readable name for the gui, note: Needs to be unique
    name = "Scope"
    def __init__(self, *args):
        devGlobal.__init__(self, *args)

        self.runStop = 0
        self.write(":STOP")

        # Register functions for use in the interface
        self.register(self.RunStop, 'Run\nStop')
        self.register(self.SetVoltDiv, 'Set Voltage\nDivision (V)', parameters = ["Voltage Division"])
        self.register(self.SetTimeDiv, 'Set Time\nDivision (μs)', parameters = ["Time Division"])

    def RunStop(self, msg):
        if self.runStop == 0:
            self.runStop = 1
            self.write(":RUN")
        else:
            self.runStop = 0
            self.write(":STOP")
        cmd_string = "Sets the Scope to Run/Stop on "
        self.printOut(cmd_string)

    def SetVoltDiv(self, msg):
        param = msg['params']
        cmd_string = f"Sets Volt Division of Ch {param[0]} to {param[2]} V on "
        self.write(":CHAN{0}:SCAL {1}".format(param[0], param[2]))
        self.query(":CHAN{0}:SCAL?".format(param[0]))
        self.printOut(cmd_string)

    def SetTimeDiv(self, msg):
        param = msg['params']
        cmd_string = f"Sets Time Division to {param[2]} μs on "
        self.write(":TIM:MODE MAIN")
        self.write(":TIM:SCAL {0:e}".format(float(param[2]) * 10**(-6)))
        self.query(":TIM:SCAL?")
        self.printOut(cmd_string)

# IMPORTANT Don't forget this line (and remember to use the class name above)
instrument = ScopeClass

