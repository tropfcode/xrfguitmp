from matplotlib.widgets import Lasso
from matplotlib.collections import RegularPolyCollection
from matplotlib import colors as mcolors, path
import matplotlib.patches as patches
import numpy as np
import math
from implementation import ExampleApp as obj
import functions as func

class LassoManager():

    def __init__(self, ax, data):
        self.axes = ax
        self.canvas = ax.figure.canvas
        self.data = data
        self.cid = self.canvas.mpl_connect('button_press_event', self.onpress)
        self.switch = False
        self.patch = patches.PathPatch(path.Path.circle())

    def callback(self, verts):
        if self.switch is True:
            self.patch.remove()
        self.p = path.Path(verts, closed=True)
        #self.patch = patches.PathPatch(self.p, facecolor=(1, 0, 0, 0.3), lw=2)
        self.patch = patches.Circle((50, 50), radius=5)
        self.axes.add_patch(self.patch)
        self.canvas.draw_idle()
        self.canvas.widgetlock.release(self.lasso)
        for vert in self.p.vertices:
            if math.isnan(vert[0]) or math.isnan(vert[1]):
                detailStr = "When choosing an ROI make sure to release the mouse within the\
                             limits of the image. No ROI is currently chosen for analysis until\
                             an ROI has been properly chosen."
                func.errorMsg("Release mouse on image", detailStr)
                #if self.patch:
                self.patch.set_visible(False)
                self.patch.remove()
                self.switch = False
                del self.lasso
                self.canvas.draw()
                return
     
        self.patch.set_visible(True)
        self.switch = True
        del self.lasso

    def onpress(self, event):
        if self.canvas.widgetlock.locked():
            return
        if event.inaxes is None:
            return
        self.lasso = Lasso(event.inaxes,
                           (event.xdata, event.ydata),
                           self.callback)
    
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)
        
    def hide_roi(self):
        self.patch.set_visible(False)
        self.canvas.draw()
        
    def show_roi(self, patch = None):
        if patch != None:
            try:
                self.patch.remove()
            except:
                func.msg("show_roi: No extra patch to remove")
            self.patch = patch
            self.axes.add_patch(self.patch)
        self.switch = True
        self.patch.set_visible(True)
        self.canvas.draw()
        
    def save_roi(self):
        minx = int(round(np.amin(self.patch.get_path().vertices[:,0])))
        maxx = int(round(np.amax(self.patch.get_path().vertices[:,0])))
        miny = int(round(np.amin(self.patch.get_path().vertices[:,1])))
        maxy = int(round(np.amax(self.patch.get_path().vertices[:,1])))
        intensity = 0
        for row in range(miny, maxy):
            for col in range(minx, maxx):
                if self.patch.get_path().contains_point((col, row)):
                    intensity = self.data[row][col] + intensity
        return intensity, self.patch
        