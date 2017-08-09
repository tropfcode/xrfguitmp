from PyQt4 import QtCore, QtGui

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
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.roi_list = []
        
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
        
        #Setting size
        self.setMinimumWidth(400)
        self.setMaximumWidth(450)
        
    def addRoi(self, title, roi):
        roiObj = RoiObj(title, roi)
        self.roi_list.append(roiObj)
        self.scrollWidget_layout.addWidget(self.roi_list[len(self.roi_list)-1].widget)
        
class RoiObj():
    def __init__(self, title, roi):
        self.widget = QtGui.QWidget()
        self.hbox = QtGui.QHBoxLayout()
        self.widget.setLayout(self.hbox)
        self.roi = roi
        self.title = str(title)
        self.check_box = QtGui.QCheckBox()
        self.titleLabel = QtGui.QLabel(self.title)
        self.typeLabel = QtGui.QLabel(self.roi.roi_type)
        self.hbox.addWidget(self.check_box)
        self.hbox.addWidget(self.titleLabel)
        self.hbox.addWidget(self.typeLabel)
        self.check_box.setCheckState(True)
        self.check_box.clicked.connect(self.handleCheckBox)
      
    def setVisible(self, switch):
        self.roi.roi.set_visible(switch)
        
    def handleCheckBox(self):
        print("line 74 roipopup.py", self.check_box.isChecked())
        if self.check_box.isChecked():
            self.setVisible(True)
        else:
            self.setVisible(False)
        self.roi.axes.figure.canvas.draw()
        

        