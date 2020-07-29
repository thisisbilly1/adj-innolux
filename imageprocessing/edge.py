import cv2
import numpy as np
from utils import cvimage_to_pygame
from interfacetools.slider import slider 

class edge:
	def __init__(self, world, controller, x, y):
		self.world = world
		self.controller = controller
		self.x = x
		self.y = y
		
		self.threshSliderMax = slider(self.world,250,40,"maxVal",sliderange=(0,250),start=120)
		self.threshSliderMin = slider(self.world,100,40,"minVal",sliderange=(0,250),start=60)
		
		
	def draw(self, img):
		xx = self.controller.xx
		yy = self.controller.yy
		
		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		edge = cv2.Canny(gray,self.threshSliderMin.slideValue,self.threshSliderMax.slideValue)#60,120
		bgr = cv2.cvtColor(edge,cv2.COLOR_GRAY2RGB)
		
		self.world.screen.blit(cvimage_to_pygame(bgr),(94+xx, 10+yy))
		
		
		self.threshSliderMin.draw()
		self.threshSliderMax.draw() 