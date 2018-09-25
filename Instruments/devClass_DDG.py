from Instruments.devGlobalFunctions import devGlobal
import wx
import math

class specBtnPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        button_sizer = wx.BoxSizer(wx.VERTICAL)

        btn_width       = 90
        btn_height      = 40
        blank_btn_label = "&Blank"

        self.button = []
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_in_a_row = 5
        buttons_in_a_col = 8
        for i in range(buttons_in_a_row*buttons_in_a_col):
            btn_index_col = i % buttons_in_a_row + 1
            btn_index_row = int(math.floor(i/buttons_in_a_row)) + 1
            self.button.append(wx.Button(self,
                                         label=blank_btn_label + "\n(" + str(btn_index_row) + ","
                                                                       + str(btn_index_col) + ")",
                                         size=(btn_width, btn_height)))
            self.button[i].SetBackgroundColour("RED")
            row_sizer.Add(self.button[i], 0, wx.ALL, 1)

            if btn_index_col == buttons_in_a_row:
                button_sizer.Add(wx.StaticLine(self), 0, wx.ALL, 1)
                button_sizer.Add(row_sizer,            0, wx.ALL, 0)
                row_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.SetSizerAndFit(button_sizer)

class specInOutPanel(wx.Panel):
    def __init__(self, parent, w):
        wx.Panel.__init__(self, parent)

        param_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.txtParamLbl1 = wx.StaticText(self, size=((w - 20) / 4, 20), label="      Channel: ")
        self.txtParamLbl2 = wx.StaticText(self, size=((w - 20) / 4, 20), label="      Channel: ")
        self.txtParamLbl3 = wx.StaticText(self, size=((w - 20) / 2, 20), label="      Command Input Value: ")
        self.txtParamLbl4 = wx.StaticText(self, size=((w - 20) / 2, 20), label=" Command Output Value: ")
        param_label_sizer = wx.BoxSizer(wx.HORIZONTAL)
        param_label_sizer.Add(self.txtParamLbl1, 0, wx.ALL, 1)
        param_label_sizer.Add(self.txtParamLbl2, 0, wx.ALL, 1)
        param_label_sizer.Add(self.txtParamLbl3, 0, wx.ALL, 1)

        self.txtParam1 = wx.TextCtrl(self, size=((w - 20) / 4, 20))
        self.txtParam2 = wx.TextCtrl(self, size=((w - 20) / 4, 20))
        self.txtParam3 = wx.TextCtrl(self, size=((w - 20) / 2, 20))
        self.txtParam4 = wx.TextCtrl(self, size=((w - 20), 80), style=wx.TE_MULTILINE | wx.TE_READONLY)
        param_sizer = wx.BoxSizer(wx.HORIZONTAL)
        param_sizer.Add(self.txtParam1, 0, wx.ALL, 1)
        param_sizer.Add(self.txtParam2, 0, wx.ALL, 1)
        param_sizer.Add(self.txtParam3, 0, wx.ALL, 1)

        self.paramVector = []
        self.paramVector.append(self.txtParam1)
        self.paramVector.append(self.txtParam2)
        self.paramVector.append(self.txtParam3)

        param_panel_sizer.Add(param_label_sizer, 0, wx.ALL | wx.CENTER, 1)
        param_panel_sizer.Add(param_sizer, 0, wx.ALL | wx.CENTER, 1)
        param_panel_sizer.Add(self.txtParamLbl4, 0, wx.CENTER, 1)
        param_panel_sizer.Add(self.txtParam4, 0, wx.ALL, 1)

        self.output = self.txtParam4

        self.SetSizerAndFit(param_panel_sizer)

class specPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.specBtn   = specBtnPanel(self)
        w, _           = self.specBtn.GetSize()
        self.specInOut = specInOutPanel(self, w)

        self.output    = self.specInOut.output
        self.button    = self.specBtn.button
        self.param_vec = self.specInOut.paramVector

        main_sizer.Add(self.specInOut, 0, wx.CENTER, 1)
        main_sizer.Add(self.specBtn,   0, wx.LEFT,    1)

        self.SetSizerAndFit(main_sizer)

class DDGClass(devGlobal):
    # Human readable name for the gui, note: Needs to be unique
    name = "DDG"
    def __init__(self, *args):
        devGlobal.__init__(self, *args)

        self.register(self.advTrigMode, 'Enables Adv\nTriggering')

        self.register(self.setCh1Delay, 'Set\nDelay', parameters=["Delay [s]"], panel_specific='Ch1 Tab')
        self.register(self.setCh1Width, 'Set\nWidth', parameters=["Width [s]"], panel_specific='Ch1 Tab')
        self.register(self.setCh1Amplitude, 'Set\nAmplitude', parameters=["Amplitude [V]"],
                      panel_specific='Ch1 Tab')
        self.register(self.setCh1Offset, 'Set\nOffset', parameters=["Offset [V]"],
                      panel_specific='Ch1 Tab')
        self.register(self.setCh1Polarity, 'Set Polarity\n(1=pos;0=neg)', parameters=["Offset [V]"],
                      panel_specific='Ch1 Tab')

        self.register(self.setCh2Delay, 'Sets Ch2\nDelay', parameters=["Delay [s]"], panel_specific='Ch2 Tab')
        self.register(self.setCh3Delay, 'Sets Ch3\nDelay', parameters=["Delay [s]"], panel_specific='Ch3 Tab')
        self.register(self.setCh4Delay, 'Sets Ch4\nDelay', parameters=["Delay [s]"], panel_specific='Ch4 Tab')

        self.additionalPanels = [(specPanel, 'Ch1 Tab'),
                                 (specPanel, 'Ch2 Tab'),
                                 (specPanel, 'Ch3 Tab'),
                                 (specPanel, 'Ch4 Tab')]

    def advTrigMode(self, msg):
        cmd_string = "Sets the triggering to advanced mode on "
        self.write("advt 1\n")
        self.printOut(cmd_string)

    def setCh1Delay(self, msg):
        param = msg['params']
        cmd_string = "Sets the delay on channel 1 (AB) to {0} [s] on ".format(param[2])
        test_string = "dlay 2,0,{0}\n".format(param[2])
        self.write(test_string)
        test_string = "dlay?2\n".format(param[2])
        self.query(test_string)
        self.printOut(cmd_string)
        test_string = "disp 11,2"
        self.write(test_string)

    def setCh1Width(self, msg):
        param = msg['params']
        cmd_string = "Sets the delay on channel 1 (AB) to {0} [s] on ".format(param[2])
        test_string = "dlay 3,2,{0}\n".format(param[2])
        self.write(test_string)
        test_string = "dlay?3\n".format(param[2])
        self.query(test_string)
        self.printOut(cmd_string)
        test_string = "disp 11,3"
        self.write(test_string)

    def setCh1Amplitude(self, msg):
        param = msg['params']
        cmd_string = "Sets the amplitude on channel 1 (AB) to {0} [V] on ".format(param[2])
        test_string = "lamp 1,{0}\n".format(param[2])
        self.write(test_string)
        test_string = "lamp?1\n".format(param[2])
        self.query(test_string)
        self.printOut(cmd_string)
        test_string = "disp 12,3"
        self.write(test_string)

    def setCh1Offset(self, msg):
        param = msg['params']
        cmd_string = "Sets the offset on channel 1 (AB) to {0} [V] on ".format(param[2])
        test_string = "loff 1,{0}\n".format(param[2])
        self.write(test_string)
        test_string = "loff?1\n".format(param[2])
        self.query(test_string)
        self.printOut(cmd_string)
        test_string = "disp 12,2"
        self.write(test_string)

    def setCh1Polarity(self, msg):
        param = msg['params']
        cmd_string = "Sets the polarity on channel 1 (AB) to {0} on ".format(param[2])
        test_string = "lpol 1,{0}\n".format(param[2])
        self.write(test_string)
        test_string = "lpol?1\n".format(param[2])
        self.query(test_string)
        self.printOut(cmd_string)
        test_string = "disp 13,3"
        self.write(test_string)

    def setCh2Delay(self, msg):
        param = msg['params']
        cmd_string = "Sets the delay on channel 1 (CD) to {0} [s] on".format(param[2])
        test_string = "dlay 4,0,{0}\n".format(param[2])
        self.write(test_string)
        test_string = "dlay?4\n".format(param[2])
        self.query(test_string)
        self.printOut(cmd_string)

    def setCh3Delay(self, msg):
        param = msg['params']
        cmd_string = "Sets the delay on channel 1 (EF) to {0} [s] on".format(param[2])
        test_string = "dlay 6,0,{0}\n".format(param[2])
        self.write(test_string)
        test_string = "dlay?6\n".format(param[2])
        self.query(test_string)
        self.printOut(cmd_string)

    def setCh4Delay(self, msg):
        param = msg['params']
        cmd_string = "Sets the delay on channel 1 (HG) to {0} [s] on".format(param[2])
        test_string = "dlay 8,0,{0}\n".format(param[2])
        self.write(test_string)
        test_string = "dlay?8\n".format(param[2])
        self.query(test_string)
        self.printOut(cmd_string)
                
# IMPORTANT Don't forget this line (and remember to use the class name above)
instrument = DDGClass

