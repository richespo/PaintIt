import os, time, random
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import QObject, QPoint, QTimer
from PyQt5.QtWidgets import QFileDialog, QGraphicsPixmapItem, QGraphicsScene, QDesktopWidget


screen_x, screen_y = 640, 480

class Ui_MainWindow(QObject):
    def setupUi(self, MainWindow):
        self.slice = 0
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
        self.timer = QTimer()
        self.timer.timeout.connect(self.transition)

        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.menuOpen.addAction(self.actionOpen)
        self.menubar.addAction(self.menuOpen.menuAction())
        self.actionOpen.triggered.connect(self.timerStart)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Viewer"))
        self.menuOpen.setTitle(_translate("MainWindow", "File"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))

    def timerStart(self):
        self.timer.start(1)

    def transition(self):
        self.slice += 1
        self.myAction(self.slice)

        if self.slice != 0:
            self.timer.start(50)
        else: self.timer.stop()



    def myAction(self, portion):
        if portion == 1:
            self.srcImage = QImage("cam92_1.jpg")
            self.w = self.srcImage.width()
            self.h = self.srcImage.height()
            self.destImage = QImage("DSC_0035.jpg")
            self.pix = QPixmap(self.destImage)
            self.painter = QPainter(self.pix)
        cropped = self.srcImage.copy(0, 0, int((self.w * portion) / 50),  self.h)
        dest_point = QPoint(0,0,)
        self.painter.drawImage(dest_point, cropped)
        if portion == 50:
            self.painter.end()
            self.pix = QPixmap(self.srcImage)
            self.slice = 0
        item = QGraphicsPixmapItem(self.pix)
        scene = QGraphicsScene(self)
        scene.addItem(item)
        self.graphicsView.setScene(scene)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())