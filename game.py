import pygame
import cairo
import random
from random import randint

pygame.init()
SCREEN = WIDTH, HEIGHT = 1000, 800
win = pygame.display.set_mode(SCREEN)
pygame.display.set_caption('Memory Puzzle')

cairo_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
context = cairo.Context(cairo_surface)

gx0 = 0
gy0 = 0
gx1 = 0
gy1 = HEIGHT
linearGrad = cairo.LinearGradient(gx0, gy0, gx1, gy1)
linearGrad.add_color_stop_rgb(0, 0, 1, 0) 
linearGrad.add_color_stop_rgb(1, 0, 0, 1) 
context.set_source(linearGrad)
context.rectangle(0, 0, WIDTH, HEIGHT)
context.fill()

data = cairo_surface.get_data()
gradient_bg = pygame.image.frombuffer(data, (WIDTH, HEIGHT), "ARGB")

clock = pygame.time.Clock()
FPS = 120

ROWS, COLS = 4, 5
TILESIZE = 140 

WHITE = (255, 255, 255)

img_list = []
for img in range(1, 11): 
    image = pygame.image.load(f"Assets/icons/{img}.jpg")
    image = pygame.transform.scale(image, (TILESIZE, TILESIZE))
    img_list.append(image)

game_won = pygame.image.load('Assets/won.png')

class Button(pygame.sprite.Sprite):
    def __init__(self, img, scale, x, y):
        super(Button, self).__init__()

        self.image = pygame.transform.scale(img, scale)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.clicked = False

    def draw(self, win, image=None):
        if image:
            self.image = image
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                action = True
                self.clicked = True

            if not pygame.mouse.get_pressed()[0]:
                self.clicked = False

        win.blit(self.image, self.rect)
        
        return action

restart_img = pygame.image.load('Assets/restart.png')
restart_btn = Button(restart_img, (70, 70), 350, 720)

close_img = pygame.image.load('Assets/close.png')
close_btn = Button(close_img, (70, 70), 550, 720) 

class Board:
    def __init__(self, imglist):
        self.image_list = imglist
        self.extended_imglist = imglist * 2 

        self.board = None
        self.randomize_images()

    def randomize_images(self):
        random.shuffle(self.extended_imglist) 
        board = [[0 for j in range(COLS)] for i in range(ROWS)]

        margin_x = (WIDTH - (COLS * TILESIZE + (COLS - 1) * 10)) // 2
        margin_y = (HEIGHT - (ROWS * TILESIZE + (ROWS - 1) * 10) - 100) // 2 

        for r in range(ROWS):
            for c in range(COLS):
                index = r * COLS + c
                image = self.extended_imglist[index]
                x = c * TILESIZE + c * 10 + margin_x
                y = r * TILESIZE + r * 10 + margin_y
                card = Card(index, (r, c), image, (x, y))
                board[r][c] = card

        self.board = board

class Card:
    def __init__(self, value, index, image, pos):
        self.value = value
        self.index = index
        self.image = image
        self.pos = pos

        self.is_alive = True
        self.visible = False
        self.animate = False
        self.slide_left = True
        self.animation_complete = False

        self.rect = self.image.get_rect()
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

        self.cover_x = TILESIZE

        self.rotation_angle = 0
        self.scale_factor = 1.0
        self.rotating = False
        self.scaling_up = True
        self.rotation_completed = False

    def on_click(self, win, speed=None):
        if self.visible or self.rotating:
            if self.slide_left:
                self.animation_complete = False
                if self.cover_x > 0:
                    self.cover_x -= speed
                if self.cover_x <= 0:
                    self.animate = False
            else:
                if self.cover_x < TILESIZE:
                    self.cover_x += speed
                if self.cover_x >= TILESIZE:
                    self.animate = False
                    self.visible = False
                    self.slide_left = False
                    self.animation_complete = True

            if self.rotating:
                self.rotation_angle += 15
                if self.rotation_angle >= 360:
                    self.rotation_angle = 0
                    self.rotation_completed = True

                if self.scaling_up:
                    self.scale_factor += 0.05
                    if self.scale_factor >= 1.5:
                        self.scaling_up = False
                else:
                    self.scale_factor -= 0.05
                    if self.scale_factor <= 1.0:
                        self.rotating = False
                        self.rotation_completed = True
                        self.is_alive = False
                        self.visible = False
                        self.scaling_up = True
                        self.scale_factor = 1.0
                        self.rotation_angle = 0

            rotated_image = pygame.transform.rotate(self.image, self.rotation_angle)
            scaled_image = pygame.transform.scale(rotated_image, (int(TILESIZE * self.scale_factor), int(TILESIZE * self.scale_factor)))
            scaled_rect = scaled_image.get_rect(center=self.rect.center)
            win.blit(scaled_image, scaled_rect.topleft)

            rect = (self.rect.x, self.rect.y, self.cover_x, TILESIZE)
            pygame.draw.rect(win, (255, 255, 255), rect)

    def start_rotation(self):
        self.rotating = True
        self.rotation_angle = 0
        self.scale_factor = 1.0
        self.rotation_completed = False

board = Board(img_list)

animated_boxes = [(randint(0, ROWS - 1), randint(0, COLS - 1)) for i in range(10)] 

game_screen = True
first_card = None
second_card = None
first_click_time = None
second_click_time = None
numCards = 20 
isLoading = True
animation_on = True
animation_count = 0

gameWon = False
numClicks = 0

running = True

while running:
    win.blit(gradient_bg, (0, 0)) 
    pygame.draw.rect(win, WHITE, (10, 10, 980, 680), 2)

    if restart_btn.draw(win):
        game_screen = True
        first_card = None
        second_card = None
        first_click_time = None
        second_click_time = None

        board.randomize_images()

        isLoading = True
        animation_on = True
        animation_count = 0
        numClicks = 0
        numCards = 20 
        gameWon = False

    if close_btn.draw(win):
        running = False

    clicked = False

    x, y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked = True
                x, y = pygame.mouse.get_pos()

    if game_screen:
        if numCards == 0:
            gameWon = True

        if isLoading:
            clicked = False

            if animation_count < 10:
                for index, pos in enumerate(animated_boxes):
                    card = board.board[pos[0]][pos[1]]
                    if card.cover_x >= TILESIZE:
                        card.visible = True
                        card.animate = True
                        card.slide_left = True

                    if card.cover_x <= 0:
                        card.animate = True
                        card.slide_left = False

                if card.animation_complete:
                    for pos in animated_boxes:
                        card = board.board[pos[0]][pos[1]]
                        card.visible = False
                        card.animate = False
                    animated_boxes = [(randint(0, ROWS - 1), randint(0, COLS - 1)) for i in range(10)] 
                    animation_count += 1
            else:
                isLoading = False
                animation_on = False
                animation_count = 0

        if not gameWon:
            if second_click_time:
                current_time = pygame.time.get_ticks()

                delta = current_time - second_click_time
                if delta >= 1000:
                    if first_card.image == second_card.image:
                        first_card.start_rotation()
                        second_card.start_rotation()
                        numCards -= 2
                    else:
                        first_card.animate = True
                        first_card.slide_left = False
                        second_card.animate = True
                        second_card.slide_left = False
                    first_card = None
                    second_card = None
                    second_click_time = None

            for r in range(ROWS):
                for c in range(COLS):
                    card = board.board[r][c]
                    if card.is_alive:
                        if card.rect.collidepoint((x, y)) and clicked:
                            if not first_card and not card.rotating:
                                card.visible = True
                                card.animate = True
                                card.slide_left = True
                                first_card = card
                            elif card != first_card and not card.rotating and not second_card:
                                card.visible = True
                                card.animate = True
                                card.slide_left = True
                                second_card = card
                                second_click_time = pygame.time.get_ticks()
                        
                        if card.rotating:
                            card.on_click(win, 8)
                        elif card.visible:
                            win.blit(card.image, card.rect)
                        else:
                            pygame.draw.rect(win, WHITE, (card.rect.x, card.rect.y, TILESIZE, TILESIZE))
                        
                        if card.animate and not card.rotating:
                            card.on_click(win, 8 if not isLoading else 5)
        else:
            win.blit(game_won, (350, 150))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()