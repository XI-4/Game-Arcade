
import sys
import random
import pygame
from pygame.locals import *

pygame.init()

from pygame.display import update
from pygame.sprite import Sprite as SS
from pygame.mixer import Sound

''' IMAGES '''

playerShip = 'plyship.png'
enemyShip = 'enemyship.png'
ufoShip = 'ufo.png'
playerBullet = 'pbullet.png'
enemyBullet = 'enemybullet.png'
ufoBullet = 'enemybullet.png'

''' SOUND '''
laser_sound = Sound('laser.wav')
explosion_sound = Sound('low_expl.wav')
goSound = Sound('herewego.mp3')
gameOverDelay = Sound('game_over.wav')
startScreenMusic = Sound('bgm.mp3')
gameOverMusic = Sound('bgm.mp3')

backgroundMusic = pygame.mixer.music.load('bgm.mp3')

pygame.mixer.init()

screen = pygame.display.set_mode((0,0), FULLSCREEN)
s_width, s_height = screen.get_size()

clock = pygame.time.Clock()
FPS = 60

backgroundGroup = pygame.sprite.Group()
playerGroup = pygame.sprite.Group()
enemyGroup = pygame.sprite.Group()
ufoGroup = pygame.sprite.Group()
playerbulletGroup = pygame.sprite.Group()
enemybulletGroup = pygame.sprite.Group()
ufobulletGroup = pygame.sprite.Group()
explosionGroup = pygame.sprite.Group()
particleGroup = pygame.sprite.Group()


spriteGroup = pygame.sprite.Group()

pygame.mouse.set_visible(False)

class Background(SS):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([x,y])
        self.image.fill('white')
        self.image.set_colorkey('black')
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y += 1
        self.rect.x += 1 
        if self.rect.y > s_height:
            self.rect.y = random.randrange(-10, 0)
            self.rect.x = random.randrange(-400, s_width)

class Particle(Background):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.rect.x = random.randrange(0, s_width)
        self.rect.y = random.randrange(0, s_height)
        self.image.fill('grey')
        self.vel = random.randint(3,8)
    def update(self):
        self.rect.y += self.vel 
        if self.rect.y > s_height:
            self.rect.x = random.randrange(0, s_width)
            self.rect.y = random.randrange(0, s_height)

class Player(SS):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')
        self.alive = True
        self.countToLive = 0 
        self.activateBullet = True
        self.alpha_duration = 0
    def update(self):
        if self.alive:
            self.image.set_alpha(80)
            self.alpha_duration += 1
            if self.alpha_duration > 170:
                self.image.set_alpha(255)
            mouse = pygame.mouse.get_pos()
            self.rect.x = mouse[0] - 20
            self.rect.y = mouse[1] + 40
        else:
            self.alpha_duration = 0
            expl_x = self.rect.x + 20
            expl_y = self.rect.y + 40
            explosion = Explosion(expl_x, expl_y)
            explosionGroup.add(explosion)
            spriteGroup.add(explosion)
            pygame.time.delay(22)
            self.rect.y = s_height + 200
            self.countToLive += 1
            if self.countToLive > 100:
                self.alive = True
                self.countToLive = 0
                self.activateBullet = True
    def shoot(self):
        if self.activateBullet:
            bullet = PlayerBullet(playerBullet)
            mouse = pygame.mouse.get_pos()
            bullet.rect.x = mouse[0]
            bullet.rect.y = mouse[1]
            playerbulletGroup.add(bullet)
            spriteGroup.add(bullet)
    def dead(self):
        Sound.play(explosion_sound)
        self.alive = False
        self.activateBullet = False

class Enemy(Player):
    def __init__(self, img):
        super().__init__(img)
        self.rect.x = random.randrange(80, s_width-80)
        self.rect.y = random.randrange(-500, 0)
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        self.rect.y += 1
        if self.rect.y > s_height:
            self.rect.x = random.randrange(80, s_width-50)
            self.rect.y = random.randrange(-2000, 0)
        self.shoot()

    def shoot(self):
        if self.rect.y in (0, 300, 700):
            enemybullet = EnemyBullet(enemyBullet)
            enemybullet.rect.x = self.rect.x + 20
            enemybullet.rect.y = self.rect.y + 50
            enemybulletGroup.add(enemybullet)
            spriteGroup.add(enemybullet)


class Ufo(Enemy):
    def __init__(self, img):
        super().__init__(img)
        self.rect.x = -200 
        self.rect.y = 200 
        self.move = 1
    def update(self):
        self.rect.x += self.move 
        if self.rect.x > s_width + 200:
            self.move *= -1 
        elif self.rect.x < -200:
            self.move *= -1
        self.shoot()
    def shoot(self):
        if self.rect.x % 50 == 0:
            ufobullet = EnemyBullet(ufoBullet)
            ufobullet.rect.x = self.rect.x + 50
            ufobullet.rect.y = self.rect.y + 70
            ufobulletGroup.add(ufobullet)
            spriteGroup.add(ufobullet)

class PlayerBullet(SS):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')
    def update(self):
        self.rect.y -= 18
        if self.rect.y < 0:
            self.kill()

class EnemyBullet(PlayerBullet):
    def __init__(self, img):
        super().__init__(img)
        self.image.set_colorkey('white')

    def update(self):
        self.rect.y += 3
        if self.rect.y > s_height:
            self.kill()

class Explosion(SS):
    def __init__(self, x, y):
        super().__init__()
        self.img_list = []
        for i in range(1, 6):
            img = pygame.image.load(f'exp{i}.png').convert()
            img.set_colorkey('black')
            img = pygame.transform.scale(img, (120, 120))
            self.img_list.append(img)
        self.index = 0
        self.image = self.img_list[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.count_delay = 0 

    def update(self):
        self.count_delay += 1
        if self.count_delay >= 12:
            if self.index < len(self.img_list) - 1:
                self.count_delay = 0
                self.index += 1
                self.image = self.img_list[self.index]
        if self.index >= len(self.img_list) - 1:
            if self.count_delay >= 12:
                self.kill()

class Game:
    def __init__(self):
        self.count_hit = 0 
        self.count_hit2 = 0 
        self.lives = 3
        self.score = 0
        self.init_create = True
        self.gameOverSoundDelay = 0
        self.startScreen()

    def startText(self):
        font = pygame.font.SysFont('Calibri', 50)
        text = font.render('SPACE WAR', True, 'blue')
        textRect = text.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text, textRect)

        font2 = pygame.font.SysFont('Calibri', 20)
        text2 = font2.render('PythonProject 2022', True, 'white')
        text2_rect = text2.get_rect(center=(s_width/2, s_height/2+60))
        screen.blit(text2, text2_rect)

    def startScreen(self):
        Sound.stop(gameOverMusic)
        Sound.play(startScreenMusic)
        self.lives = 3 
        spriteGroup.empty()
        while True: 
            screen.fill('black')
            self.startText()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_RETURN:
                        self.run_game()
            update()

    def pause_text(self):
        font = pygame.font.SysFont('Calibri', 50)
        text = font.render('PAUSED', True, 'white')
        textRect = text.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text, textRect)

    def pause_screen(self):
        self.init_create = False
        while True: 
            self.pause_text()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_SPACE:
                        self.run_game()
            update()

    def game_over_text(self):
        font = pygame.font.SysFont('Calibri', 50)
        text = font.render('GAME OVER', True, 'red')
        textRect = text.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text, textRect)

    def game_over_screen(self):
        pygame.mixer.music.stop()
        Sound.play(gameOverDelay)
        while True: 
            screen.fill('black')
            self.game_over_text()
            self.gameOverSoundDelay += 1
            if self.gameOverSoundDelay > 1400:
                Sound.play(gameOverMusic)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.startScreen()

            update()

    def create_background(self):
        for i in range(20):
            x = random.randint(1,6)
            backgroundImage = Background(x,x)
            backgroundImage.rect.x = random.randrange(0, s_width)
            backgroundImage.rect.y = random.randrange(0, s_height)
            backgroundGroup.add(backgroundImage)
            spriteGroup.add(backgroundImage)

    def create_particles(self):
        for i in range(70):
            x = 1 
            y = random.randint(1,7)
            particle = Particle(x, y)
            particleGroup.add(particle)
            spriteGroup.add(particle)

    def create_player(self):
        self.player = Player(playerShip)
        playerGroup.add(self.player)
        spriteGroup.add(self.player)

    def create_enemy(self):
        for i in range(10):
            self.enemy = Enemy(enemyShip)
            enemyGroup.add(self.enemy)
            spriteGroup.add(self.enemy)

    def create_ufo(self):
        for i in range(1):
            self.ufo = Ufo(ufoShip)
            ufoGroup.add(self.ufo)
            spriteGroup.add(self.ufo)

    def playerbullet_hits_enemy(self):
        hits = pygame.sprite.groupcollide(enemyGroup, playerbulletGroup, False, True)
        for i in hits:
            self.count_hit += 1
            if self.count_hit == 3:
                self.score += 10
                expl_x = i.rect.x + 20
                expl_y = i.rect.y + 40
                explosion = Explosion(expl_x, expl_y)
                explosionGroup.add(explosion)
                spriteGroup.add(explosion)
                i.rect.x = random.randrange(0, s_width)
                i.rect.y = random.randrange(-3000, -100)
                self.count_hit = 0
                Sound.play(explosion_sound)

    def playerbullet_hits_ufo(self):
        hits = pygame.sprite.groupcollide(ufoGroup, playerbulletGroup, False, True)
        for i in hits:
            self.count_hit2 += 1
            if self.count_hit2 == 40:
                self.score += 50
                expl_x = i.rect.x + 50
                expl_y = i.rect.y + 60
                explosion = Explosion(expl_x, expl_y)
                explosionGroup.add(explosion)
                spriteGroup.add(explosion)
                i.rect.x = -199
                self.count_hit2 = 0
                Sound.play(explosion_sound)

    def enemybullet_hits_player(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, enemybulletGroup, True)
            if hits:
                self.lives -= 1
                self.player.dead()
                if self.lives < 0:
                    self.game_over_screen()

    def ufobullet_hits_player(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, ufobulletGroup, True)
            if hits:
                self.lives -= 1
                self.player.dead()
                if self.lives < 0:
                    self.game_over_screen()

    def player_enemy_crash(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, enemyGroup, False)
            if hits:
                for i in hits:
                    i.rect.x = random.randrange(0, s_width)
                    i.rect.y = random.randrange(-3000, -100)
                    self.lives -= 1
                    self.player.dead()
                    if self.lives < 0:
                        self.game_over_screen()

    def player_ufo_crash(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, ufoGroup, False)
            if hits:
                for i in hits:
                    i.rect.x = -199
                    self.lives -= 1
                    self.player.dead()
                    if self.lives < 0:
                        self.game_over_screen()

    def create_lives(self):
        self.live_img = pygame.image.load(playerShip)
        self.live_img = pygame.transform.scale(self.live_img, (20,23))
        n = 0
        for i in range(self.lives):
            screen.blit(self.live_img, (0+n, s_height-860))
            n += 60

    def create_score(self):
        score = self.score 
        font = pygame.font.SysFont('Calibri', 30)
        text = font.render("Score: "+str(score), True, 'green')
        textRect = text.get_rect(center=(s_width-150, s_height-850))
        screen.blit(text, textRect)

    def run_update(self):
        spriteGroup.draw(screen)
        spriteGroup.update()

    def run_game(self):
        Sound.stop(startScreenMusic)
        Sound.play(goSound)
        pygame.mixer.music.play(-1)
        if self.init_create:
            self.create_background()
            self.create_particles()
            self.create_player()
            self.create_enemy()
            self.create_ufo()
        while True:
            screen.fill('black')
            self.playerbullet_hits_enemy()
            self.playerbullet_hits_ufo()
            self.enemybullet_hits_player()
            self.ufobullet_hits_player()
            self.player_enemy_crash()
            self.player_ufo_crash()
            self.run_update()
            pygame.draw.rect(screen, 'black', (0,0,s_width,30))
            self.create_lives()
            self.create_score()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    Sound.play(laser_sound)
                    self.player.shoot()
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if event.key == K_SPACE:
                        self.pause_screen()

            update()
            clock.tick(FPS)

def main():
    game = Game()

if __name__ == '__main__':
    main()
