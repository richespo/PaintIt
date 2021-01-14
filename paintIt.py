import os, time, random
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import QObject, QPoint, QTimer, pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QGraphicsPixmapItem, QGraphicsScene, QDesktopWidget


screen_x, screen_y = 640, 480

class Ui_MainWindow(QObject):
    def setupUi(self, MainWindow):
        # sizeObject = QDesktopWidget().screenGeometry(-1)
        # screen_y, screen_x = sizeObject.height(), sizeObject.width()
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(screen_x, screen_y)
        #     MainWindow.setMaximumSize(QtCore.QSize(screen_x, screen_y))
        #     MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(0, 0, screen_x, screen_y))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setHorizontalScrollBarPolicy(1);
        self.graphicsView.setVerticalScrollBarPolicy(1);
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 12))
        self.menubar.setObjectName("menubar")
        self.menuOpen = QtWidgets.QMenu(self.menubar)
        self.menuOpen.setObjectName("menuOpen")
        MainWindow.setMenuBar(self.menubar)
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.transition)

        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.menuOpen.addAction(self.actionOpen)
        self.menubar.addAction(self.menuOpen.menuAction())
        self.actionOpen.triggered.connect(theMaster.startTransition)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Viewer"))
        self.menuOpen.setTitle(_translate("MainWindow", "File"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))



class TransitionMaster():

    def __init__(self):
        self.pix = QPixmap()
        self.painter = QPainter(self.pix)
        self.tranTimer = QTimer()

    def startTransition(self):
        self.newImage = QImage("cam92_1.jpg")
        self.currentImage = QImage("DSC_0035.jpg")
        self.w = self.newImage.width()
        self.h = self.newImage.height()
        self.pix = QPixmap(self.currentImage)
        self.scene = QGraphicsScene()
        self.numSlices = 9
        self.slice = 0
        # self.transition_type = random.randint(0,6)
        self.transition_type = 4
        self.tranTimer.start(10)

    def transition(self):
        self.slice += 1
        self.theTransition()
        if self.slice > self.numSlices:
            self.painter.end()
            self.currentImage = self.newImage
        else:
            item = QGraphicsPixmapItem(self.pix)
            self.scene.addItem(item)
            ui.graphicsView.setScene(self.scene)
            self.tranTimer.start(50)

    def theTransition(self):
        if self.transition_type == 1:                  #wipe right
            cropped = self.newImage.copy(0, 0, int((self.w * self.slice) / self.numSlices),  self.h)
            dest_point = QPoint(0,0,)
            self.painter.begin(self.pix)
            self.painter.drawImage(dest_point, cropped)
        elif self.transition_type == 2:                #wipe left
            self.chunk = int((self.w * self.slice) / self.numSlices)
            cropped = self.newImage.copy(self.w-self.chunk, 0, self.w,  self.h)
            dest_point = QPoint(self.w-self.chunk,0)
            self.painter.begin(self.pix)
            self.painter.drawImage(dest_point, cropped)
        elif self.transition_type == 3:               #wipe down
            self.chunk = int((self.h * self.slice) / self.numSlices)
            cropped = self.newImage.copy(0, 0, self.w, self.chunk)
            dest_point = QPoint(0,0)
            self.painter.begin(self.pix)
            self.painter.drawImage(dest_point, cropped)
        elif self.transition_type == 4:                 #wipe up
            self.chunk = int((self.h * self.slice) / self.numSlices)
            cropped = self.newImage.copy(0, self.h-self.chunk, self.w, self.h)
            dest_point = QPoint(0,self.h-self.chunk)
            self.painter.begin(self.pix)
            self.painter.drawImage(dest_point, cropped)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    theMaster = TransitionMaster()
    theMaster.tranTimer.timeout.connect(theMaster.transition)
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())