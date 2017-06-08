from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.image as mpimg
import matplotlib.pylab as plt
from PyQt4 import QtGui

def brush_to_color_tuple(brush):
    r, g, b, a = brush.color().getRgbF()
    return (r, g, b)

        

class MplCanvas(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        # We want the axes cleared every time plot() is called
        self.axes = self.fig.add_subplot(1, 1, 1)

        self.axes.hold(False)

        #FigureCanvas.__init__(self, fig)
        super(MplCanvas, self).__init__(self.fig)

        # self.figure
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self._title = ''
        self.title_font = {'family': 'serif', 'fontsize': 10}
        self._title_size = 0
        self.figure.subplots_adjust(top=0.95, bottom=0.15)

        window_brush = self.window().palette().window()
        self.fig.set_facecolor(brush_to_color_tuple(window_brush))
        self.fig.set_edgecolor(brush_to_color_tuple(window_brush))
        self._active = False
        
    def save(self,name):
        self.fig.savefig(name)