from xrfGui_v2 import Ui_MainWindow
from PyQt4 import QtCore, QtGui
import matplotlib.pyplot as plt
import numpy as np
from MplCanvas import MplCanvas, brush_to_color_tuple
import matplotlib.image as mpimg
import sys
import functions as func
from pyxrf.api import (make_hdf)
import os
from matplotlib import interactive
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.axes_grid1 import make_axes_locatable
#import Lasso as lasso
from RoiSelector import RoiSelector
import RoiPopUp as roiPop
#%matplotlib qt

class ExampleApp(QtGui.QMainWindow, Ui_MainWindow):
    """
    This class connects buttons from the inherited Ui_MainWindow GUI to functions
    which will visualize, register, and analyze x-ray fluorescence data.
    It is intended that the functionality of buttons and the GUI itself be
    seperate for maximum flexibility and code adaptation.
    """
    
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)
    
        #Initialize Variables
        self.popup = None
        self.wd = os.getcwd()
        self.h5_file = ""
        self.json = ""
        self.imList = []
        self.horizontalSlider.setMaximum(len(self.imList))
        self.horizontalSlider.setMinimum(0)
        self.ref_img = np.array([])
        self.norm_img = np.array([])
        self.normBox = False
        self.alignBox = False
        self.data_list = []
        
        # Set tri-state false for all checkboxes
        self.checkBox.setTristate(False)
        self.checkBox_2.setTristate(False)
        self.checkBox_3.setTristate(False)
        self.checkBox_4.setTristate(False)
        self.checkBox_5.setTristate(False)
        self.checkBox_6.setTristate(False)
        
        #Setup Dock Widgets as Tabs (can't be done in qt designer)
        self.tabifyDockWidget(self.dockWidget_4, self.dockWidget)        
        
        #Create blank Images and display as placeholders
        self.canvas = MplCanvas(width=9,height=7)
        tmpLayout = QtGui.QHBoxLayout()
        #self.rlist = roiPop.RoiList()
        self.roiList = roiPop.RoiList(self.canvas.axes)
        tmpLayout.addWidget(self.roiList)
        blank = np.zeros((100, 100))
        tmp = mpimg.imread('numpy.png')
        self.blank_img = func.Im(blank)
        self.ref_canvas = MplCanvas()
        self.image = self.canvas.axes.imshow(tmp, cmap='jet')
        self.navi_toolbar = NavigationToolbar(self.canvas, self)
        #self.gridLayout_8.addWidget(self.navi_toolbar)
        self.image2 = self.ref_canvas.axes.imshow(tmp)
        tmpLayout.insertWidget(1, self.canvas)
        self.verticalLayout_4.insertWidget(0, self.navi_toolbar)
        #self.verticalLayout_4.insertWidget(1, self.canvas)
        self.verticalLayout_4.insertLayout(1, tmpLayout)
        self.verticalLayout_6.insertWidget(0, self.ref_canvas)
        divider = make_axes_locatable(self.canvas.axes)
        cax = divider.append_axes('right', size='5%', pad=0.05) # Set colorbar to right of image
        self.cb = self.canvas.fig.colorbar(self.image, cax = cax)
        #self.lman = lasso.LassoManager(self.canvas.axes, tmp)
        
        
        
        #Begin with no images displayed
        self.lineEdit_9.setText(str(0)+"/"+str(0))
        
        #Buttons for choosing ROI and deleting images from imList
        self.pushButton_21.clicked.connect(lambda: func.delete_im(self))
        
        #Data acquisition tab
        self.pushButton.clicked.connect(lambda: func.choose_wd(self))
        self.pushButton_2.clicked.connect(lambda: func.create_h5(self))    
        self.pushButton_3.clicked.connect(lambda: func.create_h5_from_file(self))
        self.pushButton_4.clicked.connect(lambda: func.choose_json(self))
        self.pushButton_5.clicked.connect(lambda: func.fit_h5(self))
        
        #Image operation tab
        self.pushButton_6.clicked.connect(lambda: func.choose_im(self))
        self.pushButton_9.clicked.connect(lambda: func.plot_crnt_im(self))
        self.pushButton_8.clicked.connect(lambda: func.choose_norm(self))
        self.pushButton_13.clicked.connect(lambda: func.choose_ref(self))
        self.pushButton_14.clicked.connect(lambda: func.plot_reference(self))
        self.pushButton_7.clicked.connect(lambda: func.choose_img_dir(self))
        self.pushButton_11.clicked.connect(lambda: func.plot_imgs(self))
        
        #Chemical analysis tab
        self.pushButton_19.clicked.connect(lambda: func.batch_registration(self))
        self.pushButton_20.clicked.connect(lambda: func.generate_roi_data(self))
        self.pushButton_15.clicked.connect(lambda: func.get_data(self))
        self.pushButton_25.clicked.connect(lambda: func.plot_all_data(self))
        
        #Primary Dock Widget
        self.horizontalSlider.valueChanged.connect(lambda: func.slider_change(self))
        self.checkBox_5.clicked.connect(lambda: func.make_ref_align_box(self))
        self.checkBox_6.clicked.connect(lambda: func.make_ref_norm_box(self))
        self.pushButton_22.clicked.connect(lambda: func.delete_all(self))
        self.pushButton_17.clicked.connect(lambda: func.remove_data(self))
        
        
        #Image Augmentation
        self.checkBox.clicked.connect(lambda: func.align_check(self))
        self.checkBox_2.clicked.connect(lambda: func.normalize_check(self))
        
        # Roi stuff
        self.pushButton_10.clicked.connect(lambda: func.compute_roiList_intensity(self))
        
def main():
    app = QtGui.QApplication(sys.argv)
    form = ExampleApp()
    form.setGeometry(50, 50, 2000, 1200)
    form.show()
    app.exec_()
    
if __name__ == '__main__':
    main()