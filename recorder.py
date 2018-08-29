import os
import json
import threading

import saveSession

from wx.lib.pubsub import pub

def split_children(current, commands):
    for i in range(len(commands)):
        if commands[i][2]["depth"] <= current[2]["depth"]:
            return commands[:i], commands[i:]

    return commands, []

def translate_structural(commands):
    if len(commands) == 0:
        return []
    else:
        children, rest = split_children(commands[0], commands[1:])
        current = [{"com": commands[0],
                    "children": translate_structural(children)}]
        return current + translate_structural(rest)


class Recorder():
    def __init__(self):
        self._listening = False
        self._commands = []
        self.devInfoList = []
        self.devNameList = []
        self.notPaused = threading.Event()
        self.thread = threading.Thread()
        self.macroPath  = os.path.abspath("macros")
        self.autosaveFile = os.path.join(self.macroPath, 'lastsession.ses')
        
        pub.subscribe(self.listen, pub.ALL_TOPICS)

        pub.subscribe(self.start, 'RecorderStart')
        pub.subscribe(self.stop, 'RecorderStop')
        pub.subscribe(self.load, 'RecorderLoad')
        pub.subscribe(self.play, 'RecorderPlay')
        pub.subscribe(self.clear, 'RecorderClear')
        pub.subscribe(self.pause, 'RecorderPause')

    def start(self, msg):
        self._listening = True
        self.clear(msg)
        print("Recording Started")

    def stop(self, msg):
        self._listening = False
        print("Recording Stopped")
        self.save()

    def clear(self, msg):
        self._commands = []
        print("Macro Cleared!")

    def listen(self, topic = pub.AUTO_TOPIC, **kwargs):
        topic_name = topic.getName()

        # Only listen to instrument commands
        if not topic_name.startswith("INSTRUMENT<==>"): return

        if self._listening:
            self._commands.append([topic_name, kwargs, {"depth": 1, "repeat": 1}])
            pub.sendMessage('MacroPanelRefresh') # Could also move this to self.stop()

    def play(self):
        if self._listening:
            self.stop() #don't want an infinite loop

        print("Lets play!")
        self.notPaused.set() # The thread is clear to run

        if not self.thread.is_alive(): # No active thread
            run_structure = translate_structural(self._commands)
            self.thread = threading.Thread(target = self.__play, args = (run_structure,self.notPaused))
            print("Starting Thread")
            self.thread.start()

    def __play(self, commands, notPaused):
        if len(commands) == 0:
            return
        else:
            com, *rest = commands
            topic_name, kwargs, info = com["com"]
            for i in range(info["repeat"]):
                can_run = notPaused.wait()
                pub.sendMessage(topic_name, **kwargs)
                self.__play(com["children"], notPaused)

            self.__play(rest, notPaused)
            
    def pause(self):
        print("Trying to pause")
        self.notPaused.clear()

    def get_macros(self):
        macros = []
        for com in self._commands:
            topic, args, loop_info = com
            head, idn, label = topic.split("<==>")

            macros.append([idn, label, args, loop_info])

        return macros

    def set_macros(self, new_macros):
        self._commands = []
        for com in new_macros:
            idn, label, args, loop_info = com
            topic = "<==>".join(["INSTRUMENT", idn, label])
            self._commands.append([topic, args, loop_info])
        self.save()

    def save(self):
        print(self.devInfoList)
        saveSession.saveSession(self.devInfoList, self.devNameList,
                macros = self._commands,
                filename = self.autosaveFile)
                
    def load(self, msg):
        self.devInfoList, self.devNameList, self._commands = msg

if __name__ == "__main__":
    def print_play(msg = ""):
        print(msg)
    test = [
            ["Test", {"msg": "1"},     {"depth": 1, "repeat": 2}],
            ["Test", {"msg": "  2"},   {"depth": 2, "repeat": 1}],
            ["Test", {"msg": "    3"}, {"depth": 3, "repeat": 1}],
            ["Test", {"msg": "  2"},   {"depth": 2, "repeat": 3}],
            ["Test", {"msg": "  2"},   {"depth": 2, "repeat": 4}],
            ["Test", {"msg": "    3"}, {"depth": 3, "repeat": 1}],
            ["Test", {"msg": "1"},     {"depth": 1, "repeat": 3}],
            ["Test", {"msg": "  2"},   {"depth": 2, "repeat": 1}],
            ]
    print(json.dumps(translate_structural(test), indent = 2))
    pub.subscribe(print_play, "Test")
    recorder = Recorder(test)
    recorder.play({})
