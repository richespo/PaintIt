import os, time, random
from PyQt5 import QtWidgets, QtGui, QtCore, Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter, QGuiApplication
from PyQt5.QtCore import QObject, QPoint, QTimer, pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QGraphicsPixmapItem, QGraphicsScene, QDesktopWidget


imageDir = "/Users/rich/smallFrame"
imageDuration = 5000       #in milliseconds


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
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(0, 0, self.screen_x, self.screen_y))
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
        self.actionOpen.triggered.connect(theMaster.masterInit)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Viewer"))
        self.menuOpen.setTitle(_translate("MainWindow", "File"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))


class Master():

    def __init__(self):
        #get screen size
        screen = QGuiApplication.primaryScreen()
        screenGeometry = screen.geometry()
        self.screen_y = screenGeometry.height()
        self.screen_x = screenGeometry.width()
        self.blkbox = QImage(self.screen_x, self.screen_y, 4)
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
        self.newImage = None
        while self.newImage == None:        # returns None if first portrait saved
            self.newImage = self.scaleImage(QImage(self.image_list[self.imageNum]))
            if self.newImage != None:
                continue
            self.imageNum += 1
        transitioner.initTransition(self.newImage)
        transitioner.startTransition()
        self.imageNum += 1                  # index next image from list
        self.displayTimer.start(imageDuration)


    def getFileList(self):
        # fdialog = QFileDialog()
        # fdialog.setFileMode(QFileDialog.DirectoryOnly)
        # file_name = QFileDialog.getExistingDirectory(None, 'Choose Directory', "/Users/rich")
        #file_name = "C:\\Users\\riche\\smallFrame"
        image_list = [os.path.join(imageDir, f) for f in os.listdir(imageDir) if f.endswith('.jpg')]
        return image_list

    ''' scales image to height of display. After resize if wider than screen width lop off a bit from each side
        if less wide than screen pad both sides with black bar'''

    def scaleImage(self, im):
        if im.height() == self.screen_y and im.width() == self.screen_x:
            return im
        else:
            scaledImage = im.scaledToHeight(self.screen_y, QtCore.Qt.FastTransformation)
            if scaledImage.height() == self.screen_y and scaledImage.width() == self.screen_x:
                return scaledImage
            if scaledImage.width() > scaledImage.height():              #landscape
                if scaledImage.width() > self.screen_x:                   # width needs to be cropped
                    increment = (scaledImage.width() - self.screen_x) / 2   # crop 1/2 oversize from each side
                    scaledImage = scaledImage.copy(increment, 0, int(scaledImage.width() - (2*increment)), int(self.screen_y))
                    return scaledImage
                elif scaledImage.width() < self.screen_x:           # too narrow, add black padding
                    increment = (self.screen_x - scaledImage.width()) / 2
                    self.blkbox.fill(0)                             # make it black
                    myPainter = QPainter( self.blkbox)
                    dest = QPoint(increment,0)
                    myPainter.begin(self.blkbox)
                    myPainter.drawImage(dest, scaledImage)
                    myPainter.end()
                    return   self.blkbox
            else:                               #portrait, so we want to have two to display together
                if self.gotFirstImage == False:
                    self.firstHalf = scaledImage    # save the first portrait sized image
                    self.gotFirstImage = True
                    return None
                else:
                    self.gotFirstImage = False
                    self.portrait = scaledImage
                    if self.firstHalf.width() + self.portrait.width() <= self.screen_x:   # need padding
                        self.blkbox.fill(0)
                        padding = (self.screen_x - (self.firstHalf.width() + self.portrait.width())) / 3  # compute padding\
                        myPainter = QPainter( self.blkbox)
                        dest1 = QPoint(padding,0)
                        dest2 = QPoint(self.firstHalf.width() + 2 *padding, 0)
                        myPainter.begin(self.blkbox)
                        myPainter.drawImage(dest1, self.firstHalf)
                        myPainter.drawImage(dest2, self.portrait)
                        myPainter.end()
                        self.firstHalf = None
                        return self.blkbox
                #self.return_image = self.blkbox
                # self.GOT_firstImage = False
                # self.firstImage = self.blank_image
                # return self.return_image
            # else:                           #add code for width too wide
            #     if self.firstImage.size[0] > screen_x/2:
            #         xtra = self.firstImage.size[0] - screen_x/2
            #         chop = int(xtra/2)
            #         box = (chop, 0, int(chop+(screen_x/2)), screen_y)
            #         self.firstImage = self.firstImage.crop(box)
            #     if portrait_image.size[0] > screen_x/2:
            #         xtra = portrait_image.size[0] - screen_x/2
            #         chop = int(xtra/2)
            #         box = (chop, 0, int(chop+(screen_x/2)), screen_y)
            #         portrait_image = portrait_image.crop(box)
            #     self.blank_image.paste(self.firstImage, (0,0))
            #     self.blank_image.paste(portrait_image, ((self.firstImage.size[0], 0)))
            #     self.return_image = self.blank_image
            #     self.GOT_firstImage = False
            #     self.firstImage = self.blank_image
            #
            #     self.blank_image = Image.new("RGB", (screen_x, screen_y), "black")
            #     return self.return_image



class TransitionMaster():

    def __init__(self):
        self.pix = QPixmap()
        self.painter = QPainter(self.pix)
        self.tranTimer = QTimer()
        self.scene = QGraphicsScene()
        self.numSlices = 9

    def initTransition(self, im):
        self.newImage = im
        self.slice = 0
        self.transition_type = random.randint(1,4)


    def startTransition(self):
        self.slice += 1
        self.doTransition()
        if self.slice > self.numSlices:
            self.displayImage = self.pix.toImage()
        else:
            item = QGraphicsPixmapItem(self.pix)
            self.scene.addItem(item)
            ui.graphicsView.setScene(self.scene)
            self.tranTimer.start(50)


    def doTransition(self):
        if self.transition_type == 1:                  #wipe right
            self.cropped = self.newImage.copy(0, 0, int((self.newImage.width() * self.slice) / self.numSlices), self.newImage.height())
            dest_point = QPoint(0,0,)
            self.painter.drawImage(dest_point, self.cropped)
        elif self.transition_type == 2:                #wipe left
            self.chunk = int((self.newImage.width() * self.slice) / self.numSlices)
            self.cropped = self.newImage.copy(self.newImage.width()-self.chunk, 0, self.newImage.width(),  self.newImage.height())
            dest_point = QPoint(self.newImage.width()-self.chunk,0)
            self.painter.drawImage(dest_point, self.cropped)
        elif self.transition_type == 3:               #wipe down
            self.chunk = int((self.newImage.height() * self.slice) / self.numSlices)
            self.cropped = self.newImage.copy(0, 0, self.newImage.width(), self.chunk)
            dest_point = QPoint(0,0)
            self.painter.drawImage(dest_point, self.cropped)
        elif self.transition_type == 4:                 #wipe up
            self.chunk = int((self.newImage.height() * self.slice) / self.numSlices)
            self.cropped = self.newImage.copy(0, self.newImage.height()-self.chunk, self.newImage.width(), self.newImage.height())
            dest_point = QPoint(0,self.newImage.height()-self.chunk)
            self.painter.drawImage(dest_point, self.cropped)




''' events generated by two timers, tranTimer times the transition stages
    displayTimer times the display time of image'''

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    transitioner = TransitionMaster()
    transitioner.tranTimer.timeout.connect(transitioner.startTransition)
    theMaster = Master()
    theMaster.displayTimer.timeout.connect(theMaster.masterLoop)
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())