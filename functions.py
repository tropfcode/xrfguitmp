from xrfGui_v0 import Ui_MainWindow
from PyQt4 import QtCore, QtGui
from pyxrf.model.command_tools import fit_pixel_data_and_save
from pyxrf.api import (make_hdf)
import os
import sys
import scipy.misc as mpimg#matplotlib.image as mpimg
import numpy as np
import matplotlib.pyplot as plt
import align_class as ac
from mpl_toolkits.axes_grid1 import make_axes_locatable
from PIL import Image

"""
    Must make sure that all required files -- .json, .h5 -- are in the same
    directory as the wd.
    It seems that due to how fit_pixel_data_and_save was made that
    the h5_file needs to be inside the obj.wd else the function will no work
    properly. Talk to Li and see if a user is capable of choosing a different directory
    to save the results to.
"""

class Im():
    def __init__(self, im_array, ref_check = False, norm_check = False, align_check = False,
                title = "N/A", f = "N/A", x_shift=0, y_shift=0):
        self.im_array = im_array
        self.img_array2 = im_array
        self.norm_array = np.empty(shape=(0,0))
        self.ref_check = ref_check
        self.norm_check = norm_check
        self.align_check = align_check
        self.title = title
        self.f = f
        self.x_shift = x_shift
        self.y_shift = y_shift
        self.state = 0
        self.align_global = False
        self.norm_global = False
        
    def get_state(self):
        return self.state
    
    def get_title(self):
        return self.title
    
    def get_file(self):
        return self.f
        
        
#Choose Working Directory        
def choose_wd(obj):
    """
    Choose working directory where saved data is placed
    """
    try:
        wd = str(QtGui.QFileDialog.getExistingDirectory(obj.centralwidget, 'Open File'))
        if wd == '':
            wd = obj.wd 
            return
        obj.lineEdit.setText(wd)
        obj.wd = wd
        msg(obj, "Chose the Directory "+obj.wd)
    except:
        msg(obj, "Choose Directory Error: Must choose proper directory")
    
#Ask Li about using make_hdf function such in order to save in a desired directory    
def create_h5(obj):
    """
    Create h5 file by pulling data from NSLS-II via specific hdf number
    """
    try:
        hdf_num = obj.lineEdit_2.text()
        #make_hdf(int(hdf_num), end=int(hdf_num), fname=obj.wd)
        make_hdf(int(hdf_num))
    except:
        msg(obj, "Make hdf Error: Provide hdf number (only a number)")

#AFter talkign to Li, make sure to test proper error handling for improper file selection        
def create_h5_from_file(obj):
    #try:
        h5_file = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
        obj.lineEdit_3.setText(h5_file)
        msg(obj, 'File for batch h5 creation: ' + h5_file)
        f = open(h5_file, 'r') 
        lines = f.readlines()
        #try:
        for line in lines:
            make_hdf(int(line))
        #except:
            #msg(obj, 'Create h5 from file Error: ' + 
            #                    'Need proper hdf index number or file or number already exists')
    #except:
       # msg(obj, 'Create h5 from file Error: ' + 
        #                    'Choose an appropriate file or make sure that file is proper format')

        
        
def choose_json(obj):
    try:
        word = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
        if 'json' not in word:
            msg(obj, "Error: File must be of type .json")
            return
        obj.lineEdit_4.setText(word)
        obj.json = word
        msg(obj, "Chose json file "+obj.json)
    except:
        msg(obj, "Choose json Error: Must choose proper directory")

        
def fit_h5(obj):
    try:
        h5_path = (str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File')))
        h5_file = os.path.basename(h5_path)
        obj.lineEdit_5.setText(h5_path)
        fit_pixel_data_and_save(obj.wd, h5_file, param_file_name = os.path.basename(obj.json))
        msg(obj, "Chose " + h5_path + " for fitting")
    except:
        msg(obj, "fit_h5 Error: Make sure to choose proper .json and h5 files")
    
        
def choose_im(obj):
    try:
        im_path = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
        if im_path == '':
            msg(obj, "Image not chosen")
            return
        obj.lineEdit_6.setText(im_path)
        msg(obj, "Chose image " + im_path)
    except:
        msg(obj, "Choose Image Error: Must choose an image (tiff, jpeg, etc.)")
                
def plot_crnt_im(obj):
    try:
        im_path = obj.lineEdit_6.text()
        if im_path == '':
            msg(obj, "plot_crnt_im Error: Must choose an image to plot")
            return
        img = mpimg.imread(im_path)
        img_obj = Im(img, title = os.path.basename(im_path), f = im_path)
        obj.imList.append(img_obj)
        obj.horizontalSlider.setMaximum(len(obj.imList)-1)
        obj.horizontalSlider.setValue(obj.horizontalSlider.maximum())
        if len(obj.imList) == 1:
            plot_im(obj, img_obj)
    except:
        msg(obj, "plot_crnt_im Error: Must choose an image (tiff, jpeg, etc.)")        
        
        
def slider_change(obj):
    imgNum = obj.horizontalSlider.sliderPosition()
    img = obj.imList[imgNum]
    obj.lineEdit_9.setText(str(imgNum)+"/"+str(obj.horizontalSlider.maximum()))
    checkBoxes(obj, img)
    textLabels(obj, img)
    plot_im(obj, img)

#Ask Tom about best way to handle updating data of different shape
#Still have issue with set_data. Actual image does not show up,
#instead it is just points, no image
def plot_im(obj, img):
    if img.get_state() > 0:
        array = img.img_array2
    else:
        array = img.im_array
    #obj.label.setText(img.get_title())
    #obj.label_2.setText(img.get_file())
    #obj.canvas.fig.clear()
    #obj.canvas.ax = obj.canvas.fig.add_subplot(1,1,1,)
    #image = obj.canvas.ax.imshow(array, cmap='jet')
    obj.image.set_data(array)
    obj.image.set_extent((0, array.shape[0], array.shape[1], 0))
    obj.image.set_clim(vmin=np.amin(array), vmax=np.amax(array))
    #divider = make_axes_locatable(obj.canvas.axes)
    #cax = divider.append_axes('right', size='5%', pad=0.05)
    #obj.canvas.fig.colorbar(obj.image, cax = cax)
    obj.cb.set_clim(vmin=np.amin(array), vmax=np.amax(array))
    obj.cb.draw_all()
    obj.canvas.fig.canvas.draw()

#Choose image to normalize by via button in Image Operation tab
def choose_norm(obj):
    try:        
        img_path = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
        if img_path == '':
            msg(obj, "No normalization image chosen")
            return
        if type(obj.norm_img) is Im:
            obj.norm_img.norm_global = False
        obj.norm_img = Im(mpimg.imread(img_path))
        obj.norm_img.norm_global = True
        msg(obj, "Chose normalization image " + img_path)
        obj.lineEdit_7.setText(img_path)
        obj.checkBox_6.setCheckState(False)
    except:
        msg(obj, "choose_norm Error: Must choose an image (tiff, jpeg, etc.)")

#Choose image to align by via button in Image Operation tab        
def choose_ref(obj):
    try:        
        img_path = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
        if img_path == '':
            msg(obj, "No reference image chosen")
            return
        if type(obj.ref_img) is Im:
            obj.ref_img.align_global = False
        obj.ref_img = Im(mpimg.imread(img_path))
        obj.ref_img.align_globabl = True
        msg(obj, "Chose reference image " + img_path)
        obj.lineEdit_12.setText(img_path)
        obj.checkBox_5.setCheckState(False)
    except:
        msg(obj, "choose_ref Error: Must choose an image (tiff, jpeg, etc.)")
        
        
def plot_reference(obj):
    try:
        new_im = Im(mpimg.imread(obj.lineEdit_12.text()))
        if type(obj.ref_img) is Im:
            obj.ref_img.align_global = False
            obj.checkBox_5.setCheckState(False)
            obj.ref_img = new_im
            plot_ref(obj, obj.ref_img.im_array)
        else:
            msg(obj, "plot_reference Error: Must choose a reference image first")
    except:
        msg(obj, "plot_reference Error: Must choose a reference image first")

#Error occurs when plotting for the very first time, however does not show after that
#Unknown cause, look into this later
def plot_ref(obj, im_array):
    try:
        obj.canvas2.axes.imshow(im_array)
        obj.canvas2.fig.canvas.draw()
    except:
        msg(obj, "plot_ref Error: Make sure an image was chosen to plot (tiff, jpeg, etc.)")
    
def choose_img_dir(obj):
    path = str(QtGui.QFileDialog.getExistingDirectory(obj.centralwidget, 'Open File'))
    if path == '':
        msg(obj, "No directory chosen")
        return
    obj.lineEdit_8.setText(path)
    
def plot_imgs(obj):
    try:
        path = obj.lineEdit_8.text()
        if path == '':
            msg(obj, "Must choose directory first")
            return
        for fi in os.listdir(path):
            im_path = os.path.join(path, fi)
            msg(obj, fi)
            img = mpimg.imread(im_path)
            img_obj = Im(img, title=fi, f=im_path)
            obj.imList.append(img_obj)
        if len(obj.imList) == 1:
            plot_im(obj, img_obj)
        else:
            obj.horizontalSlider.setMaximum(len(obj.imList)-1)
            obj.horizontalSlider.setValue(obj.horizontalSlider.maximum())
    except:
        msg(obj, "plot_imgs Error: Make sure all files are images (tiff, jpeg, etc.)")
        
#Normalization is pixel by pixel division
def normalize(array1, array2):
    rtn_array = np.divide(array2, array1)
    return rtn_array
    
def normalize_obj(obj):
    img = obj.imList[obj.horizontalSlider.value()]
    if img.get_state() > 0:
        img.img_array2 = normalize(obj.norm_img.img_array2, img.img_array2)
    else:
        img.img_array2 = normalize(obj.norm_img.im_array, img.im_array)
    img.norm_check = True
    img.norm_array = obj.norm_img.im_array
    plot_im(obj, img)
    
def unNormalize(obj):
    img = obj.imList[obj.horizontalSlider.value()]
    if img.state > 0:
        print(type(img.img_array2), type(img.norm_array))
        img.img_array2 = np.multiply(img.img_array2,img.norm_array)
    else:
        img.img_array2 = img.im_array
    img.norm_check = False
    plot_im(obj, img)

#Handle normalization checkbox
def normalize_check(obj):
    if len(obj.imList) is 0:
        msg(obj, "normalize_check Error: Need to plot image in order to normalize it")
        obj.checkBox_2.setCheckState(False)
        return
    img = obj.imList[obj.horizontalSlider.value()]
    #Normalizing Image
    if obj.checkBox_2.isChecked():
        if type(obj.norm_img) is not Im:
            msg(obj, "normalize_check Error: Need to choose an image to normalize by")
            obj.checkBox_2.setCheckState(False)
            return
        if obj.norm_img.img_array2.shape != img.img_array2.shape:
            msg(obj, "normalize_check Error: Normalizing Image and current image need to have same shape")
            obj.checkBox_2.setCheckState(False)
            return
        if obj.checkBox.isChecked():
            img.state = 4
        else:
            img.state = 2
        normalize_obj(obj)
    else:
        #Unnormalize Image
        handleImageInverse(obj, unNor=True)
        
def make_ref_norm_box(obj):
    if len(obj.imList) == 0:
        msg(obj, "Need to plot an image first")
        obj.checkBox_6.setCheckState(False)
    else:
        img = obj.imList[obj.horizontalSlider.value()]
        if obj.checkBox_6.isChecked():
            if img.norm_global is False:
                img.norm_global = True
                if type(obj.norm_img) is Im:
                    obj.norm_img.norm_global = False
                obj.norm_img = img
        else:
            obj.norm_img.norm_global = False

def align(ref_array, align_array):
    img, x_shift, y_shift = ac.subpixel_align(ref_array, align_array, 0, 0, 1)
    return img, x_shift, y_shift

def align_obj(obj):
    img = obj.imList[obj.horizontalSlider.value()]
    if img.state == 3:
        tmp_array = img.img_array2
    else:
        tmp_array = img.im_array
    tmp_array, x_shift, y_shift = align(obj.ref_img.im_array, tmp_array)
    img.img_array2 = tmp_array.real
    img.x_shift = x_shift
    img.y_shift = y_shift
    plot_im(obj, img)
    textLabels(obj, img)
    
#Handle alignment checkbox    
def align_check(obj):
    if len(obj.imList) is 0:
        msg(obj, "align_check Error: Need to plot image in order to align it")
        obj.checkBox.setCheckState(False)
        return
    img = obj.imList[obj.horizontalSlider.value()]
    if obj.checkBox.isChecked():
        if type(obj.ref_img) is not Im:
            msg(obj, "Need to choose reference image to align by")
            obj.checkBox.setCheckState(False)
            return
        if obj.checkBox_2.isChecked():
            img.state = 3
        else:
            img.state = 1
        align_obj(obj)
    else:
        handleImageInverse(obj, unAl = True)
           
def make_ref_align_box(obj):
    if len(obj.imList) == 0:
        msg(obj, "Need to plot an image first")
        obj.checkBox_5.setCheckState(False)
    else:
        img = obj.imList[obj.horizontalSlider.value()]
        if obj.checkBox_5.isChecked():
            if img.align_global is False:
                img.align_global = True
                if type(obj.ref_img) is Im:
                    obj.ref_img.align_global = False
                obj.ref_img = img
        else:
            obj.ref_img.align_global = False
        if obj.ref_img.state != 0:
            plot_ref(obj, obj.ref_img.img_array2)
        else:
            plot_ref(obj, obj.ref_img.im_array)
           
            
def unAlign(obj):
    img = obj.imList[obj.horizontalSlider.value()]
    if img.state is 3:
        img.img_array2 = ac.pixel_shift_2d(img.img_array2, (-1)*img.x_shift, (-1)*img.y_shift)
    else:
        img.img_array2 = img.im_array
    img.x_shift = 0
    img.y_shift = 0
    img.align_check = False
    plot_im(obj, img)
    textLabels(obj, img)
    
    
def unAlignTrue(array, x_shift, y_shift):
    array = ac.pixel_shift_2d(array, (-1)*img.x_shift, (-1)*img.y_shift)
    return array  
    
    
def checkBoxes(obj, img):  
    #Handle combination of normalization and alignment for displayed image
    if img.state is 0:
        obj.checkBox.setCheckState(False)
        obj.checkBox_2.setCheckState(False)
    elif img.state is 1:
        obj.checkBox.setCheckState(True)
        obj.checkBox_2.setCheckState(False)
    elif img.state is 2:
        obj.checkBox.setCheckState(False)
        obj.checkBox_2.setCheckState(True)
    else:
        obj.checkBox.setCheckState(True)
        obj.checkBox_2.setCheckState(True)
        
    #Handle if displayed image is reference image for alignment    
    if img.align_global is False:
        obj.checkBox_5.setCheckState(False)
    else:
        obj.checkBox_5.setCheckState(True)
        
    #Handle if displayed image is reference image for normalization
    if img.norm_global is False:
        obj.checkBox_6.setCheckState(False)
    else:
        obj.checkBox_6.setCheckState(True)
    
    
def handleImageInverse(obj, unNor = False, unAl = False):
    img = obj.imList[obj.horizontalSlider.value()]
    #Aligned only, now unAlign
    if img.state is 1:
        img.state = 0
        unAlign(obj)
    #Normalized only, now unNormalize
    elif img.state is 2:
        img.state = 0
        unNormalize(obj)
    #Normalized then Aligned
    elif img.state is 3:
        if unNor is True:
            img.img_array2 = ac.pixel_shift_2d(img.im_array, img.x_shift, img.y_shift)
            img.state = 1
        else:
            unAlign(obj)
            img.state = 2
    #Aligned then Normalized
    elif img.state is 4:
        if unAl is True:
            img.norm_array = ac.pixel_shift_2d(img.norm_array, img.x_shift, img.y_shift)
            img.img_array2 = ac.pixel_shift_2d(img.img_array2, (-1)*img.x_shift, (-1)*img.y_shift)
            img.state = 2
        else:
            img.state = 1
            unNormalize(obj)
            
def textLabels(obj, img):
    obj.label.setText("Title: "+img.get_title())
    obj.label_2.setText("File Path: "+img.f)
    obj.label_3.setText("Pixel Shift: ("+str(img.x_shift)+","+str(img.y_shift)+")")            

"""
#Reshape two Im objects, always scaling up smaller object            
def resizeIms(im1, im2):
    pass

def resize(im, x, y):
    temp_im = Image.fromarray(im)
    im2 = Image.fromarray(arr2)
    #im1 = im1.resize((100, 100))
"""

def msg(obj, msgStr):
    obj.textEdit.append("->"+msgStr)
    
            
            
            
    