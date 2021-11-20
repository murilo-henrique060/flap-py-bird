import pygame, json, os, random
from pygame.locals import *

# Initialize pygame
pygame.init()

# Set Screen
screen_width = 360
screen_height = 640
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('FlapPy Bird')

fps = 30
tick = 0

# Sprites
base_path = os.path.dirname(os.path.abspath(__file__))
sprite_path = os.path.join(base_path, 'assets\\sprites')

sprite_sheet = pygame.image.load(os.path.join(sprite_path, 'Mobile - Flappy Bird - Version 12 Sprites.png'))
sprite_sheet_config = json.load(open(os.path.join(sprite_path, 'sprites.json')))

sprites = {}

for sprite in sprite_sheet_config:
    sprites[sprite] = []

    for start in sprite_sheet_config[sprite]['start']:
        rect = (start[0], start[1], sprite_sheet_config[sprite]['size'][0], sprite_sheet_config[sprite]['size'][1])
        sprites[sprite].append(pygame.transform.scale(sprite_sheet.subsurface(rect), (rect[2] * 2.5, rect[3] * 2.5)))

# Score
score = 0
high_score = 0

# Clock
clock = pygame.time.Clock()

# Game functions
def draw_medal():
    if 30 > score >= 10:
        screen.blit(sprites['bronze_medal'][0], (72, 302))
    elif score < 50:
        screen.blit(sprites['silver_medal'][0], (72, 302))
    elif score < 100:
        screen.blit(sprites['gold_medal'][0], (72, 302))
    else:
        screen.blit(sprites['platinum_medal'][0], (72, 302))

def draw_score():
    for i, num in enumerate(str(score)):
        screen.blit(sprites['large_numbers'][int(num)], ((screen_width // 2 - ((sprites['large_numbers'][int(num)].get_width() + 5) * len(str(score)) - 5) // 2) + (sprites['large_numbers'][int(num)].get_width() + 5) * i, 20))

def reset():
    # Reset Bird
    bird_group.add(Bird())
    bird_group.sprite.menu()

    # Reset Ground
    for ground in ground_group:
        ground.reset()

    # Reset Score
    global score
    score = 0

def menu(events):
    for event in events:
        if (event.type == KEYDOWN and event.key == K_SPACE) or (event.type == MOUSEBUTTONDOWN and event.button == 1 and start_button_group.sprite.rect.collidepoint(event.pos)):
            global game_state
            game_state = 'ready'

    # Update Background
    background_group.update()

    # Update Ground
    ground_group.update()

    # Update Bird
    bird_group.sprite.menu()
    bird_group.update()

    # Draw Objects
    background_group.draw(screen)
    ground_group.draw(screen)
    bird_group.draw(screen)
    screen.blit(sprites['FlapPy Bird'][0], (screen_width // 2 - sprites['FlapPy Bird'][0].get_width() // 2, 100))
    start_button_group.draw(screen)

def ready(events):
    for event in events:
        if event.type == KEYDOWN and event.key == K_SPACE:
            global game_state
            game_state = 'game'
            bird_group.sprite.flap()

    # Update Background
    background_group.update()

    # Update Ground
    ground_group.update()

    # Update Bird
    bird_group.sprite.menu()
    bird_group.update()

    # Draw Objects
    background_group.draw(screen)
    ground_group.draw(screen)
    draw_score()
    bird_group.draw(screen)
    screen.blit(sprites['ready'][0], (screen_width // 2 - sprites['ready'][0].get_width() // 2, screen_height // 2 + 50))
    screen.blit(sprites['get_ready'][0], (screen_width // 2 - sprites['get_ready'][0].get_width() // 2, 100))

def game(events):
    for event in events:
        if event.type == KEYDOWN:
            if event.key == K_SPACE and bird_group.sprite.living:
                bird_group.sprite.flap()

    # Update Background
    background_group.update()

    # Update Ground
    ground_group.update()

    # Update Bird
    bird_group.update()

    # Check Collisions
    if pygame.sprite.spritecollideany(bird_group.sprite, ground_group):
        bird_group.sprite.die(ground_group.sprites()[0])

        for ground in ground_group:
            ground.speed = 0

    # Draw Objects
    background_group.draw(screen)
    ground_group.draw(screen)
    draw_score()
    bird_group.draw(screen)

    # Check Game Over
    if bird_group.sprite.living == False:
        global game_state
        game_state = 'game_over'
        for ground in ground_group:
            ground.speed = 0

        bird_group.sprite.die(ground_group.sprites()[0])

def game_over(events):
    for event in events:
        if event.type == KEYDOWN and event.key == K_SPACE:
            global game_state
            game_state = 'ready'
            reset()

    # Draw Objects
    background_group.draw(screen)
    ground_group.draw(screen)
    draw_score()
    bird_group.draw(screen)
    screen.blit(sprites['game_over'][0], (screen_width // 2 - sprites['game_over'][0].get_width() // 2, 100))
    screen.blit(sprites['leaderboard'][0], (screen_width // 2 - sprites['leaderboard'][0].get_width() // 2, screen_height // 2 - sprites['leaderboard'][0].get_height() // 2))
    draw_medal()

# Game Classes
class Background(pygame.sprite.Sprite):
    def __init__(self, pos_x = 0):
        super().__init__()

        self.image = sprites['background_day'][0]
        self.rect = self.image.get_rect()
        self.size = self.image.get_size()
        self.rect[0] = pos_x
        self.speed = 1
        self.frame = 0

    def update(self):
        if self.frame == 0:
            self.rect[0] -= self.speed
            if self.rect[0] <= -screen_width:
                self.rect[0] = screen_width

                if (score // 50) % 2 == 1:
                    self.image = sprites['background_night'][0]
                else:
                    self.image = sprites['background_day'][0]

        self.frame = (self.frame + 1) % 2

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.sprites = [sprites.get('bird_yellow'), sprites.get('bird_red'), sprites.get('bird_blue')]
        self.current_sprite = random.randint(0, len(self.sprites) - 1)
        self.image = self.sprites[self.current_sprite][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect[0] = screen_width // 2 - self.size[0] // 2
        self.rect[1] = screen_height // 2 - self.size[1] // 2
        self.frame = 0
        self.speed = 5
        self.animation_timer = 0
        self.living = True
        self.rotate_speed = -0.5
        self.angle = 0

    def update(self):
        if self.rect[1] + self.speed < 0:
            self.rect[1] = 0
            self.speed = 0

        else:
            self.rect[1] += self.speed
            self.angle += self.rotate_speed

            if self.angle > 45:
                self.angle = 45

            if self.angle < -45:
                self.angle = -45

        if self.living:
            self.speed += 1
            self.rotate_speed -= 0.8

            if self.animation_timer == 0:
                self.frame = (self.frame + 1) % len(self.sprites[self.current_sprite])
                self.image = pygame.transform.rotate(self.sprites[self.current_sprite][self.frame], self.angle if self.angle >= 0 else 360 + self.angle)

            self.animation_timer = (self.animation_timer + 1) % 4
        else:
            self.speed = 0

    def flap(self):
        self.speed = -10
        self.rotate_speed = 8

    def die(self, ground_1):
        self.living = False
        self.speed = 0
        self.rect[1] = ground_1.rect[1] - self.size[1]

    def menu(self):
        self.speed = 0
        self.rotate_speed = 0
        self.rect[1] = screen_height // 2 - self.size[1] // 2
        self.angle = 0

class Ground(pygame.sprite.Sprite):
    def __init__(self, pos_x= 0):
        super().__init__()

        self.image = sprites['ground'][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect[0] = pos_x
        self.rect[1] = screen_height - self.size[1]
        self.speed = 5

    def update(self):
        self.rect[0] -= self.speed
        if self.rect[0] < -screen_width:
            self.rect[0] = screen_width

    def reset(self):
        self.speed = 5

class StartButton(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = sprites['start_button'][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect[0] = screen_width // 2 - self.size[0] // 2
        self.rect[1] = screen_height - 150

background_group = pygame.sprite.Group(Background(), Background(screen_width))
bird_group = pygame.sprite.GroupSingle(Bird())
ground_group = pygame.sprite.Group(Ground(), Ground(screen_width))
start_button_group = pygame.sprite.GroupSingle(StartButton())

game_state = 'menu'

# Main Loop
while True:
    # Event Handling
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            exit()

    # Game Logic
    if game_state == 'menu':
        menu(events)
    if game_state == 'ready':
        ready(events)
    if game_state == 'game':
        game(events)
    if game_state == 'game_over':
        game_over(events)

    # Update
    clock.tick(fps)
    pygame.display.update()