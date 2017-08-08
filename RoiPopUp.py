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
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        
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
        
    def addRoi(self):
        checkbox = QtGui.QPushButton('tmpbutton')
        self.scrollWidget_layout.addWidget(checkbox)
        
        