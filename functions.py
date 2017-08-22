from xrfGui_v1 import Ui_MainWindow
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
import RoiSelector as roiSelect
import RoiPopUp as roiPop
import PlotClass as pc

#This file contains functions which are tied to buttons of a GUI developed in QtDesigner.
#All functions take 'obj' as a parameter which is an instance of a Ui_MainWindow object.
#This is necessary as all functions in this file are connected via lambda functions.

"""
    Must make sure that all required files -- .json, .h5 -- are in the same
    directory as the wd.
    It seems that due to how fit_pixel_data_and_save was made that
    the h5_file needs to be inside the obj.wd else the function will no work
    properly. Talk to Li and see if a user is capable of choosing a different directory
    to save the results to.
"""

def compute_intensity(roi_obj, data):
    intensity = roi_obj.roi.sum_roi(data)
    return intensity

def compute_roiList_intensity(obj):
    data = obj.imList[obj.horizontalSlider.value()].img_array2
    for roi in obj.roiList.roi_list:
        intensity = compute_intensity(roi, data)
        roi.intenLabel.setText(str(intensity))
        
def get_data(obj):
    #try:
    path = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
    name = os.path.basename(path)
    obj.comboBox.insertItem(len(obj.data_list), name)
    f = open(path, 'r')
    xdata = []
    ydata = []
    for line in f:
        line = line.strip('\n')
        line = line.split(' ')
        print(line[0], line[1])
        xdata.append(float(line[0]))
        ydata.append(float(line[1]))
    msg(obj, "Chose "+name+" for plotting")
    obj.data_list.append((xdata, ydata))
    #except:
    msg(obj, "get_data error")
        
def plot_all_data(obj):
    plotObj = pc.PlotClass(obj.data_list, title="All Data")
    plotObj.show()
        
class Im():
    """
    This class manages an x-ray fluorescence image's state altered by image operations.
    If data is to be normalized, aligned, or any combination thereof a copy of the data is made
    with those changes made to the copy keeping the original data unchanged.
    """
    def __init__(self, im_array, ref_check = False, norm_check = False, align_check = False,
                title = "N/A", f = "N/A", x_shift=0, y_shift=0):
        """
        Parameters
        ----------
        
        im_array: 2D numpy array
            Required parameter that is never augmented.
            
        ref_check: Boolean
            If True, then data of object instantiaed from this class is used as reference for alignment.
            
        norm_check: Boolean
            If True, data has been normalized
            
        align_check: Boolean
            If True, data has been aligned
            
        title: String
            Title of data/image.
            
        f: String
            Full file path from which data was acquired
            
        x_shift: float
            Pixel amount data has been shifted along x-axis
            
        y_shift: float
            Pixel amount data has been shifted along y-axis
            
        Other Attributes
        ----------------
        
        state: int
            Can take values 0 to 4. 
            0 means no change to data has been made. 
            1 means image aligned only.
            2 means image normalized only. 
            3 means image normalized and then aligned. 
            4 means image aligned and then normalized.
            
        patch: matplotlib.patches.Patch
            Patch object that holds ROI information. Used to visually show ROI on image and collect
            data from ROI for analysis.
            
        intensity: float
            Total summed value from pixels within ROI.
            
        """
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
        self.patch = None
        self.intensity = 0

        
def msg(obj, msgStr):
    """
    Displays message in 'message and error box'.
    
    Parameters
    ----------
    msgStr: String
        Message to be displayed in aforementioned box.
    """
    obj.textEdit.append("->"+msgStr)
    
def errorMsg(msgStr, detailStr):
    """
    Message displayed in popup window
    
    Parameters
    ----------
    msgStr: String
        Concise message to quickly convey the error or message 
       
    detailStr: String
        More detailed message that further elaborates on the error
    """
    msg = QtGui.QMessageBox()
    msg.setIcon(QtGui.QMessageBox.Information)
    msg.setText(msgStr)
    msg.setInformativeText("Press Show Details for more Information")
    msg.setWindowTitle("Warning Message")
    msg.setDetailedText(detailStr)
    msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
    retval = msg.exec_()      
       
def delete_im(obj, value=None):
    """
    Deletes currently viewed image from imList and updates canvas to display next image in imList.
    The image count is also updated. If imList is empty then nothing happens.
    """
    if len(obj.imList) is 0:
        msg(obj, "delete_im Error: No image to delete")
    else:
        if value is not None:
            slide_num = value
        else:
            slide_num = obj.horizontalSlider.value()
        if slide_num < obj.horizontalSlider.maximum():
            msg(obj, "Deleted the following image: "+str(obj.imList[slide_num].title))
            del obj.imList[slide_num]
            #obj.horizontalSlider.setValue(slide_num)
            slider_change(obj)
        else:
            msg(obj, "Deleted the following image: "+str(obj.imList[slide_num].title))
            del obj.imList[slide_num]
            slide_num=slide_num-1
            obj.horizontalSlider.setValue(obj.horizontalSlider.maximum())
        if len(obj.imList) is 0:
            obj.horizontalSlider.setMaximum(len(obj.imList))
            plot_im(obj, obj.blank_img)
            textLabels(obj, obj.blank_img)
        else:
            obj.horizontalSlider.setMaximum(len(obj.imList)-1)
            #plot_im(obj, obj.imList[slide_num])
        obj.lineEdit_9.setText(str(obj.horizontalSlider.value())+"/"+str(obj.horizontalSlider.maximum()))
        
def delete_all(obj):
    """
    Deletes all images in imList. Size of imList becomes zero and image counter is updated.
    """
    imList_len = np.arange(len(obj.imList))
    for im_num in imList_len:
        delete_im(obj)

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

#After talkign to Li, make sure to test proper error handling for improper file selection        
def create_h5_from_file(obj):
    """
    Reads a file chosen within GUI which contains a list of hdf id numbers.
    The function 'create_h5' is then called for each number to create an h5 file.
    """
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
    """
    Choose json file with parameters used for pixel fitting.
    """
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
    """
    Pixel fit h5 file
    """
    try:
        h5_path = (str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File')))
        h5_file = os.path.basename(h5_path)
        obj.lineEdit_5.setText(h5_path)
        fit_pixel_data_and_save(obj.wd, h5_file, param_file_name = os.path.basename(obj.json))
        msg(obj, "Chose " + h5_path + " for fitting")
    except:
        msg(obj, "fit_h5 Error: Make sure to choose proper .json and h5 files")
    
        
def choose_im(obj):
    """
    Choose a single image to display. Makes an Im object out of the selected 
    image and adds the Im object to the imList.
    """
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
    """
    Plots most recently chosen image from function 'choose_im'.
    """
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
    """
    Controls slider to change displayed image from imList.
    """
    if len(obj.imList) is 0:
        plot_im(obj, obj.blank_img)
        #return
    imgNum = obj.horizontalSlider.sliderPosition()
    if len(obj.imList) is 0:
        imgNum = 0
    img = obj.imList[imgNum]
    obj.horizontalSlider.setMaximum(len(obj.imList)-1)
    obj.lineEdit_9.setText(str(imgNum)+"/"+str(obj.horizontalSlider.maximum()))
    checkBoxes(obj, img)
    textLabels(obj, img)
    plot_im(obj, img)

#Ask Tom about best way to handle updating data of different shape
#Still have issue with set_data. Actual image does not show up,
#instead it is just points, no image
def plot_im(obj, img):
    """
    Plot image
    Parameters
    ----------
    img: 2D numpy array
    """
    if img.state > 0:
        array = img.img_array2
    else:
        array = img.im_array
    #obj.label.setText(img.get_title())
    #obj.label_2.setText(img.get_file())
    #obj.canvas.fig.clear()
    #obj.canvas.ax = obj.canvas.fig.add_subplot(1,1,1,)
    #image = obj.canvas.ax.imshow(array, cmap='jet')
    obj.image.set_data(array)
    obj.image.set_extent((0, array.shape[1], array.shape[0], 0))
    obj.image.set_clim(vmin=np.amin(array), vmax=np.amax(array))
    #divider = make_axes_locatable(obj.canvas.axes)
    #cax = divider.append_axes('right', size='5%', pad=0.05)
    #obj.canvas.fig.colorbar(obj.image, cax = cax)
    obj.cb.set_clim(vmin=np.amin(array), vmax=np.amax(array))
    obj.cb.draw_all()
    obj.canvas.fig.canvas.draw()

def choose_norm(obj):
    """
    Choose image via Image Operation tab from file as the image to normalize by.
    """
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
        
def choose_ref(obj):
    """
    Choose image to align by via button in Image Operation tab
    """
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
    """
    Plot reference image used for alignment. This image is plotted in secondary widget tab.
    """
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
"""
def plot_ref(obj, im_array):
    try:
        obj.ref_canvas.axes.imshow(im_array)
        obj.ref_canvas.fig.canvas.draw()
    except:
        msg(obj, "plot_ref Error: Make sure an image was chosen to plot (tiff, jpeg, etc.)")
"""    
def choose_img_dir(obj):
    """
    Choose directory filled with images for plotting.
    """
    path = str(QtGui.QFileDialog.getExistingDirectory(obj.centralwidget, 'Open File'))
    if path == '':
        msg(obj, "No directory chosen")
        return
    obj.lineEdit_8.setText(path)
    
def plot_imgs(obj):
    """
    Plots all images in directory from chosen via the 'choose_img_dir()' function.
    """
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
 
#Need to handle division by zero case
def normalize(array1, array2):
    """
    Pixel by pixel division.
    """
    rtn_array = np.divide(array2, array1)
    return rtn_array
    
def normalize_obj(obj):
    """
    Normalize currently displayed image by chosen reference image
    """
    img = obj.imList[obj.horizontalSlider.value()]
    if img.state > 0:
        img.img_array2 = normalize(obj.norm_img.img_array2, img.img_array2)
    else:
        img.img_array2 = normalize(obj.norm_img.im_array, img.im_array)
    img.norm_check = True
    img.norm_array = obj.norm_img.img_array2
    plot_im(obj, img)
    
def unNormalize(obj):
    """
    Inverse operation for normalization. Reverts image back to state before normalization
    and plots it.
    """
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
    """
    Manages normalization check box in 'Image Augmentation' button group. Will normalize currently
    displayed image if check box is clicked and will un-normalize if check box is being unchecked.
    """
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
        
def normalize_all(obj):
    """
    Normalize all images in imList by reference normalization image.
    """
    if obj.horizontalSlider.maximum() is 0:
        obj.checkBox_2.setCheckState(True)
        normalize_check(obj)
    for value in np.arange(obj.horizontalSlider.maximum()+1):
        obj.horizontalSlider.setValue(value)
        obj.checkBox_2.setCheckState(True)
        normalize_check(obj)
        
        
def make_ref_norm_box(obj):
    """
    Manages check box which when checked makes image reference image for normalization.
    """
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
    """
    Aligns align_array by ref_array using convolution.
    Returns aligned image and x,y shift.
    Parameters
    ----------
    ref_array: 2D numpy array
        Reference image for alignment
    
    align_array: 2D numpy array
        Image to align.
    """
    img, x_shift, y_shift = ac.subpixel_align(ref_array, align_array, 0, 0, 1)
    return img, x_shift, y_shift

#Update later
def align_obj(obj):
    """
    
    """
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
       
def align_check(obj):
    """
    Manages align image check box in 'Image Augmentation' box. Aligns or
    unaligns image based on how box is checked.
    """
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
    """
    Choose currently viewed image as reference image for alignment.
    
    """
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
        #if obj.ref_img.state != 0:
        #    plot_reference(obj.ref_img.img_array2)
        #else:
        #    plot_reference(obj.ref_img.im_array)
           
            
def unAlign(obj):
    """
    Does inverse of alignment of currently viewed image by shifting back to original state.
    Image state is updated and plotted again.
    """
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
    
#Update later    
def unAlignTrue(array, x_shift, y_shift):
    """
    
    """
    array = ac.pixel_shift_2d(array, (-1)*img.x_shift, (-1)*img.y_shift)
    return array  
    
    
def checkBoxes(obj, img):  
    """
    Manages checkboxes in 'Image Augmentation' group. When changing to
    new image for viewing these checkboxes are chaged to reflect the current status
    of the viewed image.
    """
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
        
    obj.checkBox.setTristate(False)
    obj.checkBox_2.setTristate(False)
    obj.checkBox_3.setTristate(False)
    obj.checkBox_4.setTristate(False)
    obj.checkBox_5.setTristate(False)
    obj.checkBox_6.setTristate(False)
    
    
def handleImageInverse(obj, unNor = False, unAl = False):
    """
    Handles all inverse operations of image and state updates for image.
    Parameters
    ----------
    unNor: Boolean
        If True then image will be unnormalized.
    
    unAl: Boolean
        If True then image will be unaligned.
    """
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
            msg(obj, "I'M ON THE INSIDE AT LINE 498 DELETE ME PLEASE")
            img.state = 1
            unNormalize(obj)
            
def textLabels(obj, img):
    """
    Manages display of currently viewed image information.
    """
    obj.label.setText("Title: "+img.title)
    obj.label_2.setText("File Path: "+img.f)
    obj.label_3.setText("Pixel Shift: ("+str(img.x_shift)+","+str(img.y_shift)+")")
    obj.label_5.setText("Intensity from ROI: "+str(img.intensity))

"""
#Reshape two Im objects, always scaling up smaller object            
def resizeIms(im1, im2):
    pass

def resize(im, x, y):
    temp_im = Image.fromarray(im)
    im2 = Image.fromarray(arr2)
    #im1 = im1.resize((100, 100))
"""    
            
#Currently assuming all images are same shape, including ref
def batch_registration(obj):
    """
    Image registration on all images in imList.
    """
    if type(obj.ref_img) is not Im:
        msg(obj, "Need to choose reference image to align by")
        return
    reg_file = open(obj.wd+'/registration.txt', 'w')
    if obj.ref_img.state is not 0:
        ref_array = obj.ref_img.img_array2
    else:
        ref_array = obj.ref_img.im_array
    imList_len = np.arange(len(obj.imList))
    for im_num in imList_len:
        obj.horizontalSlider.setValue(im_num)
        obj.checkBox.setCheckState(True)
        align_check(obj)
        """
        if im.state is not 0:
            align_array = im.img_array2
        else:
            align_array = im.im_array
        aligned_array, im.x_shift, im.y_shift = align(ref_array, align_array)
        im.img_array2 = aligned_array.real    
        """
        #slider_change(obj)
    for im in obj.imList:
        reg_file.write('{} {}\n'.format(im.x_shift, im.y_shift))
    reg_file.close()
        
# Need to implement xdata of incident beam energy        
def generate_roi_data(obj):
    for roi in obj.roiList.roi_list:
        count = 0
        fname = roi.title
        f = open(fname, 'w')
        for im in obj.imList:
            intensity = compute_intensity(roi, im.img_array2)
            f.write('{} {}\n'.format(count, intensity))
            count += 1
        f.close()