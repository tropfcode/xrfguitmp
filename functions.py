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

"""
    Must make sure that all required files -- .json, .h5 -- are in the same
    directory as the wd.
    It seems that due to how fit_pixel_data_and_save was made that
    the h5_file needs to be inside the obj.wd else the function will no work
    properly. Talk to Li and see if a user is capable of choosing a different directory
    to save the results to.
"""

class Image():
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
        
        
#Choose Working Directory        
def choose_wd(obj):
    """
    Choose working directory where saved data is placed
    """
    try:
        wd = str(QtGui.QFileDialog.getExistingDirectory(obj.centralwidget, 'Open File'))
        if wd == "":
            wd = obj.wd 
        obj.lineEdit.setText(wd)
        obj.wd = wd
        obj.textEdit.append("Chose the Directory "+obj.wd)
    except:
        obj.textEdit.append("Choose Directory Error: Must choose proper directory")
    
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
        obj.textEdit.append("Make hdf Error: Provide hdf number (only a number)")

#AFter talkign to Li, make sure to test proper error handling for improper file selection        
def create_h5_from_file(obj):
    #try:
        h5_file = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
        obj.lineEdit_3.setText(h5_file)
        obj.textEdit.append('File for batch h5 creation: ' + h5_file)
        f = open(h5_file, 'r') 
        lines = f.readlines()
        #try:
        for line in lines:
            make_hdf(int(line))
        #except:
            #obj.textEdit.append('Create h5 from file Error: ' + 
            #                    'Need proper hdf index number or file or number already exists')
    #except:
       # obj.textEdit.append('Create h5 from file Error: ' + 
        #                    'Choose an appropriate file or make sure that file is proper format')

        
        
def choose_json(obj):
    try:
        word = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
        if "json" not in word:
            obj.textEdit.append("Error: File must be of type .json")
            return

        obj.lineEdit_4.setText(word)
        obj.json = word
        obj.textEdit.append("Chose json file "+obj.json)
    except:
        obj.textEdit.append("Choose json Error: Must choose proper directory")

        
def fit_h5(obj):
    try:
        h5_path = (str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File')))
        h5_file = os.path.basename(h5_path)
        obj.lineEdit_5.setText(h5_path)
        fit_pixel_data_and_save(obj.wd, h5_file, param_file_name = os.path.basename(obj.json))
        obj.textEdit.append("Chose " + h5_path + " for fitting")
    except:
        obj.textEdit.append("fit_h5 Error: Make sure to choose proper .json and h5 files")
    
        
def choose_im(obj):
    try:
        im_path = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
        if im_path == '':
            obj.textEdit.append("Image not chosen")
            return
        obj.lineEdit_6.setText(im_path)
        obj.textEdit.append("Chose image " + im_path)
    except:
        obj.textEdit.append("Choose Image Error: Must choose an image (tiff, jpeg, etc.)")
                
def plot_crnt_im(obj):
    try:
        im_path = obj.lineEdit_6.text()
        if im_path == '':
            obj.textEdit.append("Plot Current Image Error: Must choose an image to plot")
            return
        img = mpimg.imread(im_path)
        img_obj = Image(img, title = os.path.basename(im_path), f = im_path)
        obj.imList.append(img_obj)
        obj.horizontalSlider.setMaximum(len(obj.imList)-1)
        obj.horizontalSlider.setValue(obj.horizontalSlider.maximum())
        if len(obj.imList) == 1:
            plot_im(obj, img_obj)
    except:
        obj.textEdit.append("Plot Current Image Error: Must choose an image (tiff, jpeg, etc.)")        
        
        
def slider_change(obj):
    imgNum = obj.horizontalSlider.sliderPosition()
    img = obj.imList[imgNum]
    obj.lineEdit_9.setText(str(imgNum)+"/"+str(obj.horizontalSlider.maximum()))
    checkBoxes(obj, img)
    plot_im(obj, img)

#Ask Tom about best way to handle updating data of different shape
def plot_im(obj, img):
    if img.state > 0:
        array = img.img_array2
    else:
        array = img.im_array
    obj.label.setText(img.title)
    obj.label_2.setText(img.f)
    obj.canvas.fig.clear()
    obj.canvas.ax = obj.canvas.fig.add_subplot(1,1,1,)
    image = obj.canvas.ax.imshow(array)
    #obj.image.set_data(array)
    #obj.canvas.axes.autoscale()
    #obj.canvas.axes.set_ylim([0,array.shape[0]])
    #obj.canvas.axes.set_xlim([0,array.shape[1]])
    #obj.image.set_clim(vmin = np.min(array), vmax=np.max(array))
    
    divider = make_axes_locatable(obj.canvas.axes)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    obj.canvas.fig.colorbar(image, cax = cax)
    obj.canvas.fig.canvas.draw()
               
def choose_norm(obj):
    try:        
        img_path = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
        if img_path == '':
            obj.textEdit.append("No normalization image chosen")
            return
        obj.norm_img = mpimg.imread(img_path)
        obj.textEdit.append("Chose normalization image " + img_path)
        obj.lineEdit_7.setText(img_path)
    except:
        obj.textEdit.append("Choose Noralmization Error: Must choose an image (tiff, jpeg, etc.)")
        
def choose_ref(obj):
    try:        
        img_path = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
        if img_path == '':
            obj.textEdit.append("No reference image chosen")
            return
        obj.ref_img = mpimg.imread(img_path)
        obj.textEdit.append("Chose reference image " + img_path)
        obj.lineEdit_12.setText(img_path)
    except:
        obj.textEdit.append("Choose Reference Error: Must choose an image (tiff, jpeg, etc.)")
        
def plot_ref(obj, im_array):
    try:
        obj.canvas2.axes.imshow(im_array)
        obj.canvas2.fig.canvas.draw()
    except:
        obj.textEdit.append("Plot Reference Error: Make sure an image was chosen to plot (tiff, jpeg, etc.)")
    
def choose_img_dir(obj):
    path = str(QtGui.QFileDialog.getExistingDirectory(obj.centralwidget, 'Open File'))
    if path == '':
        obj.textEdit.append("No directory chosen")
        return
    obj.lineEdit_8.setText(path)
    
def plot_imgs(obj):
    #try:
        path = obj.lineEdit_8.text()
        if path == '':
            obj.textEdit.append("Must choose directory first")
            return
        for fi in os.listdir(path):
            im_path = os.path.join(path, fi)
            obj.textEdit.append(fi)
            img = mpimg.imread(im_path)
            img_obj = Image(img, title=fi, f=im_path)
            obj.imList.append(img_obj)
            obj.horizontalSlider.setMaximum(len(obj.imList)-1)
            obj.horizontalSlider.setValue(obj.horizontalSlider.maximum())
        if len(obj.imList) == 1:
            plot_im(obj, img_obj)
    #except:
       # obj.textEdit.append("Plot Images Error: Make sure all files are images (tiff, jpeg, etc.)")
        
#Normalization is pixel by pixel division
def normalize(array1, array2):
    rtn_array = np.divide(array2, array1)
    return rtn_array
    
def normalize_obj(obj):
    img = obj.imList[obj.horizontalSlider.value()]
    if img.state > 0:
        img.img_array2 = normalize(obj.norm_img, img.img_array2)
    else:
        img.img_array2 = normalize(obj.norm_img, img.im_array)
    img.norm_check = True
    img.norm_array = obj.norm_img
    plot_im(obj, img)
    
def unNormalize(obj):
    img = obj.imList[obj.horizontalSlider.value()]
    if img.state > 0:
        img.img_array2 = np.multiply(img.img_array2,img.norm_array)
    else:
        img.img_array2 = img.im_array
    img.norm_check = False
    plot_im(obj, img)
    
def normalize_check(obj):
    img = obj.imList[obj.horizontalSlider.value()]
    #Normalizing Image
    if obj.checkBox_2.isChecked():
        if obj.norm_img.size == 0:
            obj.textEdit.append("Need to choose an image to normalize by")
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
    
def align(ref_array, align_array):
    img, x_shift, y_shift = ac.subpixel_align(ref_array, align_array, 0, 0, 1)
    return img, x_shift, y_shift

def align_obj(obj):
    img = obj.imList[obj.horizontalSlider.value()]
    if img.state == 2:
        tmp_array = img.img_array2
        img.state = 3
    else:
        tmp_array = img.im_array
        img.state = 1
    tmp_array, x_shift, y_shift = align(obj.ref_img, tmp_array)
    img.img_array2 = tmp_array.real
    img.x_shift = x_shift
    img.y_shift = y_shift
    plot_im(obj, img)
    
    
def align_check(obj):
    img = obj.imList[obj.horizontalSlider.value()]
    if obj.checkBox.isChecked():
        if obj.ref_img.size == 0:
            obj.textEdit.append("Need to choose an image to normalize by")
            obj.checkBox.setCheckState(False)
            return
        if obj.checkBox_2.isChecked():
            img.state = 3
        else:
            img.state = 1
        align_obj(obj)
    else:
        handleImageInverse(obj, unAl = True)
           
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
    
    
def unAlignTrue(array, x_shift, y_shift):
    array = ac.pixel_shift_2d(array, (-1)*img.x_shift, (-1)*img.y_shift)
    return array  
    
    
def checkBoxes(obj, img):    
    #Deal with Normalization Button
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
            img.state = 2
            unAlign(obj)
    #Aligned then Normalized
    else:
        if unAl is True:
            img.norm_array = ac.pixel_shift_2d(img.norm_array, img.x_shift, img.y_shift)
            img.img_array2 = ac.pixel_shift_2d(img.img_array2, (-1)*img.x_shift, (-1)*img.y_shift)
            img.state = 2
        else:
            img.state = 1
            unNormalize(obj)
    