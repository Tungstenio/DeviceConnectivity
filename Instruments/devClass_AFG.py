from Instruments.devGlobalFunctions import devGlobal

class AFGClass(devGlobal):
    # Human readable name for the gui, note: Needs to be unique
    name = "AFG"
    def __init__(self, *args):
        devGlobal.__init__(self, *args)

        self.register(self.Ch1Off, 'Ch1 Output\nOff')
        self.register(self.Ch1On, 'Ch1 Output\nOn')
        self.register(self.Ch1Sinusoid, 'Ch1 Waveform\nSinusoidal')
        self.register(self.Ch1Frequency, 'Ch1 Frequency\nSet', parameters=["Frequency [Hz]"])

    def Ch1Off(self, msg):
        cmd_string = "Turns channel 1 OFF on "
        self.write(":OUTput1:STAte OFF")
        self.printOut(cmd_string)

    def Ch1On(self, msg):
        cmd_string = "Turns channel 1 ON on "
        self.write(":OUTput1:STAte ON")
        self.printOut(cmd_string)

    def Ch1Sinusoid(self, msg):
        cmd_string = "Sets sinusoidal waveform on channel 1 on "
        self.write(":SOURce1:FUNCtion:SHAPe SINusoid")
        self.printOut(cmd_string)

    def Ch1Frequency(self, msg):
        param = msg['params']
        cmd_string = "Sets Channel 1 operating frequency on "
        test_string = ":SOURce1:FREQuency:FIXed {0}".format(param[2])
        self.write(test_string)
        self.printOut(cmd_string)

instrument = AFGClass

