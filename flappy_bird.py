import pygame
from pygame.locals import *
import random
from pygame import mixer  # For sound Effects

mixer.init()
pygame.init()


clock = pygame.time.Clock()
FPS = 60
SCREEN_WIDTH = 864
SCREEN_HEIGHT = 668
BG = (105, 105, 105)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird by Group G-31")


# Define font
font = pygame.font.SysFont('Segoe UI', 50)

# define coluor
white = (255, 255, 255)
BLACK = (0, 0, 0)

# Define game variables
ground_scrool = 0
scrool_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
high_score = 0
pass_pipe = False
start_game = False

bg_scroll = 0

# Load music and sound
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)
# Load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

pine1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6,
                    SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7,
                    SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8,
                    SCREEN_HEIGHT - pine2_img.get_height()))


def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(SCREEN_HEIGHT / 2)
    score = 0
    return score


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0

        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)

        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0  # gravity
        self.clicked = False

    def update(self):
        if flying == True:
            # gravity
            self.vel += 0.5

            if self.vel > 8:
                self.vel = 8
            # print(self.vel)

            if self.rect.bottom < 504:
                self.rect.y += int(self.vel)

        if game_over == False:
            # jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True  # can only click once to jump
                self.vel = -8
                jump_fx.play()

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # rotate bird
            self.image = pygame.transform.rotate(
                self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        # takes that image and creates a rectangle boundary around it
        self.rect = self.image.get_rect()
        # position = 1 means from the top,
        # position = -1 means from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scrool_speed
        if self.rect.right < 0:
            self.kill()


class ScreenFade:
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        # if self.direction == 1:  # whole screen fade
        # pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, screen_width // 2, screen_height))
        if self.direction == 2:  # vertical screen fade down
            pygame.draw.rect(screen, self.colour,
                             (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_HEIGHT:
            fade_complete = True
        return fade_complete


# Create screen fade
death_fade = ScreenFade(2, BLACK, 4)


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(
            image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()
        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action


# Group class - A container class to hold and manage multiple Sprite objects.
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()


flappy = Bird(100, int(SCREEN_HEIGHT / 2))
bird_group.add(flappy)

# create restart button instance
restart_button = Button(SCREEN_WIDTH // 2 - 100,
                        SCREEN_HEIGHT // 2 - 50, restart_img, 2)
# the floor division // rounds the result down to the nearest whole number

start_button = Button(SCREEN_WIDTH // 2 - 130,
                      SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = Button(SCREEN_WIDTH // 2 - 110,
                     SCREEN_HEIGHT // 2 + 50, exit_img, 1)

# -------------------------------------------- GAME LOOP ------------------------------------------------

run = True
while run:

    clock.tick(FPS)

    if start_game == False:
        # Main Menu
        screen.fill(BLACK)
        # Add buttons
        # draw_text(f'High score: {high_score}', font, white, 20, screen_height - 100)
        if start_button.draw(screen):
            start_game = True

        if exit_button.draw(screen):
            run = False
    else:
        # background
        # screen.blit(bg, (0,0))
        draw_bg()

        # Bird
        bird_group.draw(screen)
        bird_group.update()

        # Pipe
        pipe_group.draw(screen)

        # draw the ground
        screen.blit(ground_img, (ground_scrool, 504))

        # check the score
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                    and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                    and pass_pipe == False:
                # bird in between the pipe
                pass_pipe = True

            if pass_pipe == True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    #  bird passes the pipe
                    score += 1
                    pass_pipe = False
                    if score > high_score:
                        high_score = score
        # print(f"Score: {score}")

        draw_text(str(score), font, white, int(SCREEN_WIDTH/2), 20)
        draw_text(f'High score: {high_score}', font,
                  BLACK, 20, SCREEN_HEIGHT - 100)

        # look for collision
        # or flappy.rect.top < 0:
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False):
            # if Third argument is True - then delete the bird
            # if Fourth argument is True - then delete the pipe
            game_over = True

        # check if the bird has hit the ground
        if flappy.rect.bottom >= 504:
            game_over = True
            flying = False

        # ground
        if game_over == False and flying == True:
            # generate new pipes
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(SCREEN_WIDTH, int(
                    SCREEN_HEIGHT / 2) + pipe_height, -1)
                top_pipe = Pipe(SCREEN_WIDTH, int(
                    SCREEN_HEIGHT / 2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)

                last_pipe = time_now

            # Draw and scrool the ground and background
            ground_scrool -= scrool_speed
            bg_scroll += scrool_speed

            if abs(ground_scrool) > 35:
                ground_scrool = 0

            pipe_group.update()

    # check for game over and reset
    if game_over == True:
        if death_fade.fade():
            draw_text(f'Your score: {score}', font, white, 20, 20)
            draw_text(f'High score: {high_score}', font, white, 20, 100)
            if restart_button.draw(screen) == True:
                death_fade.fade_counter = 0
                # print("Reset Button Clicked")
                bg_scroll = 0
                game_over = False
                score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # clicking the x button on the right
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    pygame.display.update()
# ------------------------------------- GAME LOOP ENDS --------------------------------------------------

pygame.quit()


"""
Q. How games work?
A. An image that continuously updates + Player input + Logic
   Vanilla Python cannot draw images not it can get the user input that games need.
   Modules in python used for game development -> Pygame, Pyglet, Arcade.

Architecture of pygame ->
    pygame.init()
    Your logic
    pygame.quit()


pygame.init()
display_surface -> the canvas you draw on / game window
game loop -> actual logic of the game and canvas update
event loop -> events are player input
pygame.quit()

"""

