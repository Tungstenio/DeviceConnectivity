from Instruments.devGlobalFunctions import devGlobal

class LaserClass(devGlobal):
    # Human readable name for the gui, note: Needs to be unique
    name = "Laser"
    def __init__(self, *args):
        devGlobal.__init__(self, *args)

        self.func_list  = self.func_list + [
                           self.SetWL,
                           self.SetOutputPower,
                           self.OutputEna,
                           self.IsLocked,
                           self.IsStable,
                           ]
        self.label_list = self.label_list + [
                           'Set\nWavelength',         #1
                           'Set Output\nPower',       #2
                           'Output\n(En/Dis)able',    #3
                           'Laser\nLocked?',          #4
                           'Laser\nStable?',          #5
                           ]

    def SetWL(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Operating Wavelength to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def SetOutputPower(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Output Power to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def OutputEna(self, event):
        StringInit = "(En/Dis)ables Output on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def IsLocked(self, event):
        StringInit = "Checks if the device is locked on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def IsStable(self, event):
        StringInit = "Checks if the device is stable on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

# IMPORTANT Don't forget this line (and remember to use the class name above)
instrument = LaserClass

