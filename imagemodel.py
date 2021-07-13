import cv2
import numpy as np
import math
from modes import Modes
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) 


class imageModel():

    def __init__(self,imagepath:str):
        self.imagepath = imagepath
        self.img = cv2.cvtColor(cv2.imread(self.imagepath), cv2.COLOR_BGR2GRAY)
        self.imgShape = self.img.shape
        self.f = np.fft.fft2(self.img)
        self.fshift = np.fft.fftshift(self.f)
        self.magnitude=np.abs(self.fshift)
        self.magnitude2=20 * np.log(np.abs(self.fshift))
        self.phase =np.angle(self.fshift)
        self.real=np.real(self.fshift)
        self.real2=20 * np.log(np.real(self.fshift))
        self.imaginary=np.imag(self.fshift)
        self.uni_phase= np.zeros(self.imgShape) 
        self.uni_mag= np.ones(self.imgShape) 
        

    def mix(self, imageToBeMixed: 'imageModel', component1_ratio: float, component2_ratio: float, mode: 'Modes') -> np.ndarray:
        ratio1=component1_ratio/100
        ratio2=component2_ratio/100

        def output_transform (comp1,comp2):
            if mode == Modes.realAndImaginary:
            	Output_fourrier = comp1+(comp2*1j)
            else:
                Output_fourrier = comp1*np.exp(comp2*1j)
            Output = np.abs(np.fft.ifft2(np.fft.ifftshift(Output_fourrier)))
            logger.info("Transfromed components into time ")
            return Output


        if mode==Modes.magnitudeAndPhase:
            magnitude=self.magnitude*ratio1+(imageToBeMixed.magnitude*(1-ratio1))
            phase=imageToBeMixed.phase*ratio2+(self.phase*(1-ratio2))
            data=output_transform(magnitude,phase)
            logger.info("Mixed mode 1")

        if mode==Modes.realAndImaginary:
            real=self.real*ratio1+(imageToBeMixed.real*(1-ratio1))
            imaginary=imageToBeMixed.imaginary*ratio2+(self.imaginary*(1-ratio2))
            data=output_transform(real,imaginary)
            logger.info("Mixed mode 2")

        if mode==Modes.magnitudeAndUniPhase:
            magnitude=self.magnitude*ratio1+(imageToBeMixed.magnitude*(1-ratio1))
            uni_phase=self.uni_phase 
            data=output_transform(magnitude,uni_phase)
            logger.info("Mixed mode 3")

        if mode==Modes.UnimagnitudeAndPhase:
            uni_magnitude=self.uni_mag 
            phase=imageToBeMixed.phase*ratio2+(self.phase*(1-ratio2))
            data=output_transform(uni_magnitude,phase)
            logger.info("Mixed mode 4")

        if mode==Modes.uniMagAnduniPhase:
            uni_magnitude=self.uni_mag 
            uni_phase=self.uni_phase 
            data=output_transform(uni_magnitude,uni_phase)
            logger.info("Mixed mode 5")

        if(len(data) >0):
        	logger.info("Finished mixing")
        else: 
        	logger.info("no mixing")

        return data