import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import threading
import serial
import time
import cv2
import numpy as np

def nothing(*arg):
        pass

def toma(camara):
    i      = 0
    cap = cv2.VideoCapture(camara)
    tim = time.time()
    while i < 6:
	ret, img = cap.read()
        i = time.time() - tim
        #cv2.waitKey(100)
        print i
	if i > 5:
  	   print "Whisky"
           cv2.imwrite("Foto.png", img)
	   break

    cap.release()
