import re
import wx
from wx.lib.pubsub import pub

import warnings

class devGlobal():

    def __init__(self, com_type, info, paramVec, output, devComm, panelId):

        self.info     = info
        self.address  = info["address"]
        self.idn      = info["idn"]
        self.com_type = com_type
        self.paramVec = paramVec
        self.output   = output
        self.devComm  = devComm
        self.panelId  = panelId

        self.additionalPanels = []

        self.answer = []

        self.label_list = []


        self.write("*CLS")

        self.register(self.GetId,    'Get Device\nId')
        self.register(self.clear_dev_errorbyte, 'Clears Error\nByte')
        self.register(self.getDevError, 'Get Device\nError')
        # self.register(self.autoCal,  'Runs Auto\nCalibration')
        self.register(self.selfTest, 'Runs Auto\nTest')

    def GetId(self, msg):
        cmd_string = "Gets Identification on "
        self.query("*IDN?")
        self.printOut(cmd_string)

    def clear_dev_errorbyte(self, msg):
        cmd_string = "Clears the error byte on "
        self.write("*CLS")
        self.printOut(cmd_string)

    def getDevError(self, msg):
        cmd_string = "Determines error on connectivity for "
        self.query("*ESR?")
        self.printOut(cmd_string)

    # def autoCal(self, msg):
    #     cmdString = "Runs auto calibration on "
    #     self.write("*CAL?")
    #     OPC = False
    #     while not(OPC):
    #         a = self.query("*ESR?")
    #         print(a)
    #         if bin(a)[-1:] == '1':
    #             OPC = True
    #     self.printOut(cmdString)

    def selfTest(self, msg):
        cmd_string = "Runs self test on "
        self.query("*TST?")
        self.printOut(cmd_string)

    def get_param_vector(self, param_pointer):
        param = []
        for i in range(len(param_pointer)):
            param.append(param_pointer[i].GetValue())
        return param
        
    def register(self, func, label, parameters=[], panel_specific=""):
        # This needs to be changed, further down the road the inputs on each function 
        # Need to be each given a name (currently we just have channel 1, channel 2,
        # and parameter, the parameters list will hold those names
        name = ""
        if len(parameters) > 0:
            name = parameters[0]
        self.label_list.append((label, func, name, parameters, panel_specific))
        pub.subscribe(func, self.createTopic(label))

    def createTopic(self, label):
        # Beginning a topic with "INSTRUMENT--" is reserved
        return "INSTRUMENT<==>{}<==>{}".format(self.idn, label)

    def printOut(self, cmd_string):
        total_cmd_string = f"{cmd_string}\n{self.idn}\n{self.answer}"
        self.output.SetValue(total_cmd_string)

        self.answer = ''

    def find_str(self, sub, sent):
        return [x.start() for x in re.finditer(sub,sent)]

    def query(self, cmd, paranoia_level = 1):
        ans = self.devComm.query(cmd)
        self.wait_for_command(paranoia_level)
        self.answer = ans
        return ans

    def write(self, cmd, paranoia_level = 1):
        self.devComm.write(cmd)
        self.wait_for_command(paranoia_level)

    # Added for symmetry
    def read(self):
        return self.devComm.read()

    def wait_for_command(self, paranoia_level = 1):
        """This is adaptaded from code provided to us by Tabor
        Information about the OPC? command:
            http://na.support.keysight.com/vna/help/latest/Programming/GP-IB_Command_Finder/Common_Commands.htm#opcq"""
        if paranoia_level <= 1:
            return self.devComm.query('*OPC?')

        elif paranoia_level > 1:
            syst_err = self.devComm.query(':SYST:ERR?')
            try:
                errnb = int(syst_err.split(',')[0])
            except:
                errnb = -1
            if errnb != 0:
                syst_err = syst_err.rstrip()
                wrn_msg = 'ERR: "{0}"'.format(syst_err)
                _ = self.devComm.query('*CLS; *OPC?') # clear the error-list
                if paranoia_level >= 3:
                    raise NameError(wrn_msg)
                else:
                    warnings.warn(wrn_msg)

