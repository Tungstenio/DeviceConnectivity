import json
import os

import tkinter
from tkinter import filedialog

# 
def saveSession(info, name, macros, filename = None):
    if len(info) != len(name):
        raise Exception("length of info must equal length of names")

    toSave = {"Devices": {
                "Info": info,
                "Name": name
                },
              "Macros": macros}

    configPath = os.path.abspath("macros")

    if filename == None:
        filename = filedialog.asksaveasfilename(initialdir = configPath, 
                filetypes = [("Session Files", "*.ses")])

    with open(filename, 'w') as f:
        json.dump(toSave, f, indent = 2)

def loadSession(start_folder = "macros", filename = None):
    configPath = os.path.abspath(start_folder)

    if filename == None:
        filename = filedialog.askopenfilename(initialdir = configPath, 
                filetypes = [("Session Files", "*.ses")])

    with open(filename, 'r') as f:
        loaded = json.load(f)

    devices = loaded["Devices"]

    return devices["Info"], devices["Name"], loaded["Macros"]


if __name__ == "__main__":
    saveSession(["Tabor?"], ["Super Fast"], macros = [
            ["IDN?", {"msg": "idn"},   {"depth": 1, "repeat": 4}],
            ["SetWave", {"msg": "sw"}, {"depth": 2, "repeat": 1}],
            ["TurnOn", {"msg": "to"},     {"depth": 3, "repeat": 3}],
            ["Refr", {"msg": "refr"},   {"depth": 1, "repeat": 1}]])
    # print(loadSession())

