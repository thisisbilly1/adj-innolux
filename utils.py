from tkinter import filedialog
from tkinter import *

import os
import cv2
import pygame

import numpy as np

def resizeImage(image,zoom):
	width = int(image.shape[1] * zoom)
	height = int(image.shape[0] * zoom)
    
	return cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)

def returnCameraIndexes():
    # checks the first 10 indexes.
    index = 0
    arr = []
    i = 10
    while i > 0:
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index += 1
        i -= 1
    return arr

def drawbox(box, world, color, hovercolor, clickfunction, clickargs=(), text="", offclickfunction=None):
    c=color
    if checkmousebox(box,[world.mouse_x,world.mouse_y]):
        c=hovercolor
        if world.mouse_left_down:
            clickfunction(args=clickargs)
    else:
        if offclickfunction!=None:
            if world.mouse_left_down:
                offclickfunction()
                
    pygame.draw.rect(world.screen, c,(box[0],box[1],box[2],box[3]), 0)
    pygame.draw.rect(world.screen, (0,0,0),(box[0]-1,box[1]-1,box[2]+1,box[3]+1), 1)
    
    world.screen.blit(world.fontobject.render(str(text), 1, (0,0,0)),(box[0]+5, box[1]+5))


def clamp(x,minn,maxx):
    return max(min(x,maxx),minn)

def checkmousebox(box,mouse):
        if (box[0]+box[2]>mouse[0]>box[0] 
            and box[1]+box[3]>mouse[1]>box[1]):
            return True
        return False
    
def cvimage_to_pygame(image):
	"""Convert cvimage into a pygame image"""
	image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
	return pygame.image.frombuffer(image.tostring(), image.shape[1::-1],"RGB")

def folderLoad(folder=""):
	if folder=="":
		root = Tk()
		root.withdraw()
		folder = filedialog.askdirectory(parent=root)
        
	imglist=[]
	for file in os.listdir(folder):
		if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".PNG"):
			print("loading: "+str(file))
			imglist.append(cv2.imread(str(folder)+"/"+str(file)))
    
	print(imglist)
	return imglist
    

