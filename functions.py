from xrfGui_v0 import Ui_MainWindow
from PyQt4 import QtCore, QtGui
from pyxrf.model.command_tools import fit_pixel_data_and_save
from pyxrf.api import (make_hdf)

def choose_wd(obj):
    try:
        word = str(QtGui.QFileDialog.getExistingDirectory(obj.centralwidget, 'Open File'))
        obj.lineEdit.setText(word)
        obj.wd = word
        obj.textEdit.append("Chose the Directory "+obj.wd)
    except:
        obj.textEdit.append("Choose Directory Error: Must choose proper directory")
    
def create_h5(obj):
    #try:
        hdf_num = obj.lineEdit_2.text()
    
        if obj.wd is None:
            make_hdf(int(hdf_num))
        else:
            make_hdf(int(hdf_num), end=int(hdf_num), fname=obj.wd)
    #except:
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
        h5_file = str(QtGui.QFileDialog.getOpenFileName(obj.centralwidget, 'Open File'))
        fit_pixel_data_and_save(obj.wd, h5_file, param_file_name = obj.json)
    except:
        obj.textEdit.append("fit_h5 Error: Make sure to choose working directory and .json file")
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        