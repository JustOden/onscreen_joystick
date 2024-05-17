import pygame, sys
from pygame.locals import *

pygame.init()

'''
to be fixed:
    1. needs to update joystick inner circle movement when clicking
    on the screen with multiple fingers. (backend) ✅
    
    2. needs to switch between finger ids so that any joystick can be
    used when clicked first AND/OR second. ✅
    
    3. needs better class variable names. (low priority) ❌
    
    4. needs to update innercircle position on screen blit for other fingers. (frontend) ✅
    
    5. needs to move object on screen with joy directions. ✅
    
    6. needs to cleanup code and remove redundancies. (low priority) ❌
    
    7. needs to fix the invalid id problem that freezes the inner circle movement
    when clicking on the restriction rect with another finger id in 
    non-stationary move (backend) ❌
'''
class Square(pygame.sprite.Sprite):
    def __init__(self, col, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(col)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.direction = pygame.math.Vector2()
        self.speed = 10
    
    def input(self, joystick):
        if joystick.up:
            self.direction.y = -1
        elif joystick.down:
            self.direction.y = 1
        else:
            self.direction.y = 0
        
        if joystick.right:
            self.direction.x = 1
        elif joystick.left:
            self.direction.x = -1
        else:
            self.direction.x = 0
    
    def move(self):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
            
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
    def update(self, surface, joystick):
        self.input(joystick)
        self.move()
        self.draw(surface)
        

class Joystick:
    def __init__(self, pos="left", stationary=False):
        self.screen = pygame.display.set_mode((0, 0))
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        self.clock = pygame.time.Clock()
        self.outer = pygame.image.load("../graphics/joystick_bg.png").convert_alpha()
        self.inner = pygame.image.load("../graphics/joystick.png").convert_alpha()
        self.outer_rect = self.outer.get_rect(topleft=(0,0))
        self.inner_rect = self.inner.get_rect(center=self.outer_rect.center)
        
        self.up = False
        self.down = False
        self.right = False
        self.left = False
        self.debug_on = False
        self.v_only = False
        self.h_only = False
        
        self.position = pos
        self.stationary = stationary
        self.sensitivity = 50
        self.id = 0
        
        self.fingers = {}
        self.placed = {}
        
        self.rect_length = 500
        self.rect_width = self.width/2
        
        self.rect_position = self.width/2 if self.position == "right" else 0 if self.position == "left" else 0        
        # for debugging
        if self.rect_position == 0:
            self.color = "red"
        else:
            self.color = "green"
            
        self.restriction_rect = pygame.draw.rect(self.screen, self.color, [self.rect_position, self.height-self.rect_length, self.rect_width, self.rect_length], 1)
        
        if self.stationary:
            self.outer_rect = self.outer.get_rect(center=(self.restriction_rect.center))
            self.inner_rect = self.inner.get_rect(center=self.outer_rect.center)
        
    def placement(self, ev):
        if ev.type == pygame.FINGERDOWN:
            x = ev.x*self.width
            y = ev.y*self.height
            pos = int(x), int(y)
            
            self.frozen_b = self.inner_rect.bottom 
            
            self.fingers[ev.finger_id] = pos
            
            for finger, pos in self.fingers.items():
                if self.restriction_rect.collidepoint(pos) and not self.stationary and len(self.placed) == 0:
                    
                    self.placed[finger] = True
                    self.id = finger
                
                    if ev.finger_id in self.placed and ev.finger_id == self.id and self.placed[ev.finger_id] and len(self.placed) == 1:
                        self.outer_rect.center = pos
                        self.inner_rect.center = self.outer_rect.center
                
                elif self.restriction_rect.collidepoint(pos) and self.inner_rect.collidepoint(pos) and self.stationary and len(self.placed) == 0:
                    
                    self.placed[finger] = True
                    self.id = finger
                
                    if ev.finger_id in self.placed and ev.finger_id == self.id and self.placed[ev.finger_id] and len(self.placed) == 0:
                        self.inner_rect.center = self.outer_rect.center
                    
        if ev.type == pygame.FINGERUP and ev.finger_id == self.id:
            self.up = False
            self.down = False
            self.right = False
            self.left = False
            
            self.fingers.pop(ev.finger_id, None)
            self.placed[ev.finger_id] = False
            self.placed.pop(ev.finger_id, None)
            self.inner_rect.center = self.outer_rect.center
            self.id = 0
            
        if self.id != 0:
            self.movement(ev)
            
    def movement(self, ev=None):
        for (finger, f_pos), (placed_finger, placed) in zip(self.fingers.items(), self.placed.items()):
            
            if ev is not None and ev.type == pygame.FINGERMOTION and self.id > 0 and ev.finger_id in self.placed and self.placed[ev.finger_id] and ev.finger_id == placed_finger and placed_finger == self.id and len(self.placed) == 1:
                x = ev.x*self.width
                y = ev.y*self.height
                pos = int(x), int(y)
                
                self.inner_rect.center = pos
                self.direction()
            
            elif ev is None:
                if pygame.mouse.get_pressed() == (1,0,0) and self.id == 0 and self.id == placed_finger and placed and len(self.placed) == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    self.inner_rect.center = mouse_pos
                    self.direction()
            
    def direction(self):
        # up
        if self.h_only:
            self.inner_rect.bottom = self.outer_rect.bottom - 50
        elif self.inner_rect.bottom - self.sensitivity < self.outer_rect.center[1]:
            self.up = True
            if self.inner_rect.bottom < self.outer_rect.center[1]:
                self.inner_rect.bottom = self.outer_rect.center[1]   
        else:
            self.up = False

        # down
        if self.h_only:
            self.inner_rect.top = self.outer_rect.top + 50
        elif self.inner_rect.top + self.sensitivity > self.outer_rect.center[1]:
            self.down = True
            if self.inner_rect.top > self.outer_rect.center[1]:
                self.inner_rect.top = self.outer_rect.center[1]
        else:
            self.down = False

        # right
        if self.v_only:
            self.inner_rect.left = self.outer_rect.left + 50
        elif self.inner_rect.left + self.sensitivity > self.outer_rect.center[0]:
            self.right = True
            if self.inner_rect.left > self.outer_rect.center[0]:
                self.inner_rect.left = self.outer_rect.center[0]
        else:
            self.right = False

        # left
        if self.v_only:
            self.inner_rect.right = self.outer_rect.right - 50
        elif self.inner_rect.right - self.sensitivity < self.outer_rect.center[0]:
            self.left = True
            if self.inner_rect.right < self.outer_rect.center[0]:
                self.inner_rect.right = self.outer_rect.center[0]
        else:
            self.left = False
    
    def blit(self):
        if self.debug_on:
            pygame.draw.rect(self.screen, self.color, [self.rect_position, self.height-self.rect_length, self.rect_width, self.rect_length], 1)
        if self.stationary:
            self.screen.blit(self.outer, self.outer_rect)
            self.screen.blit(self.inner, self.inner_rect)
        else:
            pass # make it blit when touching screen
            for finger, placed in self.placed.items():
                if placed:
                    self.screen.blit(self.outer, self.outer_rect)
                    self.screen.blit(self.inner, self.inner_rect)

    def run(self):
        if self.id == 0:
            self.movement()
        self.blit()

    def test_run(self):
        player = Square("yellow", self.width/2, self.height/2)
        
        while True:
            for event in pygame.event.get():
                self.placement(event)
                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill((0,0,0))
            player.update(self.screen, self) 
            self.run()

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    Joystick(stationary=True).test_run()
