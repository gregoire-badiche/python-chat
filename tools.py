from platform import system

if(system() == "Windows"):
    import msvcrt
else:
    from pynput.keyboard import Listener, Key

class wHandler():
    def __init__(self, callback, blocking):
        self.callback = callback
    def getk(self):
        arrow = False
        while(msvcrt.kbhit()):
            key = msvcrt.getch()
            if(key == b"\xe0"):
                arrow = True
            if(arrow == True and key == b"H"):
                return 'up'
            if(arrow == True and key == b"P"):
                return 'down'
            if(arrow == True and key == b"K"):
                return 'left'
            if(arrow == True and key == b"M"):
                return 'right'
        return ""

class uHandler():
    def __init__(self, callback, blocking):
        self.callback = callback()
        self.listener = Listener(on_press=self.callback)
        self.listener.start()
        if(blocking):
            self.listener.join()

def Handler(callback, blocking=False):
    if(system() == "Windows"):
        return wHandler(callback, blocking)
    else:
        return uHandler(callback, blocking)
