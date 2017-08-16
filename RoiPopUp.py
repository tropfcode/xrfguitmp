from PyQt4 import QtCore, QtGui
import RoiSelector as roiSelect
import functions as func

class RoiPopUp(QtGui.QWidget):
    def __init__(self):   
        QtGui.QWidget.__init__(self)
        self.choice_box = QtGui.QComboBox()
        self.choice_box.insertItem(0, "rectangle")
        self.choice_box.insertItem(1, "ellipse")
        self.choice_box.insertItem(2, "freehand")
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.choice_box)
        self.setLayout(self.layout)
        self.setGeometry(100, 100, 400, 100)
        

class RoiList(QtGui.QWidget):
    def __init__(self, axes):
        QtGui.QWidget.__init__(self)
        self.roi_list = []
        self.axes = axes
        self.count = 0
        
        # Widget layout
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        
        # Groupbox where ScrollArea will go
        self.box = QtGui.QGroupBox("ROI")
        self.box_layout = QtGui.QVBoxLayout()
        self.box.setLayout(self.box_layout)
        
        # Setting widet for ScrollArea
        self.scrollWidget = QtGui.QWidget()
        self.scrollWidget_layout = QtGui.QVBoxLayout()
        self.scrollWidget.setLayout(self.scrollWidget_layout)
        
        # Scrollarea widget and layout
        self.scroll = QtGui.QScrollArea()
        self.scroll.setWidget(self.scrollWidget)
        self.scroll.setWidgetResizable(True) # Make area scrollable
        self.layout.addWidget(self.scroll)
        
        # Place Groupbox in parent widget and ScrollArea in Groupbox
        self.layout.addWidget(self.box)
        self.box_layout.addWidget(self.scroll)
        
        # Groupbox for creating new ROI and activating ROI
        self.roi_box = QtGui.QGroupBox("ROI Manipulation")
        self.roi_box_layout = QtGui.QGridLayout()
        self.roi_box.setLayout(self.roi_box_layout)
        self.layout.addWidget(self.roi_box)
        
        # Create and Place ComboBoxes and Buttons in roi_box
        self.create_combo = QtGui.QComboBox()
        self.create_btn = QtGui.QPushButton("Create ROI")
        self.create_btn.clicked.connect(self.createRoi)
        self.create_combo.insertItem(0, "rectangle")
        self.create_combo.insertItem(1, "ellipse")
        self.create_combo.insertItem(2, "freehand")
        self.activate_combo = QtGui.QComboBox()
        self.activate_btn = QtGui.QPushButton("Activate ROI")
        self.activate_btn.clicked.connect(self.activateRoi)
        self.roi_box_layout.addWidget(self.create_combo, 0, 0)
        self.roi_box_layout.addWidget(self.create_btn, 1, 0)
        self.roi_box_layout.addWidget(self.activate_combo, 0, 1)
        self.roi_box_layout.addWidget(self.activate_btn, 1, 1)
        
        #Setting size
        self.setMinimumWidth(400)
        self.setMaximumWidth(450)
        
    def addRoi(self, title, roi):
        roiObj = RoiObj(title, roi, self)
        self.roi_list.append(roiObj)
        self.scrollWidget_layout.addWidget(self.roi_list[len(self.roi_list)-1].widget)

        
    # Need to confirm this function is obsolete 
    def delete(self, index):
        roi_item = self.roi_list[index]
        roi_item.setVisible(False)
        roi_item.roi.axes.figure.canvas.draw()
        roi_item.widget.setParent(None)
        if self.roi_list[index].lasso_switch is True:
            del self.roi_list[index].roi
        del self.roi_list[index]
        
    def activateRoi(self):
        num = self.activate_combo.currentIndex()
        if len(self.roi_list) < 1:
            return
        for roi in self.roi_list:
            roi.roi.active(False)
        self.roi_list[num].roi.active(True)

    def createRoi(self):
        if len(self.roi_list) > 0:
            for roi in self.roi_list:
                roi.roi.active(False)
        roi_type = self.create_combo.currentText()
        roi = roiSelect.RoiSelector(self.axes, roi_type)
        title = "Roi "+str(self.count)
        self.addRoi(title, roi)
        self.activate_combo.addItem(self.roi_list[len(self.roi_list)-1].title)
        self.count = self.count + 1
        
        
class RoiObj():
    def __init__(self, title, roi, roi_list_obj):
        self.roi_list_obj = roi_list_obj
        self.widget = QtGui.QWidget()
        self.hbox = QtGui.QHBoxLayout()
        self.widget.setLayout(self.hbox)
        self.roi = roi
        self.title = str(title)
        self.roi.title = self.title
        self.check_box = QtGui.QCheckBox()
        self.titleLabel = QtGui.QLabel(self.title)
        self.typeLabel = QtGui.QLabel(self.roi.roi_type)
        self.hbox.addWidget(self.check_box)
        self.hbox.addWidget(self.titleLabel)
        self.hbox.addWidget(self.typeLabel)
        self.check_box.setCheckState(True)
        self.check_box.setTristate(False)
        self.check_box.clicked.connect(self.handleCheckBox)
        self.delButton = QtGui.QPushButton("Remove")
        self.delButton.clicked.connect(self.delete)
        self.hbox.addWidget(self.delButton)
        self.roi.global_switch = True
      
    def setVisible(self, switch):
        if self.roi.roi_type != 'rectangle' and self.roi.roi_type != 'ellipse':
            self.roi.lasso_visible(switch)
            return
        self.roi.visible(switch)
        if switch is False:
            self.roi.active(False)
        
    def handleCheckBox(self):
        if self.check_box.isChecked():
            self.setVisible(True)
            self.roi.global_switch = True
        else:
            self.setVisible(False)
            self.roi.global_switch = False
        
    def delete(self):
        self.setVisible(False)
        self.widget.setParent(None)
        self.roi_list_obj.roi_list.remove(self)
        self.roi_list_obj.activate_combo.clear()
        del self.roi.roi
        self.roi.axes.figure.canvas.draw()
        count = 0
        for roi in self.roi_list_obj.roi_list:
            self.roi_list_obj.activate_combo.insertItem(count, roi.title)
            count += 1
        
        
        