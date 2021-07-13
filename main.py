from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog , QLabel , QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from imagemodel import imageModel
from modes import Modes
import numpy as np
from matplotlib import pyplot as plt
import cv2
import sys , logging
from Ui import Ui_MainWindow
logging.basicConfig(filename='logger.log', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger()

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.filepath=["",""]
        self.images=[[],[]]
        self.image_no=[0,0]
        self.data=[]
        self.output_no=0
        self.img_viewers=[self.ui.Original_image1,self.ui.Original_image2,self.ui.Modified_image1,self.ui.Modified_image2,self.ui.Output_image1,self.ui.Output_image2]
        self.combobox_mixer=[self.ui.Component1_combobox , self.ui.Component2_combobox]
        self.combobox_image=[self.ui.image1_combobox,self.ui.image2_combobox]
        self.comboBox_component_image=[self.ui.choose_image1,self.ui.choose_image2]
        self.sliders=[self.ui.Component1_slider, self.ui.Component2_slider]
        self.output=self.ui.output_combobox
        self.ui.actionImage_1.triggered.connect(lambda: self.open(0))
        self.ui.actionImage_2.triggered.connect(lambda: self.open(1))
        self.combobox_image[0].currentIndexChanged.connect(lambda: self.img_options(0))
        self.combobox_image[1].currentIndexChanged.connect(lambda: self.img_options(1))
        self.comboBox_component_image[0].currentIndexChanged.connect(lambda: self.Mixer_img(0))
        self.comboBox_component_image[1].currentIndexChanged.connect(lambda: self.Mixer_img(1))
        self.output.currentIndexChanged.connect(lambda: self.output_img())
        self.combobox_mixer[0].currentIndexChanged.connect(lambda: self.mix_options(True))
        self.combobox_mixer[1].currentIndexChanged.connect(lambda: self.mix_options())
        self.sliders[0].valueChanged.connect(lambda: self.mix_options())
        self.sliders[1].valueChanged.connect(lambda: self.mix_options())

    def open(self,flag):
        options = QFileDialog.Options()
        self.filepath[flag], _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",
                        "(*.jfif);;(*png);;(*.jpeg);;(*.jpg) ", options=options)
        self.path = self.filepath[flag]
        logger.info("Image"+str(flag+1)+" opened correctly")
        self.img =cv2.cvtColor(cv2.imread(self.path), cv2.COLOR_BGR2GRAY)
        self.images[flag] = imageModel(self.path)
        if flag == 0:
            self.view_image(self.img , flag)
        self.check_size(flag)
        logger.info("Image"+str(flag+1)+"  is ploted")


    def check_size(self,flag):
        if self.images[0] != [] and self.images[1] != []:
            if self.images[0].imgShape != self.images[1].imgShape:
                msg = QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setText("The two images are of different size")
                logger.warning("The two images are of different size")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
            else:
                self.view_image(self.img , flag)
                logger.info("The two images are of same size" )
    
    def view_image(self,data,imgflag):
        self.img_viewers[imgflag].setImage((data).T)
        self.img_viewers[imgflag].view.setAspectLocked(False)
        logger.info("Data is ploted")

    def img_options(self,imgflag):
        if self.combobox_image[imgflag].currentText() == "Magnitude":
            self.data = self.images[imgflag].magnitude2 
            logger.info("Magnitude has been selected")
        elif self.combobox_image[imgflag].currentText() == "Phase":
            self.data = self.images[imgflag].phase 
            logger.info("Phase has been selected")
        elif self.combobox_image[imgflag].currentText() == "Real":
            self.data= self.images[imgflag].real2
            logger.info("Real has been selected")   
        elif self.combobox_image[imgflag].currentText()== "Imaginary":
            self.data = self.images[imgflag].imaginary 
            logger.info("Imaginary has been selected")
        else:
            logger.warning("No component has been selected")
        self.view_image(self.data,imgflag+2)


    def mix_options(self,flag=False):
        self.Data=[]
        if flag:
            self.comboxox_setitems()
        for i in range(2):
            if self.combobox_mixer[self.image_no[i]].currentText() == "Magnitude" and self.combobox_mixer[not(self.image_no[i])].currentText() == "Phase":
                self.Data = self.images[self.image_no[i]].mix(self.images[not(self.image_no[i])],self.sliders[i].value(),self.sliders[not(i)].value(),Modes.magnitudeAndPhase)
                logger.info("Mix magnitude of image"+str(self.image_no[i]+1)+" and phase of image" +str((self.image_no[not(i)])+1))

            elif self.combobox_mixer[self.image_no[i]].currentText() == "Real" and self.combobox_mixer[not(self.image_no[i])].currentText() == "Imaginary":
                self.Data = self.images[self.image_no[i]].mix(self.images[not(self.image_no[i])],self.sliders[self.image_no[i]].value(),self.sliders[not(self.image_no[i])].value(),Modes.realAndImaginary)
                logger.info("Mix real of image"+str(self.image_no[i]+1)+" and Imaginary of image" +str((self.image_no[not(i)])+1))

            elif self.combobox_mixer[self.image_no[i]].currentText() == "Magnitude" and self.combobox_mixer[not(self.image_no[i])].currentText() == "Uni Phase":
                self.Data = self.images[self.image_no[i]].mix(self.images[not(self.image_no[i])],self.sliders[self.image_no[i]].value(),self.sliders[not(self.image_no[i])].value(),Modes.magnitudeAndUniPhase)
                logger.info("Mix magnitude of image"+str(self.image_no[i]+1)+" and uniphase of image" +str((self.image_no[not(i)])+1))

            elif self.combobox_mixer[self.image_no[i]].currentText() == "Uni Magnitude" and self.combobox_mixer[not(self.image_no[i])].currentText() == "Phase":
                self.Data = self.images[self.image_no[i]].mix(self.images[not(self.image_no[i])],self.sliders[self.image_no[i]].value(),self.sliders[1].value(),Modes.UnimagnitudeAndPhase)
                logger.info("Mix unimagnitude of image"+str(self.image_no[i]+1)+" and phase of image" +str((self.image_no[not(i)])+1))

            elif self.combobox_mixer[self.image_no[i]].currentText() == "Uni Magnitude" and self.combobox_mixer[not(self.image_no[i])].currentText() == "Uni Phase":
                self.Data = self.images[self.image_no[i]].mix(self.images[not(self.image_no[i])],self.sliders[self.image_no[i]].value(),self.sliders[1].value(),Modes.uniMagAnduniPhase)
                logger.info("Mix unimagnitude of image"+str(self.image_no[i]+1)+" and uniphase of image" +str((self.image_no[not(i)])+1))

            else:
                logger.warning("Unavailable Mode")

        if len(self.Data) >0:
            self.view_image(self.Data,self.output_no+4)
            logger.info("Mode is selected")
        else:
            logger.warning("No mood is selected")

    def Mixer_img(self,boxflag):
        if self.comboBox_component_image[boxflag].currentText() == "Image 1":
            self.image_no[boxflag] =0
        logger.info("Image1 is selected as input"+str(boxflag+1))
        if self.comboBox_component_image[boxflag].currentText() == "Image 2":
            self.image_no[boxflag] =1
        logger.info("Image is selected as input"+str(boxflag+1))

    def output_img(self):
        if self.output.currentText() == "Output 1":
            self.output_no =0
            logger.info("Display mixed image in output1")
        if self.output.currentText()== "Output 2":
            self.output_no =1
            logger.info("Display mixed image in output2")

    def comboxox_setitems(self):
        self.combobox_mixer[1].clear()
        if self.combobox_mixer[0].currentText() == "Magnitude" or self.combobox_mixer[0].currentText() == "Uni Magnitude":
            self.combobox_mixer[1].addItem("Phase")
            self.combobox_mixer[1].addItem("Uni Phase")
        elif self.combobox_mixer[0].currentText() == "Phase" or self.combobox_mixer[0].currentText() == "Uni Phase":
            self.combobox_mixer[1].addItem("Magnitude")
            self.combobox_mixer[1].addItem("Uni Magnitude")
        elif self.combobox_mixer[0].currentText() == "Real":
            self.combobox_mixer[1].addItem("Imaginary")
        elif self.combobox_mixer[0].currentText() == "Imaginary":
            self.combobox_mixer[1].addItem("Real")
        logger.info("Combobox Itemtext changed")    



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())