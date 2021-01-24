import os, random
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QImage, QPainter, QGuiApplication
from PyQt5.QtCore import QObject, QPoint, QTimer, QUrl
from PyQt5.QtWidgets import (QFileDialog, QGraphicsPixmapItem, QGraphicsScene,
                             QDesktopWidget, QHBoxLayout)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

IMAGE_DIR = "/Users/rich/smallFrame"
#IMAGE_DIR = "C:/Users/riche/smallFrame"
IMAGE_DURATION = 5000      #in milliseconds


class Ui_MainWindow(QObject):
    def setupUi(self, MainWindow):
        sizeObject = QDesktopWidget().screenGeometry(-1)
        self.screen_y, self.screen_x = sizeObject.height(), sizeObject.width()
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(self.screen_x, self.screen_y)
        MainWindow.setMaximumSize(QtCore.QSize(self.screen_x, self.screen_y))
        MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, self.screen_x, self.screen_y))
        self.stackedWidget.setObjectName("stackedWidget")
        self.picPage = QtWidgets.QWidget()
        self.picPage.setObjectName("page")
        self.graphicsView = QtWidgets.QGraphicsView(self.picPage)
        self.graphicsView.setGeometry(QtCore.QRect(0, 0, self.screen_x, self.screen_y))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setHorizontalScrollBarPolicy(1);
        self.graphicsView.setVerticalScrollBarPolicy(1);
        self.stackedWidget.addWidget(self.picPage)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()
        self.videoWidget.setFullScreen(False)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        self.vidPage = QtWidgets.QWidget()
        self.vidPage.setObjectName("page_2")
        self.widget = QtWidgets.QWidget(self.vidPage)
        self.widget.setGeometry(QtCore.QRect(0, 0, self.screen_x, self.screen_y))
        self.widget.setObjectName("widget")
        layout = QHBoxLayout()
        layout.addWidget(self.videoWidget)
        self.widget.setLayout(layout)
        self.stackedWidget.addWidget(self.vidPage)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 24))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionClose)
        self.menubar.addAction(self.menuFile.menuAction())

        self.actionOpen.triggered.connect(theMaster.masterInit)
        self.actionClose.triggered.connect(self.stopVid)

        MainWindow.keyPressEvent = self.keyPressEvent       #overrride
        self.stackedWidget.keyPressEvent = self.keyPressEvent
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def stopVid(self):
        self.mediaPlayer.stop()
        ui.stackedWidget.setCurrentIndex(0)

    def keyPressEvent(self, e):                         #quit on q
        if e.key()  == QtCore.Qt.Key_Q :
            exit()
        elif e.key() == QtCore.Qt.Key_0:
            self.mediaPlayer.stop()
            ui.stackedWidget.setCurrentIndex(0)
        elif e.key() == QtCore.Qt.Key_1:
            ui.stackedWidget.setCurrentIndex(1)
            fileName = ("/Users/rich/vid4.mov")
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            ui.stackedWidget.setCurrentIndex(0)

    def screenSize(self):
        return (self.screen_x, self.screen_y)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Viewer"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionClose.setText(_translate("MainWindow", "Close"))


class Master():

    def __init__(self):
        #get screen size
        screen = QGuiApplication.primaryScreen()
        screenGeometry = screen.geometry()
        self.screen_y = screenGeometry.height()
        self.screen_x = screenGeometry.width()

        self.displayTimer = QTimer()
        self.gotFirstImage = False
        self.begun = False

    def masterInit(self):
        self.image_list = self.getFileList()
        transitioner.pix = QPixmap(theMaster.screen_x, theMaster.screen_y)
        transitioner.painter.begin(transitioner.pix)
        self.imageNum = 0
        self.gotFirstImage = False
        self.displayTimer.start(10)


    def masterLoop(self):
        if self.imageNum == len(self.image_list):
            self.imageNum = 0                   # keep repeating
        newImage = None
        while newImage == None:        # returns None if have first portrait
            newImage = self.scaleImage(QImage(self.image_list[self.imageNum]))
            if newImage != None:
                continue
            self.imageNum += 1
        transitioner.initTransition(newImage)
        transitioner.transitionMaster()
        self.imageNum += 1                  # index next image from list
        self.displayTimer.start(IMAGE_DURATION)


    def getFileList(self):
        # fdialog = QFileDialog()
        # fdialog.setFileMode(QFileDialog.DirectoryOnly)
        # file_name = QFileDialog.getExistingDirectory(None, 'Choose Directory', "/Users/rich")
        #file_name = "C:\\Users\\riche\\smallFrame"
        image_list = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')]
        return image_list

    ''' scales image to height of display. After resize if wider than screen width lop off a bit from each side
        if less wide than screen pad both sides with black bar. Will compose a full sized image from two portrait 
        sized images'''

    def scaleImage(self, im):
        if im.height() == self.screen_y and im.width() == self.screen_x:
            return im
        else:
            scaledImage = im.scaledToHeight(self.screen_y, QtCore.Qt.FastTransformation)
            if scaledImage.height() == self.screen_y and scaledImage.width() == self.screen_x:
                return scaledImage
            blkbox = QImage(self.screen_x, self.screen_y, 4)
            if scaledImage.width() > scaledImage.height():              #landscape
                if scaledImage.width() > self.screen_x:                   # width needs to be cropped
                    increment = (scaledImage.width() - self.screen_x) / 2   # crop 1/2 oversize from each side
                    scaledImage = scaledImage.copy(increment, 0, int(scaledImage.width() - (2*increment)), int(self.screen_y))
                    return scaledImage
                elif scaledImage.width() < self.screen_x:           # too narrow, add black padding
                    increment = (self.screen_x - scaledImage.width()) / 2
                    blkbox.fill(0)                             # make it black
                    myPainter = QPainter(blkbox)
                    dest = QPoint(int(increment),0)
                    myPainter.begin(blkbox)
                    myPainter.drawImage(dest, scaledImage)
                    myPainter.end()
                    return  blkbox
            else:                               #portrait, so we want to have two to display together
                if self.gotFirstImage == False:
                    self.firstHalf = scaledImage    # save the first portrait sized image
                    self.gotFirstImage = True
                    return None
                else:
                    self.gotFirstImage = False
                    self.portrait = scaledImage
                    if self.firstHalf.width() + self.portrait.width() <= self.screen_x:   # need padding
                        blkbox.fill(0)
                        padding = (self.screen_x - (self.firstHalf.width() + self.portrait.width())) / 3  # compute padding\
                        myPainter = QPainter(blkbox)
                        dest1 = QPoint(int(padding),0)
                        dest2 = QPoint(self.firstHalf.width() + 2 * int( padding), 0)
                        myPainter.begin(blkbox)
                        myPainter.drawImage(dest1, self.firstHalf)
                        myPainter.drawImage(dest2, self.portrait)
                        myPainter.end()
                        self.firstHalf = None
                        return blkbox


class TransitionMaster():

    def __init__(self):
        self.pix = QPixmap()                #QPixMap as QPaintDevice
        self.painter = QPainter(self.pix)
        self.tranTimer = QTimer()           #times the transition phases
        self.scene = QGraphicsScene()
        self.tile_size = (ui.screen_x // 6,  ui.screen_y // 4)
        self.tiles = [(0,0), (1,0), (2,0), (3,0), (4,0), (5,0), (0,1), (1,1), (2,1), (3,1), (4,1), (5,1),
                      (0,2), (1,2), (2,2), (3,2), (4,2), (5,2), (0,3), (1,3), (2,3), (3,3), (4,3), (5,3)]
        self.tile_index = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

    #get the image to be displayed next and initiate
    def initTransition(self, im):
        self.newImage = im
        self.slice = 0
        self.numSlices = 10                 #num transition phases
        self.transition_type = random.randint(1,6)
        # self.transition_type = 7
        # if self.transition_type == 7:
        #     self.numSlices = 24


    def transitionMaster(self):
        self.slice += 1
        self.doTransition()
        if self.slice > self.numSlices:             #transition done, remember displayed image
            #      self.displayImage = self.pix.toImage()
            return
        else:
            item = QGraphicsPixmapItem(self.pix)    #QPixMap->item->scene->QGraphicsView thus displayed
            self.scene.addItem(item)
            ui.graphicsView.setScene(self.scene)
            self.tranTimer.start(50)

    # the actual transition types
    def doTransition(self):
        displayImage = QImage()
        if self.transition_type == 1:                  #wipe right
            cropped = self.newImage.copy(0, 0, int((self.newImage.width() * self.slice) / self.numSlices), self.newImage.height())
            dest_point = QPoint(0,0,)
            self.painter.drawImage(dest_point, cropped)
        elif self.transition_type == 2:                #wipe left
            chunk = int((self.newImage.width() * self.slice) / self.numSlices)
            cropped = self.newImage.copy(self.newImage.width()-chunk, 0, self.newImage.width(),  self.newImage.height())
            dest_point = QPoint(self.newImage.width()-chunk,0)
            self.painter.drawImage(dest_point, cropped)
        elif self.transition_type == 3:               #wipe down
            chunk = int((self.newImage.height() * self.slice) / self.numSlices)
            cropped = self.newImage.copy(0, 0, self.newImage.width(), chunk)
            dest_point = QPoint(0,0)
            self.painter.drawImage(dest_point, cropped)
        elif self.transition_type == 4:                 #wipe up
            chunk = int((self.newImage.height() * self.slice) / self.numSlices)
            cropped = self.newImage.copy(0, self.newImage.height()-chunk, self.newImage.width(), self.newImage.height())
            dest_point = QPoint(0,self.newImage.height()-chunk)
            self.painter.drawImage(dest_point, cropped)
        elif self.transition_type == 5:                     #center out
            if self.slice <= 10:
                h_slice = int(self.newImage.width() * self.slice / (2*self.numSlices))
                v_slice = int(self.newImage.height() * self.slice/ (2*self.numSlices))
                cropped = self.newImage.copy(int(self.newImage.width()/2)-h_slice, int(self.newImage.height()/2)-v_slice, 2*h_slice, 2*v_slice)
                dest_point = QPoint(int(self.newImage.width()/2-h_slice), int((self.newImage.height()/2)-v_slice))
                self.painter.drawImage(dest_point, cropped)
        elif self.transition_type == 6:                     #outer edge in
            displayImage = self.pix.toImage()
            self.painter.drawImage(QPoint(0,0), self.newImage)
            if self.slice <= 9:
                h_slice = int(displayImage.width() * self.slice / (2 * self.numSlices))
                v_slice = int(displayImage.height() * self.slice/ (2 * self.numSlices))
                cropped = displayImage.copy(h_slice, v_slice, displayImage.width()-2*h_slice, displayImage.height()-2*v_slice)
                dest_point = QPoint(h_slice, v_slice)
                self.painter.drawImage(dest_point, cropped)
        elif self.transition_type == 7:
            startx, starty = self.tiles[self.tile_index[self.slice-1]]
            cropped = self.newImage.copy(startx*self.tile_size[0], starty*self.tile_size[1], self.tile_size[0], self.tile_size[1])
            dest_point = QPoint(startx*self.tile_size[0], starty*self.tile_size[1])
            self.painter.drawImage(dest_point, cropped)

''' events generated by two timers, tranTimer times the transition stages
    displayTimer times the display time of image'''

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    theMaster = Master()
    theMaster.displayTimer.timeout.connect(theMaster.masterLoop)
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    transitioner = TransitionMaster()
    transitioner.tranTimer.timeout.connect(transitioner.transitionMaster)
    MainWindow.show()
    sys.exit(app.exec_())