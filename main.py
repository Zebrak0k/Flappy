import sys
import pygame
import random
import json

pygame.init()
pygame.display.set_caption('Flappy bird')
clock = pygame.time.Clock()

FPS = 70
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font('images/font/3dventure1.ttf', 80)

scroll_background = 0
speed_scroll_background = 2
scroll_ground = 0
speed_scroll_ground = 4
speed_scroll_pipe = 4
pipe_gap = 170
pipe_count = 0
score = 0
medal = 0
last_pipe = pygame.time.get_ticks()

fly = False
game_over = False
pass_pipe = False

sound_hit = pygame.mixer.Sound('sound/assets_audio_hit.wav')
sound_hit.set_volume(0.1)

sound_wing = pygame.mixer.Sound('sound/assets_audio_wing.wav')
sound_wing.set_volume(0.1)

sound_score = pygame.mixer.Sound('sound/assets_audio_point.wav')
sound_score.set_volume(0.1)

sound_die = pygame.mixer.Sound('sound/assets_audio_die.wav')
sound_die.set_volume(0.1)

background = pygame.image.load('images/Ground/bglong.png')
ground = pygame.image.load('images/Ground/ground.png')

animation = pygame.USEREVENT + 1
pygame.time.set_timer(animation, 125)


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def restart_game():
    global score, medal
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = SCREEN_HEIGHT // 2
    score = 0
    medal = 0


class Flappy(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, pos_x, pos_y):
        super().__init__(flappy_group)
        sheet = pygame.transform.scale(sheet, (160, 40))
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.rect.center = [pos_x, pos_y]
        self.vel = 0
        self.clicked = False

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        self.rect.x -= 30
        self.rect.y -= 30

        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def animation(self):
        if game_over is False:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.image = pygame.transform.rotate(self.frames[self.cur_frame], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.frames[self.cur_frame], -90)

    def update(self):
        if fly is True:
            if self.vel < 10:
                self.vel += 0.5
            if self.rect.bottom < 600:
                self.rect.y += int(self.vel)

        if game_over is False:
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                sound_wing.play(0)
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position, i):
        pygame.sprite.Sprite.__init__(self)
        load = ['images/Other/pipe-red.png', 'images/Other/pipe-green.png']
        self.frames = []
        self.x, self.y = x, y
        self.position = position

        self.image = pygame.image.load(load[i])
        self.image = pygame.transform.scale(self.image, (60, 400))
        self.rect = self.image.get_rect()
        self.rect.move(x, y)

        if self.position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [self.x, self.y - pipe_gap // 2]
        if self.position == -1:
            self.rect.topleft = [self.x, self.y + pipe_gap // 2]

    def update(self):
        self.rect.x -= speed_scroll_pipe
        if self.rect.right < 0:
            self.kill()


class Button:
    def __init__(self, x, y):
        self.game_over = pygame.image.load('images/Other/gameover.png')
        self.game_over_rect = self.game_over.get_rect()
        self.game_over_rect.topleft = (x - 35, y - 50)

        self.image = pygame.image.load('images/Other/restart.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.flappy_img = pygame.image.load('images/Other/Flappy.png')
        self.flappy_img = pygame.transform.scale(self.flappy_img, (256, 64))
        self.flappy_img_rect = self.flappy_img.get_rect()
        self.flappy_img_rect.topleft = (x - 54, 100)

        self.tutorial = pygame.image.load('images/Other/Tutorial.png')
        self.tutorial = pygame.transform.scale(self.tutorial, (220, 180))
        self.tutorial_rect = self.tutorial.get_rect()
        self.tutorial_rect.topleft = (x - 40, y - 100)

    def draw_start(self):
        screen.blit(self.flappy_img, (self.flappy_img_rect.x, self.flappy_img_rect.y))
        screen.blit(self.tutorial, (self.tutorial_rect.x, self.tutorial_rect.y))

    def draw_gameover(self):

        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        screen.blit(self.game_over, (self.game_over_rect.x, self.game_over_rect.y))
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


class Record:
    def __init__(self):
        self.best_record = self.check_best()

        self.table_img = pygame.image.load('images/Other/table.png')
        self.table_img = pygame.transform.scale(self.table_img, (200, 100))
        self.table_rect = self.table_img.get_rect()
        self.table_rect.topleft = (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50)

        self.new_rec_img = pygame.image.load('images/Other/new_record.png')
        self.new_rec_img = pygame.transform.scale(self.new_rec_img, (48, 64))
        self.new_rec_rect = self.new_rec_img.get_rect()
        self.new_rec_rect.topleft = (SCREEN_WIDTH // 2 - 88, SCREEN_HEIGHT // 2 + 80)

        self.old_record_img = pygame.image.load('images/Other/old_record.png')
        self.old_record_img = pygame.transform.scale(self.old_record_img, (48, 48))
        self.old_record_rect = self.old_record_img.get_rect()
        self.old_record_rect.topleft = (SCREEN_WIDTH // 2 - 88, SCREEN_HEIGHT // 2 + 80)

    def draw(self, reward, score_now):
        self.best_record = self.check_best()
        screen.blit(self.table_img, (self.table_rect.x, self.table_rect.y))
        draw_text(self.best_record, pygame.font.Font('images/font/numbers.ttf', 25), 'black', SCREEN_WIDTH // 2 + 50,
                  SCREEN_HEIGHT // 2 + 115)
        draw_text(str(score_now), pygame.font.Font('images/font/numbers.ttf', 25), 'black', SCREEN_WIDTH // 2 + 50,
                  SCREEN_HEIGHT // 2 + 78)
        if reward == 1:
            screen.blit(self.new_rec_img, (self.new_rec_rect.x, self.new_rec_rect.y))
        else:
            screen.blit(self.old_record_img, (self.old_record_rect.x, self.old_record_rect.y))

    def check_best(self):
        with open('record.json') as rec_file:
            data = json.load(rec_file)

        return data['the_best']

    def new_record(self, new_record):
        with open('record.json') as rec_file:
            data = json.load(rec_file)
        data['the_best'] = new_record
        with open('record.json', 'w') as rec_file:
            json.dump(data, rec_file, ensure_ascii=False, indent=4)


flappy_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Flappy(pygame.image.load('images/Flappy/style_1/Bird1-6.png'), 4, 1, 64, 16, 100, SCREEN_HEIGHT // 2)
flappy_group.add(flappy)

button = Button(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 50)
record = Record()
record.check_best()


def terminate():
    pygame.quit()
    sys.exit()


while True:
    clock.tick(FPS)

    screen.blit(background, (scroll_background, -1))

    pipe_group.draw(screen)
    flappy_group.draw(screen)
    flappy_group.update()

    screen.blit(ground, (scroll_ground, SCREEN_HEIGHT - 100))

    if len(pipe_group) > 0:
        if flappy_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and flappy_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and pass_pipe is False:
            pass_pipe = True
        if pass_pipe is True:
            if flappy_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                pass_pipe = False
                score += 1
                sound_score.play(0)
    draw_text(str(score), font, 'white', SCREEN_WIDTH // 2 - 20, 20)

    if pygame.sprite.groupcollide(pipe_group, flappy_group, False, False) or flappy.rect.bottom < 0:
        if game_over is False:
            sound_hit.play(0)
            sound_die.play(0)
        game_over = True

    if flappy.rect.bottom >= 600:
        if game_over is False:
            sound_hit.play(0)
        game_over = True
        fly = False

    if game_over is False and fly is True:
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > 1000:
            pipe_count += 1
            pipe_height = random.randint(-200, 100)
            bottom_pipe = Pipe(SCREEN_WIDTH, SCREEN_HEIGHT // 2 + pipe_height, -1, pipe_count % 2)
            top_pipe = Pipe(SCREEN_WIDTH, SCREEN_HEIGHT // 2 + pipe_height, 1, pipe_count % 2)
            pipe_group.add(bottom_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        pipe_group.update()

        if game_over is False:
            scroll_background -= speed_scroll_background
            if scroll_background < -427:
                scroll_background = 0

            scroll_ground -= speed_scroll_ground
            if scroll_ground < -100:
                scroll_ground = 0

    if game_over is True:

        if score > int(record.best_record):
            record.new_record(str(score))
            medal = 1

        record.draw(medal, score)

        if button.draw_gameover() is True:
            game_over = False
            restart_game()

    if fly is False and game_over is False:
        button.draw_start()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()

        if event.type == pygame.MOUSEBUTTONDOWN and fly is False and game_over is False:
            fly = True

        if event.type == animation:
            flappy.animation()

    pygame.display.flip()
