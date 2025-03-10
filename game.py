import sys
import random

import pygame
from pygame.locals import *

pygame.init()

''' IMAGES '''

player_ship = 'orang.png'
enemy_ship = 'enemy1.png'
ufo_ship = 'ufo.png'
player_bullet = 'bullet1.png'
enemy_bullet = 'enemybullet1.png'
ufo_bullet = "ufobullet2.png"

''' SOUND '''

laser_sound = pygame.mixer.Sound('laser.mp3')
explosion_sound = pygame.mixer.Sound('expl2.mp3')
go_sound = pygame.mixer.Sound('go.wav')
game_over_sound = pygame.mixer.Sound('game_over.wav')
start_screen_music = pygame.mixer.Sound('op.mp3')
game_over_music = pygame.mixer.Sound('illusoryrealm.mp3')

background_music = pygame.mixer.music.load('song6.mp3')

pygame.mixer.init()

screen = pygame.display.set_mode((0,0), FULLSCREEN)
s_width, s_height = screen.get_size()

clock = pygame.time.Clock()
FPS = 90

background_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
playerbullet_group = pygame.sprite.Group()
enemybullet_group = pygame.sprite.Group()
ufobullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()

sprite_group = pygame.sprite.Group()

pygame.mouse.set_visible(False)

class Background(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface([x,y])
        self.image.fill('green')
        self.image.set_colorkey('purple')
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
            self.rect.x = random.randrange(0,s_width)
            self.rect.y = random.randrange(0,s_height)
            

class Player(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')
        self.alive = True
        self.count_to_live = 0
        self.activate_bullet = True
        self.alpha_duration = 0

    def update(self):
        if self.alive:
            self.image.set_alpha(80)
            self.alpha_duration += 1
            if self.alpha_duration > 170:
                self.image.set_alpha(255)
            mouse = pygame.mouse.get_pos()
            self.rect.x = mouse[0]
            self.rect.y = mouse[1]
        else:
            self.alpha_duration = 0
            expl_x = self.rect.x +34
            expl_y = self.rect.y +34
            explosion = Explosion(expl_x, expl_y)
            explosion_group.add(explosion)
            sprite_group.add(explosion )
            self.rect.y = s_height + 200
            self.count_to_live += 1
            if self.count_to_live > 100:
                self.alive = True
                self.count_to_live = 0
                self.activate_bullet = True
        
    def shoot(self):
        if self.activate_bullet:
            bullet = PlayerBullet(player_bullet)
            mouse = pygame.mouse.get_pos()
            bullet.rect.x = mouse[0] + 25
            bullet.rect.y = mouse[1] + -28
            playerbullet_group.add(bullet)
            sprite_group.add(bullet)
    
    def dead(self):
        pygame.mixer.Sound.play(explosion_sound)
        self.alive = False
        self.activate_bullet = False


class Enemy(Player):
    def __init__(self, img):
        super().__init__(img)
        self.rect.x = random.randrange(85, s_width-85)
        self.rect.y = random.randrange(-500, 0)
        screen.blit(self.image, (self.rect.x, self.rect.y))
    
    def update(self):
        self.rect.y += 1
        if self.rect.y > s_height:
            self.rect.x = random.randrange(85, s_width-85)
            self.rect.y = random.randrange(-2000, 0)
        self.shoot()
    
    def shoot(self):
        if self.rect.y in (0, 27, 70, 285, 700):
            enemybullet = EnemyBullet(enemy_bullet)
            enemybullet.rect.x = self.rect.x + 24
            enemybullet.rect.y = self.rect.y + 80
            enemybullet_group.add(enemybullet)
            sprite_group.add(enemybullet)

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
        if self.rect.x % 90 == 0:
            ufobullet = EnemyBullet(ufo_bullet)
            ufobullet.rect.x = self.rect.x + 65
            ufobullet.rect.y = self.rect.y + 118
            ufobullet_group.add(ufobullet)
            sprite_group.add(ufobullet)

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey('white')

    def update(self):
        self.rect.y -= 12
        if self.rect.y < 0:
            self.kill()

class EnemyBullet(PlayerBullet):
    def __init__(self, img):
        super().__init__(img)
        self.image.set_colorkey('black')
    
    def update(self):
        self.rect.y += 3
        if self.rect.y > s_height:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.img_list = []
        for i in range(1, 8):
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
        self.game_over_sound_delay = 0

        self.start_screen()

    def start_text(self):
        font = pygame.font.SysFont('Garamond', 150)
        text = font.render('- Orion Outlaws -', True, 'purple')
        text_rect = text.get_rect(center=(s_width/2, s_height/2-25))
        screen.blit(text, text_rect)

        font = pygame.font.SysFont('Garamond', 53)
        text2 = font.render('. The Last Starfighters .', True, 'purple')
        text2_rect = text2.get_rect(center=(s_width/2, s_height/2+80))
        screen.blit(text2, text2_rect)
    
        font = pygame.font.SysFont('Times New Roman', 20)
        text2 = font.render('~ created by dams ~', True, 'white')
        text2_rect = text2.get_rect(center=(s_width/2, s_height/2-120))
        screen.blit(text2, text2_rect)
    
    def start_screen(self):
        pygame.mixer.Sound.stop(game_over_music)
        pygame.mixer.Sound.play(start_screen_music)
        self.lives = 3
        sprite_group.empty()
        while True:
            screen.fill('black')
            self.start_text()
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
            
            pygame.display.update()

    def pause_text(self):
        font = pygame.font.SysFont('Garamond', 60)
        text = font.render('PAUSED', True, 'black')
        text_rect = text.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text, text_rect)

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
            
            pygame.display.update()
    
    def game_over_text(self):
        font = pygame.font.SysFont('Garamond', 100)
        text = font.render('- GAME OVER -', True, 'red')
        text_rect = text.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text, text_rect)

    def game_over_screen(self):
        pygame.mixer.music.stop()
        pygame.mixer.Sound.play(game_over_sound)
        while True:
            screen.fill('black')
            self.game_over_text()
            self.game_over_sound_delay += 1
            if self.game_over_sound_delay > 1250:
                pygame.mixer.Sound.play(game_over_music)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                       self.start_screen()
            
            pygame.display.update()

    def create_background(self):
        for i in range(90):
            x = random.randint(0,6)
            background_image = Background(x,x)
            background_image.rect.x = random.randrange(0, s_width)
            background_image.rect.y = random.randrange(0, s_height)
            background_group.add(background_image)
            sprite_group.add(background_image)
    
    def create_particles(self):
        for i in range(100):
            x = 1
            y = random.randint(1,7)
            particle = Particle(x,y)
            particle_group.add(particle)
            sprite_group.add(particle)
    
    def create_player(self):
        self.player = Player(player_ship)
        player_group.add(self.player)
        sprite_group.add(self.player)
        
    def create_enemy(self):
        for i in range(12):
            self.enemy = Enemy(enemy_ship)
            enemy_group.add(self.enemy)
            sprite_group.add(self.enemy)
    
    def create_ufo(self):
        for i in range(25):
            self.ufo = Ufo(ufo_ship)
            ufo_group.add(self.ufo)
            sprite_group.add(self.ufo)
    
    def playerbullet_hits_enemy(self):
        hits = pygame.sprite.groupcollide(enemy_group, playerbullet_group, False, True)
        for i in hits:
            self.count_hit += 1
            if self.count_hit == 3:
                self.score += 10
                expl_x = i.rect.x +50
                expl_y = i.rect.y +53 
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                i.rect.x = random.randrange(0, s_width)
                i.rect.y = random.randrange(-3000, -100)
                self.count_hit = 0
                pygame.mixer.Sound.play(explosion_sound)

    def playerbullet_hits_ufo(self):
        hits = pygame.sprite.groupcollide(ufo_group, playerbullet_group, False, True)
        for i in hits:
            self.count_hit2 += 1
            if self.count_hit2 == 50000000:
                self.score += 900
                expl_x = i.rect.x +50
                expl_y = i.rect.y +53 
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                i.rect.x = -199
                self.count_hit2 = 0
                pygame.mixer.Sound.play(explosion_sound)

    def enemybullet_hits_player(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, enemybullet_group, True)
            if hits:
                self.lives -= 1
                self.player.dead()
                if self.lives < 0 :
                    self.game_over_screen()
    
    def player_enemy_crash(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, enemy_group, False)
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
            hits = pygame.sprite.spritecollide(self.player, ufo_group, False)
            if hits:
                for i in hits:
                    i.rect.x = -199
                    self.lives -= 1
                    self.player.dead()
                    if self.lives < 0:
                        self.game_over_screen()

    def ufobullet_hits_player(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, ufobullet_group, True)
            if hits:
                self.lives -= 1
                self.player.dead()
                if self.lives < 0:
                    self.game_over_screen()
    
    def create_lives(self):
        self.live_img = pygame.image.load(player_ship)
        self.live_img = pygame.transform.scale(self.live_img, (55,55))
        n = 0
        for i in range(self.lives):
            screen.blit(self.live_img, (870+n, s_height-96))
            n += 76
    
    def create_score(self):
        score = self.score
        font = pygame.font.SysFont('Calibri', 30)
        text = font.render("Score: "+str(score),True, 'green')
        text_rect = text.get_rect(center=(s_width-150, s_height-850))
        screen.blit(text, text_rect)


    def run_update(self):
        sprite_group.draw(screen)
        sprite_group.update()

    def run_game(self):
        pygame.mixer.Sound.stop(start_screen_music)
        pygame.mixer.Sound.play(go_sound)
        pygame.mixer.music.play(-1)
        if self.init_create:
            self.create_background()
            self.create_particles()
            self.create_player()
            self.create_enemy()
            self.create_ufo()
        while True: 
            screen.fill('purple')
            self.playerbullet_hits_enemy()
            self.playerbullet_hits_ufo()
            self.enemybullet_hits_player()
            self.ufobullet_hits_player()
            self.player_enemy_crash()
            self.player_ufo_crash()  
            self.run_update()
            pygame.draw.rect(screen, 'purple', (0,982,s_width,100)) 
            self.create_lives()
            self.create_score()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == KEYDOWN:  
                    pygame.mixer.Sound.play(laser_sound)
                    self.player.shoot()
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    
                    if event.key == K_SPACE:
                        self.pause_screen()
            
            pygame.display.update()
            clock.tick(FPS)

def main():
    game = Game()

if __name__ == '__main__':
    main()