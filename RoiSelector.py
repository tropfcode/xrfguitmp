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
        self.title = 'N/A'
        self.annotate = None
        self.global_switch = False
        if self.roi_type == 'rectangle':
            self.roi = RectangleSelector(self.axes, self.onselect, drawtype='box', interactive=True)
        elif self.roi_type == 'ellipse':
            self.roi = EllipseSelector(self.axes, self.onselect, drawtype='box', interactive=True)
        else:
            self.roi = LassoSelector(self.axes, onselect=self.lasso_select)
            
    def lasso_select(self, verts):
        if self.global_switch is False:
            del self.roi
            self.roi = LassoSelector(self.axes, onselect=self.lasso_select)
            self.axes.figure.canvas.draw()
            return
        if self.lasso_switch is True:
            self.patch.remove()
        self.verts = verts
        self.p = path.Path(verts, closed=True)
        self.patch = patches.PathPatch(self.p, facecolor=(1, 0, 0, 0.3), lw=2)
        self.axes.add_patch(self.patch)
        self.lasso_switch = True
        if self.annotate != None:
            self.annotate.remove()
        self.label(self.title)
        
    def onselect(self, eclick, erelease):
        if erelease:
            if self.annotate != None:
                self.annotate.remove()
            self.label(self.title)
            
    def label(self, label):
        if self.lasso_switch is True:
            if self.verts is None:
                return
            xy = self.verts[0]
        else:
            xy = self.roi.center
        self.annotate = self.axes.annotate(label, xy=xy, 
                           bbox={'facecolor':'red', 'alpha':0.5, 'pad':10}, fontsize=10)
        self.axes.figure.canvas.draw()
            
    def visible(self, switch):
        if switch is True:
            if self.annotate != None:
                self.annotate.remove()
                self.annotate = None
            self.roi.set_visible(True)
            self.label(self.title)
        if switch is False:
            if self.annotate != None:
                self.annotate.remove()
                self.annotate = None
            self.roi.set_visible(False)
        self.axes.figure.canvas.draw()
            
    def active(self, switch):
        self.roi.set_active(switch)
        
    def draw(self, extents):
        self.roi.extents = extents
        self.roi.set_visible(True)
    
    def hide_lasso(self):
        pass
    
    def lasso_visible(self, switch):
        if self.patch is None:
            return
        self.patch.set_visible(switch)
        if switch is False:
            if self.annotate != None:
                if self.annotate.get_visible():
                    self.annotate.remove()
                    self.annotate = None
            self.axes.figure.canvas.draw()
        else:
            self.label(self.title)
        
    def remove_lasso(self):
        self.patch.remove()
            