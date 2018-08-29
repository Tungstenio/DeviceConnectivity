import sys
import threading
import matplotlib

matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure

matplotlib.rc('font', family='sans-serif') 
matplotlib.rc('font', serif='Helvetica Neue') 
matplotlib.rc('text', usetex='false') 
matplotlib.rcParams.update({'font.size': 7})

import wx

class wxMatplotLib(wx.Panel): ## wx.Frame
    def __init__(self, parent, sizeXY):
        wx.Panel.__init__(self, parent) ## wx.Frame --> for statusBar

        self.version = '1.0'

        self.SetBackgroundColour("WHITE")
        
        params = {'axes.labelsize':  10,
                  'font.size':       8,
                  'legend.fontsize': 10,
                  'xtick.labelsize': 8,
                  'ytick.labelsize': 8}
        matplotlib.rcParams.update(params)
        #self.figure = Figure(dpi=dpi, figsize=figsize, facecolor='w', edgecolor='k')
        self.figure = Figure(figsize=sizeXY,facecolor = 'w', edgecolor = 'k')
        self.canvas = FigureCanvas(self, 0, self.figure)
        self.axes   = self.figure.add_subplot(111)

        #Set title and other things
        self.xlabel = ''
        self.ylabel = ''
        self.layout = (1,1,1)   #layout of plots (height, width, count)
        self.axes.grid(True)

        # Data
        self.x = []
        self.y = []

        # Plot blank
        self.axes.plot(self.x, self.y)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(self.canvas, 0, wx.ALL)
        self.SetSizer(self.sizer)
        
    def updateCanvas(self):
        self.canvas.draw()

    def setData(self, x = None, y = None, x_axis = None, y_axis = None, graph_type = None):
        if x and y:
            self.axes.clear()
            self.axes.grid(True)
            if graph_type == 'Plot':
                self.axes.plot(x, y)
            else:
                self.axes.scatter(x, y)
            if x_axis:
                self.axes.set_xlim(x_axis)
            if y_axis:
                self.axes.set_ylim(y_axis)    
        self.updateCanvas()

    def setLabel(self, xlabel = None, ylabel = None, title = None):
        if xlabel:
            self.axes.set_xlabel(xlabel)
        if ylabel:
            self.axes.set_ylabel(ylabel)
        if title:
            self.axes.set_title(title)
        self.updateCanvas()

    def setYminmax(self, Ymin = None, Ymax = None):
        if Ymin != None and Ymax != None:
            self.axes.set_ylim([Ymin,Ymax])
            self.updateCanvas()

    def setXminmax(self, Xmin = None, Xmax = None):
        if Xmin != None and Xmax != None:
            self.axes.set_xlim([Xmin,Xmax])
            self.updateCanvas()

    def setParams(self, params):
        if len(params) == 5:
            params_new = {'axes.labelsize'  : params[0],
                          'font.size'       : params[1],
                          'legend.fontsize' : params[2],
                          'xtick.labelsize' : params[3],
                          'ytick.labelsize' : params[4]}
        matplotlib.rcParams.update(params_new)
        self.updateCanvas()

    def setWH(self, width = 2, height = 2):
        self.figure.set_figwidth(width)
        self.figure.set_figheight(height)
        self.updateCanvas()

    def setDPI(self, dpi = None):
        if dpi:
            self.figure.dpi = dpi




