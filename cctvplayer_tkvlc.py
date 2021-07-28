#! /usr/bin/python3

"""A simple example for VLC python bindings using tkinter. Uses python 3.4

Author: Patrick Fay
Date: 23-09-2015
"""

# import external libraries
import vlc
import sys

if sys.version_info[0] < 3:
    import Tkinter as Tk
    from Tkinter import ttk
else:
    import tkinter as Tk
    from tkinter import ttk

# import standard libraries
import os
import platform
import configparser, logging

class Player(Tk.Frame):
    """The main window has to deal with events.
    """
    def __init__(self, parent):
        Tk.Frame.__init__(self, parent)
        self.pack(fill=Tk.BOTH, expand=1)

        self.parent = parent

        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        title = self.config['DEFAULT']['title']
        if title == None:
            title = "tk_vlc"
        logging.info("title %s", title)
        self.parent.title(title)
        self.parent.minsize(width=502, height=0)

        scrollCanvas = Tk.Canvas(self, bg="darkgrey")
        hsb = ttk.Scrollbar(self, orient=Tk.HORIZONTAL, command=scrollCanvas.xview)
        hsb.pack(side=Tk.BOTTOM , fill=Tk.X)
        scrollCanvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)

        # Link a scrollbar to the canvas
        vsb = ttk.Scrollbar(self, orient=Tk.VERTICAL, command=scrollCanvas.yview)
        vsb.pack(side=Tk.RIGHT, fill=Tk.Y)

        scrollCanvas.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        scrollCanvas.bind('<Configure>', lambda e: scrollCanvas.configure(scrollregion = scrollCanvas.bbox("all")))

        self.internalFrame = Tk.Frame(scrollCanvas, bg="gray")
        
        scrollCanvas.create_window((0,0), window=self.internalFrame, anchor="c")

        self.gridSize = self.config['DEFAULT'].getint('gridsize')
        self.player = [None] * 10
        self.videopanel = [None] * 10
        self.canvas = [None] * 10
        for index in range(8):
            self.createPlayer(index)

        #self.internalFrame.update()
        self.parent.update()


    def createPlayer(self, index):
        streamUrl = self.config['DEFAULT']['rtspurl']
        self.player[index] = None
        #rootHeight = self.internalFrame.winfo_height()
        #rootWidth = self.internalFrame.winfo_width()
        self.videopanel[index] = Tk.Frame(self.internalFrame, bg="grey", width=400, height=220, bd=5)

        rowNo = 0
        colNo = index
        if (index + 1 > self.gridSize):
            rowNo = index // self.gridSize
            colNo = index % self.gridSize
        #self.canvas[index] = Tk.Canvas(self.videopanel[index], bg="blue").grid(row=rowNo,column=colNo)
        self.videopanel[index].grid(row=rowNo,column=colNo, padx=10, pady=10)

        vlc_options = self.config['DEFAULT']['vlcoptions']
        tempInstance = vlc.Instance(vlc_options)
        self.player[index] = tempInstance.media_player_new()

        media = tempInstance.media_new(streamUrl.replace('$index', str(index + 1)))
        self.player[index].set_media(media)
        # set the window id where to render VLC's video output
        if platform.system() == 'Windows':
            self.player[index].set_hwnd(self.videopanel[index].winfo_id())
        else:
            self.player[index].set_xwindow(self.videopanel[index].winfo_id()) # this line messes up windows
        # FIXME: this should be made cross-platform
        self.player[index].play() # hit the player button
        #self.player.video_set_deinterlace(str_to_bytes('yadif'))

    def OnExit(self, evt):
        """Closes the window.
        """
        self.Close()

    def errorDialog(self, errormessage):
        """Display a simple error dialog.
        """
        Tk.tkMessageBox.showerror(self, 'Error', errormessage)

def Tk_get_root():
    if not hasattr(Tk_get_root, "root"): #(1)
        config = configparser.ConfigParser()
        config.read('config.ini')

        classname = config['DEFAULT']['classname']
        logging.info("classname : %s", classname)
        Tk_get_root.root= Tk.Tk(className=classname)  #initialization call is inside the function
    return Tk_get_root.root

def _quit():
    print("_quit: bye")
    logging.info("_quit: bye")
    root = Tk_get_root()
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate
    os._exit(1)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Create a Tk.App(), which handles the windowing system event loop
    logging.basicConfig(filename='myapp.log', level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info("starting")
    root = Tk_get_root()
    root.protocol("WM_DELETE_WINDOW", _quit)

    player = Player(root)
    root.attributes('-zoomed', True)
    root.resizable(0,0)
    # root.state('zoomed')
    # show the player window centred and run the application
    root.mainloop()
