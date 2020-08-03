import pygame
from controller import controller

class world:
    def __init__(self):
        self.controller=controller(self)
        self.size=(1500,920)
        
        #inputs
        self.keyspressed=[] #for key HOLD DOWN
        self.keyspress=[] #for key DOWN 
        
        self.mouse_x=0
        self.mouse_y=0
        self.mouse_left=False
        self.mouse_left_up=False
        self.mouse_left_down=False
        self.mouse_right=False
        self.mouse_right_up=False
        self.mouse_right_down=False
        self.mouse_left_previous=False
        self.mouse_right_previous=False
        self.mouse_scroll_down=False
        self.mouse_scroll_up=False
        
        pygame.init()
        pygame.font.init()
        self.fontobject = pygame.font.Font(None,18)
        
        self.screen = pygame.display.set_mode(self.size)
        self.clock=pygame.time.Clock()
        self.FPS=200#60
        self.running=True
    def update(self):
        while self.running:
            self.keyspress=[]
            self.draw()
            #reset the mouse vars
            self.mouse_left_up=False
            self.mouse_left_down=False
            self.mouse_right_up=False
            self.mouse_right_down=False
            self.mouse_scroll_down=False
            self.mouse_scroll_up=False
            
            self.mouse_left_previous=self.mouse_left
            self.mouse_right_previous=self.mouse_right
            #mouse inputs
            mouse = pygame.mouse.get_pos() 
            self.mouse_x=mouse[0]
            self.mouse_y=mouse[1]
            clicks = pygame.mouse.get_pressed()
            self.mouse_left=clicks[0]
            self.mouse_right=clicks[2]
            
            if self.mouse_left and self.mouse_left_previous==False:
                self.mouse_left_down=True
            if self.mouse_right and self.mouse_right_previous==False:
                self.mouse_right_down=True
            if self.mouse_left==False and self.mouse_left_previous:
                self.mouse_left_up=True
            if self.mouse_right==False and self.mouse_right_previous:
                self.mouse_right_up=True
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                    return
                #keyboard
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.stop()
                        return
                    else:
                        self.keyspressed.append(event.key)
                        self.keyspress.append(event.key)
                elif event.type == pygame.KEYUP:
                    if event.key in self.keyspressed:
                        self.keyspressed.remove(event.key)
                #scroll wheel
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button==5:
                        self.mouse_scroll_down=True
                    if event.button==4:
                        self.mouse_scroll_up=True
            
            self.controller.update()
        
    def draw(self):
        self.screen.fill((255,255,255))
        self.controller.draw()

        pygame.display.update()
        self.clock.tick(self.FPS)
    
    def stop(self):
        self.running=False
        pygame.quit()

w=world()
w.update()
            