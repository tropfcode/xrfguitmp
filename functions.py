from xrfGui_v0 import Ui_MainWindow
from PyQt4 import QtCore, QtGui
from pyxrf.model.command_tools import fit_pixel_data_and_save
from pyxrf.api import (make_hdf)
import os
import sys
import matplotlib.image as mpimg
import numpy as np
import matplotlib.pyplot as plt

"""
    Must make sure that all required files -- .json, .h5 -- are in the same
    directory as the wd.
    It seems that due to how fit_pixel_data_and_save was made that
    the h5_file needs to be inside the obj.wd else the function will no work
    properly. Talk to Li and see if a user is capable of choosing a different directory
    to save the results to.
"""

class Image():
    def __init__(self, im_array, ref_check = False, norm_check = False, align_check = False):
        self.im_array = im_array
        self.ref_check = ref_check
        self.norm_check = norm_check
        self.align_check = align_check
        
        
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
    
def create_h5(obj):
    """
    Create h5 file by pulling data from NSLS-II via specific hdf number
    """
    try:
        hdf_num = obj.lineEdit_2.text()
        if obj.wd is None:
            make_hdf(int(hdf_num))
        else:
            make_hdf(int(hdf_num), end=int(hdf_num), fname=obj.wd)
    except:
        obj.textEdit.append("Make hdf Error: Provide hdf number (only a number)")

        
def create_h5_from_file(obj):
    #try:
        h5_file = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
        obj.lineEdit_3.setText(h5_file)
        obj.textEdit.append('File for batch h5 creation: ' + h5_file)
        f = open(h5_file, 'r') 
        lines = f.readlines()
        #try:
        for line in lines:
            if obj.wd is None:
                make_hdf(int(line))
            else:
                make_hdf(int(line), fname=obj.wd)
        #except:
            obj.textEdit.append('Create h5 from file Error: ' + 
                                'Need proper hdf index number or file or number already exists')
    #except:
        obj.textEdit.append('Create h5 from file Error: ' + 
                            'Choose an appropriate file or make sure that file is proper format')

        
        
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
        obj.lineEdit_6.setText(im_path)
        obj.textEdit.append("Chose image " + im_path)
    except:
        obj.textEdit.append("Choose Image Error: Must choose an image (tiff, jpeg, etc.)")
                
        
def plot_im(obj, im_array):
    obj.canvas.axes.imshow(im_array)
    obj.canvas.fig.canvas.draw()
        
        
def plot_crnt_im(obj):
    try:
        im_path = obj.lineEdit_6.text()
        img = mpimg.imread(im_path)
        obj.imList.append(img)
        obj.horizontalSlider.setMaximum(len(obj.imList)-1)
        obj.horizontalSlider.setValue(obj.horizontalSlider.maximum())
        if len(obj.imList) == 1:
            plot_im(obj, img)
    except:
        obj.textEdit.append("Plot Current Image Error: Must choose an image (tiff, jpeg, etc.)")
    
        
def slider_change(obj):
    imgNum = obj.horizontalSlider.sliderPosition()
    img = obj.imList[imgNum]
    obj.lineEdit_9.setText(str(imgNum)+"/"+str(obj.horizontalSlider.maximum()))
    plot_im(obj, img)
       
def choose_ref(obj):
    try:        
        img_path = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
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
    
#Space for normalization (button, mathe, etc.)
#
#
##
#

def choose_img_dir(obj):
    path = str(QtGui.QFileDialog.getExistingDirectory(obj.centralwidget, 'Open File'))
    obj.lineEdit_8.setText(path)
    
def plot_imgs(obj):
    try:
        path = obj.lineEdit_8.text()
        for f in os.listdir(path):
            img = mpimg.imread(f)
            obj.imList.append(img)
            obj.horizontalSlider.setMaximum(len(obj.imList)-1)
            obj.horizontalSlider.setValue(obj.horizontalSlider.maximum())
    except:
        obj.textEdit.append("Plot Images Error: Make sure all files are images (tiff, jpeg, etc.)")
        
    
    