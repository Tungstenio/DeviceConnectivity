from Instruments.devGlobalFunctions import devGlobal
import numpy as np
import struct
import wx
import math

import pyte16 as pyte

from wx.lib.pubsub import pub

#Simple panel
class graphPanel(wx.Panel):
    def __init__(self, parent, device):
        wx.Panel.__init__(self,parent)

        button_sizer = wx.BoxSizer(wx.VERTICAL)

        btnWidth  = 90
        btnHeight = 40
        blankBtnLabel = "&Blank"

        self.device = device

        #==============================================================================================================================================================
        # Buttons are created with labels, sizes, and positions. The names of the buttons are arbitrary but
        # it is a good practice to name them according to their function.
        ##Creating Buttons

        self.button = []
        rowSizer = wx.BoxSizer(wx.HORIZONTAL)
        rowCounter = 0
        buttonsInARow = 5
        buttonsInACol = 3
        for i in range(buttonsInARow*buttonsInACol):
            btnIndexCol = i%buttonsInARow + 1
            btnIndexRow = int(math.floor(i/buttonsInARow)) + 1
            self.button.append(wx.Button(self, label = blankBtnLabel + "\n(" + str(btnIndexRow) + "," + str(btnIndexCol) + ")", size = (btnWidth, btnHeight)))
            self.button[i].SetBackgroundColour("RED")
            rowSizer.Add(self.button[i], 0, wx.ALL, 1)

            if btnIndexCol == buttonsInARow:
                button_sizer.Add(wx.StaticLine(self), 0, wx.ALL, 1)
                button_sizer.Add(rowSizer,            0, wx.ALL, 0)
                rowSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.SetSizerAndFit(button_sizer)

class SuperFastClass(devGlobal):
    # Human readable name for the gui, note: Needs to be unique
    name = "Super Fast"
    def __init__(self, *args):
        devGlobal.__init__(self, *args)

        self.devComm.write("*CLS; *RST")

        self.devComm.write(":INST:SEL 1")
        self.devComm.write(":OUTPut:STATe OFF")
        self.devComm.write(":INST:SEL 2")
        self.devComm.write(":OUTPut:STATe OFF")
        self.devComm.write(":INST:SEL 3")
        self.devComm.write(":OUTPut:STATe OFF")
        self.devComm.write(":INST:SEL 4")
        self.devComm.write(":OUTPut:STATe OFF")
        self.devComm.write(":INST:SEL 1")

        self.ch1OnOff = 0
        self.ch2OnOff = 0
        self.ch3OnOff = 0
        self.ch4OnOff = 0

        self.numTabs = 2

        self.additionalPanels  = [(graphPanel, 'Graph Tab')]

        self.register(self.GetModelOption,        'Gets Model\nOption')
        self.register(self.SegmentLength,         'Segment\nLength')
        self.register(self.Tests,                 'Tests')
        self.register(self.SetOperatingChannel,   'Sets Operating\nChannel') # not this function used channel input, but we don't handle that yet
        self.register(self.SetStandardSquareWave, 'Standard\nSquare Wave', parameters = ["Frequency"])
        self.register(self.OutputOnOff,           'Sets Operating\nChannel On/Off',  "")
        self.register(self.DeleteAllTraces,       'Deletes\nAll Traces')
        self.register(self.TracePoints,           'Queries\nTrace Points')
        self.register(self.Ch1OnOff,              'Ch1 Output\nOn/Off')
        self.register(self.Ch2OnOff,              'Ch2 Output\nOn/Off')
        self.register(self.SyncChannels,          'Sync\nCh1 and Ch2')
        self.register(self.Ch1TrigIntExt,         'Ch1 Trigger\nInt/Ext', parameters = ["Ch1 Trigger"])
        self.register(self.Ch2TrigIntExt,         'Ch2 Trigger\nInt/Ext', parameters = ["Ch1 Trigger"])
        self.register(self.Ch1setWaitTime,        'Ch1 Set\nWait Time', parameters = ["CH1 Wait Time"])


    def GetModelOption(self, msg):
        cmdString   = "Queries memory option on "
        self.answer = str(int(self.devComm.query("*OPT?")[2:4])*1e6)
        self.printOut(cmdString)
        done = 0
        while done != 1:
            print(self.devComm.query("*OPC?"))
            done = int(self.devComm.query("*OPC?"))

    def SegmentLength(self, msg):
        cmdString   = "Gets Segment Length on "
        self.answer = self.devComm.query(":TRACE:DEFine?")
        self.printOut(cmdString)

    def Tests(self, msg):
        cmdString = "Arbitrary waveform tests on "

        cycle_len = 1024
        num_cycles = 1
        seg_len = cycle_len * num_cycles

        wave1 = self.build_sine_wave(cycle_len,num_cycles, low_level=4000,
                          high_level=2 ** 14 - 4000)

        wave2 = self.build_square_wave(cycle_len, num_cycles)

        self.devComm.write(":INST:SEL 1")
        self.devComm.write(":TRAC:MODE SING")

        seg_nb = 1
        self.devComm.write(':TRAC:DEF {0:d},{1:d}'.format(seg_nb, seg_len))
        self.devComm.write(':TRAC:SEL {0:d}'.format(seg_nb))
        self.send_binary_data(pref=':TRAC:DATA', bin_dat=wave1)

        seg_nb = 2
        self.devComm.write(':TRAC:DEF {0:d},{1:d}'.format(seg_nb, seg_len))
        self.devComm.write(':TRAC:SEL {0:d}'.format(seg_nb))
        self.send_binary_data(pref=':TRAC:DATA', bin_dat=wave2)

        seg_num = [2, 1, 2, 1]
        repeats = [1, 5, 1, 4]
        jump    = [0, 0, 0, 0]
        seq_table = list(zip(repeats, seg_num, jump))

        self.devComm.write(':SEQ:SELect 1')
        self.download_sequencer_table(seq_table)

        self.devComm.write(':SOURce:FUNCtion:MODE SEQ')
        self.devComm.write(':SOUR:FREQ:RAST 1.0e9')

        self.printOut(cmdString)

        yNP = np.concatenate((wave1,wave2))

        pub.sendMessage('PrintData', msg=[self.panelId,yNP])

    def SetOperatingChannel(self, msg):
        param = self.GetParamVector()
        cmdString = "Sets the operating channel to " + param[0] + " on "
        visaCmd = ":INST:SEL " + param[0]
        self.devComm.write(visaCmd)
        self.printOut(cmdString)

    def SetStandardSquareWave(self, msg):
        param = self.GetParamVector()
        cmdString = "Sets a standard square wave with frequency " + param[2] + " on the operating channel on "
        self.devComm.write(':SOURce:FUNCtion:MODE FIX')
        self.devComm.write(":SOURce:FREQuency:CW " + param[2])
        self.devComm.write(":SOURce:FUNCtion:SHAPe SQU")
        self.devComm.write(":SOURce:SQUare:DCYC 50.0")
        self.printOut(cmdString)

    def OutputOnOff(self, msg):
        cmdString = "Sets active channel output to on/off on "

        if self.ch1OnOff == 0:
            self.ch1OnOff = 1
            self.devComm.write(":OUTPut:STATe ON")
        else:
            self.ch1OnOff = 0
            self.devComm.write(":OUTPut:STATe OFF")

        self.printOut(cmdString)

    def DeleteAllTraces(self, msg):
        cmdString = "Deletes all traces on "
        self.devComm.write(":TRACE:DELETE:ALL")
        self.printOut(cmdString)

    def TracePoints(self, msg):
        cmdString = "Queries trace points on "
        self.answer = self.devComm.query(":TRAC:POINts?")
        self.printOut(cmdString)

    def Ch1OnOff(self, msg):
        param = self.GetParamVector()
        cmdString = "Sets Ch1 Output to " + param[2] + " on "
        cmdString = cmdString + self.address + "\n"
        self.printOut(self.cmdString)

    def Ch2OnOff(self, msg):
        param = self.GetParamVector()
        cmdString = "Sets Ch2 Output to " + param[2] + " on "
        cmdString = cmdString + self.address + "\n"
        print(self.cmdString)

    def SyncChannels(self, msg):
        StringInit = "Sync Ch1 and Ch2 on "
        self.cmdString = StringInit + self.address
        print(self.cmdString)

    def Ch1TrigIntExt(self, msg):
        param = self.GetParamVector()
        cmdString = "Sets Ch1 Trigger to " + param[2] + " on "
        cmdString = cmdString + self.com_type + self.address + "\n"
        print(self.cmdString)

    def Ch2TrigIntExt(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Ch2 Trigger to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch1setWaitTime(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Ch1 Wait Time to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch2setWaitTime(self, event):
        param = self.GetParamVector()
        StringInit = "Sets Ch2 Wait Time to " + param[2] + " on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch1Ena10MExtRef(self, event):
        StringInit = "Enable Ch1 10 MHz External Reference on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def Ch2Ena10MExtRef(self, event):
        StringInit = "Enable Ch2 10 MHz External Reference on "
        self.cmdString = StringInit + self.com_type + self.address
        print(self.cmdString)

    def build_sine_wave(self, cycle_len, num_cycles=1, phase_degree=0, low_level=0, high_level=2**14-1):
        cycle_len = int(cycle_len)
        num_cycles = int(num_cycles)

        if cycle_len <= 0 or num_cycles <= 0:
            return None

        dac_min = 0
        dac_max = 2**14-1

        wav_len = cycle_len * num_cycles

        phase = float(phase_degree) * np.pi / 180.0
        x = np.linspace(start=phase, stop=phase+2*np.pi, num=cycle_len, endpoint=False)

        zero_val = (low_level + high_level) / 2.0
        amplitude = (high_level - low_level) / 2.0
        y = np.sin(x) * amplitude + zero_val
        y = np.round(y)
        y = np.clip(y, dac_min, dac_max)

        y = y.astype(np.uint16)

        wav = np.empty(wav_len, dtype=np.uint16)
        for n in range(num_cycles):
            wav[n * cycle_len : (n + 1) * cycle_len] = y

        return wav

    def build_square_wave(self, cycle_len, num_cycles=1, duty_cycle=50.0, phase_degree=0, low_level=0,
                          high_level=2 ** 14 - 1):
        cycle_len = int(cycle_len)
        num_cycles = int(num_cycles)

        if cycle_len <= 0 or num_cycles <= 0:
            return None

        dac_min = 0
        dac_max = 2 ** 14 - 1

        wav_len = cycle_len * num_cycles

        duty_cycle = np.clip(duty_cycle, 0.0, 100.0)
        low_level = np.clip(low_level, dac_min, dac_max)
        high_level = np.clip(high_level, dac_min, dac_max)

        low_level = np.uint16(low_level)
        high_level = np.uint16(high_level)

        phase = float(phase_degree) * np.pi / 180.0
        x = np.linspace(start=phase, stop=phase + 2 * np.pi, num=cycle_len, endpoint=False)
        x = x <= 2 * np.pi * duty_cycle / 100.0
        y = np.full(x.shape, low_level, dtype=np.uint16)
        y[x] = high_level

        y = y.astype(np.uint16)

        wav = np.empty(wav_len, dtype=np.uint16)
        for n in range(num_cycles):
            wav[n * cycle_len: (n + 1) * cycle_len] = y

        return wav

    def download_sequencer_table(self, seq_table, pref=':SEQ:DATA'):
        tbl_len = len(seq_table)

        s = struct.Struct('< L H B x')
        s_size = s.size
        m = np.empty(s_size * tbl_len, dtype='uint8')
        for n in range(tbl_len):
            repeats, seg_nb, jump_flag = seq_table[n]
            s.pack_into(m, n * s_size, np.uint32(repeats), np.uint16(seg_nb), np.uint8(jump_flag))

        self.send_binary_data(pref, m)

    def send_binary_data(self, pref, bin_dat):
        pyte.download_binary_data(self.devComm, pref, bin_dat, bin_dat.nbytes)

# IMPORTANT Don't forget this line (and remember to use the class name above)
instrument = SuperFastClass

