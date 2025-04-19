# ---------------------------------------------------------------
# Rogue Invaders - Jogo do tipo plataforma/arcade feito com PgZero
# Autor: Rui Tobias Carvalho
# Data: Abril de 2025
#
# Descrição:
# Este jogo foi desenvolvido como parte de um projeto educacional.
# Apresenta animações de sprite, inimigos com comportamento dinâmico,
# sons, um menu funcional e sistema de pontuação/vidas.
# ---------------------------------------------------------------

import random
from pgzero.builtins import Actor, keyboard, sounds, Rect

# -------------------- CONFIGURAÇÕES GERAIS --------------------
TITLE = "INVASORES DO ESPAÇO"
WIDTH = 800
HEIGHT = 600
PLAYER_SPEED = 5
ENEMY_SPEED = 2
ATTACK_COOLDOWN = 10         # Tempo entre disparos do jogador
ENEMY_SHOOT_CHANCE = 0.01    # Chance do inimigo atirar a cada frame

# -------------------- CLASSE DO JOGADOR --------------------
class Player:
    def __init__(self):
        # Cria a nave do jogador no centro inferior da tela
        self.actor = Actor('ship', (WIDTH // 2, HEIGHT - 60))
        self.speed = PLAYER_SPEED
        self.lives = 3
        self.score = 0
        self.cooldown = 0
        self.animation_frame = 0
        self.animation_timer = 0

    def update(self):
        # Movimento com teclado
        if keyboard.left and self.actor.x > 40:
            self.actor.x -= self.speed
        if keyboard.right and self.actor.x < WIDTH - 40:
            self.actor.x += self.speed

        # Animação da nave (alterna entre dois frames)
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.animation_frame = 1 - self.animation_frame
            self.actor.image = f"hero_{self.animation_frame + 1}"

        # Reduz o cooldown dos tiros
        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self):
        # Dispara um projétil se o cooldown for zero
        if self.cooldown <= 0:
            if game.sound_on:
                sounds.shoot.play()
            self.cooldown = ATTACK_COOLDOWN
            return Bullet(self.actor.x, self.actor.y - 20, -1, 'laser')
        return None

    def draw(self):
        self.actor.draw()

# -------------------- CLASSE DO PROJÉTIL --------------------
class Bullet:
    def __init__(self, x, y, direction, image):
        self.actor = Actor(image, (x, y))
        self.direction = direction
        self.speed = 10
        self.active = True

    def update(self):
        # Movimento vertical do projétil
        self.actor.y += self.speed * self.direction
        if self.actor.y < 0 or self.actor.y > HEIGHT:
            self.active = False

    def draw(self):
        self.actor.draw()

# -------------------- CLASSE DO INIMIGO --------------------
class Enemy:
    def __init__(self, x, y):
        # Escolhe aleatoriamente um tipo de inimigo
        self.type = random.choice(['enemy1', 'enemy2', 'enemy3'])
        self.frame = 0
        self.actor = Actor(f'{self.type}_1', (x, y))
        self.actor.scale = 0.8
        self.speed = ENEMY_SPEED
        self.health = 100
        self.animation_timer = 0

    def update(self):
        self.actor.x += self.speed
        if self.actor.x > WIDTH - 40 or self.actor.x < 40:
            self.speed *= -1
            self.actor.y += 30

        # Alterna entre frame 1 e 2 da imagem do tipo de inimigo
        self.animation_timer += 1
        if self.animation_timer >= 20:
            self.animation_timer = 0
            self.frame = 1 - self.frame
            self.actor.image = f'{self.type}_{self.frame + 1}'

    def shoot(self):
        if random.random() < ENEMY_SHOOT_CHANCE:
            return Bullet(self.actor.x, self.actor.y + 20, 1, 'enemylaser')
        return None

    def draw(self):
        self.actor.draw()

# -------------------- CLASSE PRINCIPAL DO JOGO --------------------
class Game:
    def __init__(self):
        self.state = "menu"  # Estados: menu, playing, gameover
        self.player = None
        self.enemies = []
        self.bullets = []
        self.enemy_bullets = []
        self.wave = 1
        self.sound_on = True
        self.high_score = 0

        # Botões clicáveis
        self.start_button = Rect(WIDTH // 2 - 100, 280, 200, 40)
        self.sound_button = Rect(WIDTH // 2 - 100, 330, 200, 40)
        self.quit_button = Rect(WIDTH // 2 - 100, 380, 200, 40)
        self.restart_button = Rect(WIDTH // 2 - 100, 400, 200, 40)

    def start_game(self):
        # Inicia o jogo
        self.state = "playing"
        self.player = Player()
        self.spawn_enemies()
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.wave = 1

    def spawn_enemies(self):
        # Gera inimigos organizados em 2 linhas de 3
        self.enemies.clear()
        for i in range(2):
            for j in range(5):
                x = 150 + j * 200
                y = 100 + i * 100
                self.enemies.append(Enemy(x, y))

    def update(self):
        if self.state != "playing":
            return

        self.player.update()

        # Atualiza balas do jogador
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)

        # Atualiza balas dos inimigos
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.enemy_bullets.remove(bullet)

        # Atualiza inimigos e seus tiros
        for enemy in self.enemies[:]:
            enemy.update()
            if new_bullet := enemy.shoot():
                self.enemy_bullets.append(new_bullet)

        # Verifica colisões
        self.check_collisions()

        # Próxima onda se todos os inimigos morrerem
        if not self.enemies:
            self.wave += 1
            self.spawn_enemies()

    def check_collisions(self):
        # Colisão entre tiro do jogador e inimigos
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if abs(bullet.actor.x - enemy.actor.x) < 30 and abs(bullet.actor.y - enemy.actor.y) < 30:
                    enemy.health -= 50
                    if enemy.health <= 0:
                        self.player.score += 30
                        if self.sound_on:
                            sounds.invaderkilled.play()
                        self.enemies.remove(enemy)
                    bullet.active = False

        # Colisão entre tiro inimigo e jogador
        for bullet in self.enemy_bullets[:]:
            if abs(bullet.actor.x - self.player.actor.x) < 30 and abs(bullet.actor.y - self.player.actor.y) < 30:
                self.player.lives -= 1
                bullet.active = False
                if self.sound_on:
                    sounds.shipexplosion.play()
                if self.player.lives <= 0:
                    if self.player.score > self.high_score:
                        self.high_score = self.player.score
                    self.state = "gameover"

    # -------------------- TELAS DO JOGO --------------------

    def draw_menu(self):
        screen.clear()
        screen.blit('background', (0, 0))
        screen.draw.text("INVASORES DO ESPAÇO", center=(WIDTH//2, 150), fontsize=60, color="white")
        screen.draw.filled_rect(self.start_button, "green")
        screen.draw.text("INICIAR JOGO", center=(WIDTH//2, 300), fontsize=40, color="white")
        sound_color = "green" if self.sound_on else "red"
        screen.draw.filled_rect(self.sound_button, sound_color)
        sound_text = "SOM: LIGADO" if self.sound_on else "SOM: DESLIGADO"
        screen.draw.text(sound_text, center=(WIDTH//2, 350), fontsize=40, color="white")
        screen.draw.filled_rect(self.quit_button, "red")
        screen.draw.text("SAIR", center=(WIDTH//2, 400), fontsize=40, color="white")
        screen.draw.text(f"RECORDE: {self.high_score}", center=(WIDTH//2, 470), fontsize=30, color="yellow")

    def draw_game(self):
        screen.clear()
        screen.blit('background', (0, 0))
        for enemy in self.enemies:
            enemy.draw()
        for bullet in self.bullets + self.enemy_bullets:
            bullet.draw()
        self.player.draw()
        screen.draw.text(f"VIDAS: {self.player.lives}", topleft=(20, 20), fontsize=30, color="white")
        screen.draw.text(f"PONTOS: {self.player.score}", topleft=(20, 50), fontsize=30, color="white")
        screen.draw.text(f"ONDA: {self.wave}", topleft=(20, 80), fontsize=30, color="white")

    def draw_game_over(self):
        screen.clear()
        screen.blit('background', (0, 0))
        screen.draw.text("FIM DE JOGO", center=(WIDTH//2, 200), fontsize=60, color="white")
        screen.draw.text(f"PONTUAÇÃO: {self.player.score}", center=(WIDTH//2, 300), fontsize=50, color="white")
        screen.draw.text(f"RECORDE: {self.high_score}", center=(WIDTH//2, 380), fontsize=40, color="yellow")
        screen.draw.filled_rect(self.restart_button, "blue")
        screen.draw.text("REINICIAR", center=(WIDTH//2, 450), fontsize=40, color="white")

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "gameover":
            self.draw_game_over()

    # -------------------- EVENTO DE CLIQUE DO MOUSE --------------------
    def on_mouse_down(self, pos):
        if self.state == "menu":
            if self.start_button.collidepoint(pos):
                self.start_game()
            elif self.sound_button.collidepoint(pos):
                self.sound_on = not self.sound_on
            elif self.quit_button.collidepoint(pos):
                quit()
        elif self.state == "gameover":
            if self.restart_button.collidepoint(pos):
                self.start_game()

# -------------------- INSTÂNCIA E FUNÇÕES DO PYGZERO --------------------
game = Game()

def update():
    game.update()
    if game.state == "playing" and keyboard.space:
        bullet = game.player.shoot()
        if bullet:
            game.bullets.append(bullet)

def draw():
    game.draw()

def on_mouse_down(pos):
    game.on_mouse_down(pos)
