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

        self.label_list  = []
        
        self.register(self.GetId, 'Get Device\nId')
		
    def GetId(self, msg):
        cmdString   = "Gets Identification on "
        self.query("*IDN?") # We don't use the output here but it is a query
        self.printOut(cmdString)

    def GetParamVector(self):
        param = []
        for i in range(len(self.paramVec)):
            param.append(self.paramVec[i].GetValue())
        return param
        
    def register(self, func, label, name = "", sc = False, dc = False, parameter = False):
        self.label_list.append((label, func, name, sc, dc, parameter))
        pub.subscribe(func, self.createTopic(label))

    def createTopic(self, label):
        # Beginning a topic with "INSTRUMENT--" is reserved
        return "INSTRUMENT<==>{}<==>{}".format(self.idn, label)

    def printOut(self, cmdString):
        totalCmdString = f"{cmdString}\n{self.idn}\n{self.answer}"
        self.output.SetValue(totalCmdString)

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
                wrn_msg = 'ERR: "{0}" after CMD: "{1}"'.format(syst_err, cmd_str)
                _ = self.devComm.query('*CLS; *OPC?') # clear the error-list
                if paranoia_level >= 3:
                    raise NameError(wrn_msg)
                else:
                    warnings.warn(wrn_msg)

