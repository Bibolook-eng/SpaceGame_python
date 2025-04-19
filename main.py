# ---------------------------------------------------------------
# Rogue Invaders - Jogo do tipo plataforma/arcade feito com PgZero
# Autor: Rui Tobias Carvalho
# Data: Abril de 2025
#
# Descrição:
# Este jogo foi desenvolvido como parte de um projeto educacional.
# Apresenta animações de sprite, inimigos com comportamento dinâmico,
# sons, um menu funcional e sistema de pontuação/vidas.
#
# Requisitos:
# - Python 3.x
# - Biblioteca PgZero (pgzrun)
#
# Contato:
# GitHub: https://github.com/Bibolook-eng
# LinkedIn: https://www.linkedin.com/in/ruitobias
# Email: ruitobiascarvalho@gmail.com
# ---------------------------------------------------------------

# ---------------------------------------------------------------
# Nota Educacional:
# Este projeto foi desenvolvido com fins educacionais, como parte
# do aprendizado sobre lógica de programação, desenvolvimento de jogos
# e uso da biblioteca PgZero. O foco principal está em conceitos como:
# - Animação de sprites em 2D
# - Gerenciamento de estados do jogo (menu, jogo, game over)
# - Controle de colisões e inimigos
# - Interface interativa com menus e pontuação
# - Estruturação de classes para organização de código
#
# Este código serve como base para exploração e aprimoramento futuro
# por estudantes interessados em programação de jogos com Python.
# ---------------------------------------------------------------


import random
from pgzero.builtins import Actor, keyboard, sounds, Rect

# Game constants
WIDTH = 800
HEIGHT = 600
PLAYER_SPEED = 5
ENEMY_SPEED = 2
ATTACK_COOLDOWN = 30
ENEMY_SHOOT_CHANCE = 0.01

class Player:
    def __init__(self):
        self.actor = Actor('ship', (WIDTH//2, HEIGHT-60))
        self.speed = PLAYER_SPEED
        self.lives = 3
        self.score = 0
        self.cooldown = 0
        self.animation_frame = 0
        self.animation_timer = 0
        
    def update(self):
        if keyboard.left and self.actor.x > 40:
            self.actor.x -= self.speed
        if keyboard.right and self.actor.x < WIDTH-40:
            self.actor.x += self.speed
            
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.animation_frame = 1 - self.animation_frame
            self.actor.image = f"hero_{self.animation_frame+1}"
            
        if self.cooldown > 0:
            self.cooldown -= 1
            
    def shoot(self):
        if self.cooldown <= 0:
            sounds.shoot.play()
            self.cooldown = ATTACK_COOLDOWN
            return Bullet(self.actor.x, self.actor.y-20, -1, 'laser')
        return None
        
    def draw(self):
        self.actor.draw()

class Bullet:
    def __init__(self, x, y, direction, image):
        self.actor = Actor(image, (x, y))
        self.direction = direction
        self.speed = 10
        self.active = True
        
    def update(self):
        self.actor.y += self.speed * self.direction
        if self.actor.y < 0 or self.actor.y > HEIGHT:
            self.active = False
            
    def draw(self):
        self.actor.draw()

class Enemy:
    def __init__(self):
        self.actor = Actor('enemy1_1', (WIDTH//2, 100))  # Único inimigo no centro
        self.actor.scale = 0.8
        self.speed = ENEMY_SPEED
        self.health = 100
        self.frame = 0
        self.animation_timer = 0
        
    def update(self):
        # Movimento lateral simples
        self.actor.x += self.speed
        if self.actor.x > WIDTH - 40 or self.actor.x < 40:
            self.speed *= -1
            self.actor.y += 30  # Desce um pouco quando bate na parede
            
        # Animação
        self.animation_timer += 1
        if self.animation_timer >= 20:
            self.animation_timer = 0
            self.frame = 1 - self.frame
            self.actor.image = f'enemy1_{self.frame+1}'
            
    def shoot(self):
        if random.random() < ENEMY_SHOOT_CHANCE:
            return Bullet(self.actor.x, self.actor.y+20, 1, 'enemylaser')
        return None
        
    def draw(self):
        self.actor.draw()

class Game:
    def __init__(self):
        self.state = "menu"
        self.player = None
        self.enemy = None  # Agora temos apenas um inimigo
        self.bullets = []
        self.enemy_bullets = []
        self.wave = 1
        self.sound_on = True
        
        # Menu buttons
        self.start_button = Rect(WIDTH//2 - 100, 280, 200, 40)
        self.sound_button = Rect(WIDTH//2 - 100, 330, 200, 40)
        self.quit_button = Rect(WIDTH//2 - 100, 380, 200, 40)
        
    def start_game(self):
        self.state = "playing"
        self.player = Player()
        self.spawn_enemy()
        self.bullets = []
        self.enemy_bullets = []
        self.wave = 1
        
    def spawn_enemy(self):
        self.enemy = Enemy()  # Cria apenas um inimigo
        
    def update(self):
        if self.state != "playing":
            return
            
        self.player.update()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
                
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.enemy_bullets.remove(bullet)
                
        # Update enemy
        if self.enemy:
            self.enemy.update()
            if new_bullet := self.enemy.shoot():
                self.enemy_bullets.append(new_bullet)
                
        # Check collisions
        self.check_collisions()
        
        # Next wave
        if not self.enemy:
            self.wave += 1
            self.spawn_enemy()
            
    def check_collisions(self):
        # Player bullets hit enemy
        for bullet in self.bullets[:]:
            if self.enemy and abs(bullet.actor.x - self.enemy.actor.x) < 30 and abs(bullet.actor.y - self.enemy.actor.y) < 30:
                self.enemy.health -= 50
                if self.enemy.health <= 0:
                    self.player.score += 30
                    sounds.invaderkilled.play()
                    self.enemy = None
                bullet.active = False
                    
        # Enemy bullets hit player
        for bullet in self.enemy_bullets[:]:
            if abs(bullet.actor.x - self.player.actor.x) < 30 and abs(bullet.actor.y - self.player.actor.y) < 30:
                self.player.lives -= 1
                bullet.active = False
                sounds.shipexplosion.play()
                if self.player.lives <= 0:
                    self.state = "gameover"

    # Resto dos métodos draw_menu(), draw_game(), draw_game_over() permanecem iguais
    def draw_menu(self):
        screen.clear()
        screen.blit('background', (0, 0))
        screen.draw.text("ROGUE INVADERS", center=(WIDTH//2, 150), fontsize=60, color="white")
        screen.draw.filled_rect(self.start_button, "green")
        screen.draw.text("START GAME", center=(WIDTH//2, 300), fontsize=40, color="white")
        sound_color = "green" if self.sound_on else "red"
        screen.draw.filled_rect(self.sound_button, sound_color)
        sound_text = "SOUND: ON" if self.sound_on else "SOUND: OFF"
        screen.draw.text(sound_text, center=(WIDTH//2, 350), fontsize=40, color="white")
        screen.draw.filled_rect(self.quit_button, "red")
        screen.draw.text("QUIT", center=(WIDTH//2, 400), fontsize=40, color="white")
        
    def draw_game(self):
        screen.clear()
        screen.blit('background', (0, 0))
        if self.enemy:
            self.enemy.draw()
        for bullet in self.bullets + self.enemy_bullets:
            bullet.draw()
        self.player.draw()
        screen.draw.text(f"LIVES: {self.player.lives}", topleft=(20, 20), fontsize=30, color="white")
        screen.draw.text(f"SCORE: {self.player.score}", topleft=(20, 50), fontsize=30, color="white")
        screen.draw.text(f"WAVE: {self.wave}", topleft=(20, 80), fontsize=30, color="white")
        
    def draw_game_over(self):
        screen.clear()
        screen.blit('background', (0, 0))
        screen.draw.text("GAME OVER", center=(WIDTH//2, 200), fontsize=60, color="red")
        screen.draw.text(f"FINAL SCORE: {self.player.score}", center=(WIDTH//2, 280), fontsize=40, color="white")
        screen.draw.text("PRESS S TO RESTART", center=(WIDTH//2, 350), fontsize=40, color="green")
        
    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "gameover":
            self.draw_game_over()
            
    def on_mouse_down(self, pos):
        if self.state == "menu":
            if self.start_button.collidepoint(pos):
                self.start_game()
            elif self.sound_button.collidepoint(pos):
                self.sound_on = not self.sound_on
                sounds._muted = not self.sound_on
            elif self.quit_button.collidepoint(pos):
                exit()
                    
    def on_key_down(self, key):
        if key == keys.S:
            if self.state == "gameover":
                self.start_game()
        elif key == keys.SPACE:
            if self.state == "playing":
                if new_bullet := self.player.shoot():
                    self.bullets.append(new_bullet)

# Initialize game
game = Game()

def update():
    game.update()

def draw():
    game.draw()

def on_mouse_down(pos):
    game.on_mouse_down(pos)

def on_key_down(key):
    game.on_key_down(key)