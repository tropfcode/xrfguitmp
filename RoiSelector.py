from matplotlib.widgets import  EllipseSelector, RectangleSelector, LassoSelector
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
from matplotlib import colors as mcolors, path

class RoiSelector():
    def __init__(self, axes, roi_type):
        self.axes = axes
        self.roi_type = roi_type
        self.patch = None
        self.lasso_switch = False
        self.verts = None
        if self.roi_type == 'rectangle':
            self.roi = RectangleSelector(self.axes, self.onselect, drawtype='box', interactive=True)
        elif self.roi_type == 'ellipse':
            self.roi = EllipseSelector(self.axes, self.onselect, drawtype='box', interactive=True)
        else:
            self.roi = LassoSelector(self.axes, onselect=self.lasso_select)
            self.lasso_switch = True
            
    def lasso_select(self, verts):
        if self.lasso_switch is False:
            return
        self.verts = verts
        self.p = path.Path(verts, closed=True)
        patch = patches.PathPatch(self.p, facecolor=(1, 0, 0, 0.3), lw=2)
        self.axes.add_patch(patch)
        self.axes.figure.canvas.draw()
        #self.lasso_switch = False
        
    def onselect(self, eclick, erelease):
        pass
            
    def label(self, label):
        if self.lasso_switch is True:
            xy = self.verts[0]
        else:
            xy = self.roi.center
        self.axes.annotate(label, xy=xy, 
                           bbox={'facecolor':'red', 'alpha':0.5, 'pad':10}, fontsize=10)
        self.axes.figure.canvas.draw()
            
    def visible(self, switch):
        if switch is True:
            self.roi.set_visible(True)
        if switch is False:
            self.roi.set_visible(False)
            
    def active(self, switch):
        self.roi.set_active(switch)
        
    def draw(self, extents):
        self.roi.extents = extents
        self.roi.set_visible(True)
        
    def draw_lasso(self):
        tmp = list(zip(self.roi.geometry[1], self.roi.geometry[0]))
        p = path.Path(tmp, closed=True)
        patch = patches.PathPatch(p, facecolor=(1, 1, 1, 0.3), lw=5)
        self.axes.add_patch(patch)
        self.axes.figure.canvas.draw()