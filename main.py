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

# Configurações gerais do jogo
TITLE = "INVASORES DO ESPAÇO"
WIDTH = 800
HEIGHT = 600
PLAYER_SPEED = 5
ENEMY_SPEED = 2
ATTACK_COOLDOWN = 30         # Intervalo entre disparos do jogador
ENEMY_SHOOT_CHANCE = 0.01    # Chance de o inimigo atirar a cada frame

# Classe do jogador
class Player:
    def __init__(self):
        self.actor = Actor('ship', (WIDTH//2, HEIGHT-60))  # Cria a nave do jogador
        self.speed = PLAYER_SPEED
        self.lives = 3              # Número de vidas
        self.score = 0              # Pontuação
        self.cooldown = 0           # Tempo até o próximo disparo
        self.animation_frame = 0    # Frame atual da animação
        self.animation_timer = 0    # Temporizador da animação

    def update(self):
        # Movimenta a nave com as setas esquerda/direita
        if keyboard.left and self.actor.x > 40:
            self.actor.x -= self.speed
        if keyboard.right and self.actor.x < WIDTH - 40:
            self.actor.x += self.speed

        # Controla a animação da nave
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.animation_frame = 1 - self.animation_frame
            self.actor.image = f"hero_{self.animation_frame + 1}"

        # Diminui o cooldown do disparo
        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self):
        # Dispara um tiro se o cooldown estiver zerado
        if self.cooldown <= 0:
            sounds.shoot.play()
            self.cooldown = ATTACK_COOLDOWN
            return Bullet(self.actor.x, self.actor.y - 20, -1, 'laser')
        return None

    def draw(self):
        self.actor.draw()

# Classe de projéteis
class Bullet:
    def __init__(self, x, y, direction, image):
        self.actor = Actor(image, (x, y))
        self.direction = direction  # Direção: -1 (para cima), 1 (para baixo)
        self.speed = 10
        self.active = True

    def update(self):
        # Move o projétil na direção correta
        self.actor.y += self.speed * self.direction
        if self.actor.y < 0 or self.actor.y > HEIGHT:
            self.active = False

    def draw(self):
        self.actor.draw()

# Classe do inimigo
class Enemy:
    def __init__(self, x, y, enemy_type):
        self.actor = Actor(self.get_enemy_image(enemy_type), (x, y))
        self.actor.scale = 0.8  # Ajuste o tamanho do inimigo para ser do mesmo tamanho do jogador
        self.speed = ENEMY_SPEED
        self.health = 100
        self.frame = 0
        self.animation_timer = 0
        self.enemy_type = enemy_type

    def get_enemy_image(self, enemy_type):
        """Retorna a imagem do inimigo com base no tipo."""
        if enemy_type == 1:
            return random.choice(['enemy1_1', 'enemy1_2'])
        elif enemy_type == 2:
            return random.choice(['enemy2_1', 'enemy2_2'])
        elif enemy_type == 3:
            return random.choice(['enemy3_1', 'enemy3_2'])

    def update(self):
        # Movimento lateral e descida
        self.actor.x += self.speed
        if self.actor.x > WIDTH - 40 or self.actor.x < 40:
            self.speed *= -1
            self.actor.y += 30  # Desce um pouco a cada borda atingida

        # Alterna os frames de animação
        self.animation_timer += 1
        if self.animation_timer >= 20:
            self.animation_timer = 0
            self.frame = 1 - self.frame
            self.actor.image = self.get_enemy_image(self.enemy_type)

    def shoot(self):
        # Tiro aleatório com base em chance
        if random.random() < ENEMY_SHOOT_CHANCE:
            return Bullet(self.actor.x, self.actor.y+20, 1, 'enemylaser')
        return None

    def draw(self):
        self.actor.draw()

# Classe principal do jogo
class Game:
    def __init__(self):
        self.state = "menu"         # Estados: menu, playing, gameover
        self.player = None
        self.enemies = []           # Lista de inimigos
        self.bullets = []           # Balas do jogador
        self.enemy_bullets = []     # Balas dos inimigos
        self.wave = 1
        self.sound_on = True
        self.high_score = 0

        # Botões do menu (como retângulos clicáveis)
        self.start_button = Rect(WIDTH//2 - 100, 280, 200, 40)
        self.sound_button = Rect(WIDTH//2 - 100, 330, 200, 40)
        self.quit_button = Rect(WIDTH//2 - 100, 380, 200, 40)
        self.restart_button = Rect(WIDTH//2 - 100, 400, 200, 40)

    def start_game(self):
        self.state = "playing"
        self.player = Player()
        self.spawn_enemies()  # Modificado para gerar vários inimigos
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.wave = 1

    def spawn_enemies(self):
        # Gerar 6 inimigos dispostos em 2 linhas com 3 inimigos em cada
        self.enemies.clear()  # Limpa os inimigos anteriores, se houver
        for i in range(2):  # Duas linhas
            for j in range(3):  # Três inimigos por linha
                x = 150 + j * 200  # Espaçamento horizontal
                y = 100 + i * 100  # Espaçamento vertical
                enemy_type = random.choice([1, 2, 3])  # Escolhe aleatoriamente o tipo do inimigo
                self.enemies.append(Enemy(x, y, enemy_type))

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

        # Atualiza os inimigos
        for enemy in self.enemies[:]:
            enemy.update()
            if new_bullet := enemy.shoot():
                self.enemy_bullets.append(new_bullet)

        # Verifica colisões
        self.check_collisions()

        # Cria novos inimigos se todos forem destruídos
        if not self.enemies:
            self.wave += 1
            self.spawn_enemies()

    def check_collisions(self):
        # Verifica se alguma bala do jogador atingiu um inimigo
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if abs(bullet.actor.x - enemy.actor.x) < 30 and abs(bullet.actor.y - enemy.actor.y) < 30:
                    enemy.health -= 50
                    if enemy.health <= 0:
                        self.player.score += 30
                        sounds.invaderkilled.play()
                        self.enemies.remove(enemy)
                    bullet.active = False

        # Verifica se o jogador foi atingido
        for bullet in self.enemy_bullets[:]:
            if abs(bullet.actor.x - self.player.actor.x) < 30 and abs(bullet.actor.y - self.player.actor.y) < 30:
                self.player.lives -= 1
                bullet.active = False
                sounds.shipexplosion.play()
                if self.player.lives <= 0:
                    if self.player.score > self.high_score:
                        self.high_score = self.player.score
                    self.state = "gameover"

    def draw_menu(self):
        # Tela de menu
        screen.clear()
        screen.blit('background', (0, 0))
        screen.draw.text("INVASORES DO ESPAÇO", center=(WIDTH//2, 150), fontsize=60, color="white")
        screen.draw.filled_rect(self.start_button, "green")
        screen.draw.text("INICIAR JOGO", center=(WIDTH//2, 300), fontsize=40, color="white")
        sound_color = "green" if self.sound_on else "red"
        screen.draw.filled_rect(self.sound_button, sound_color)
        screen.draw.text("SOM", center=(WIDTH//2, 380), fontsize=40, color="white")
        screen.draw.filled_rect(self.quit_button, "red")
        screen.draw.text("SAIR", center=(WIDTH//2, 460), fontsize=40, color="white")

    def draw_game(self):
        # Tela de jogo
        screen.clear()
        screen.blit('background', (0, 0))
        self.player.draw()

        for bullet in self.bullets:
            bullet.draw()
        for enemy in self.enemies:
            enemy.draw()
        for bullet in self.enemy_bullets:
            bullet.draw()

        screen.draw.text(f"PONTUAÇÃO: {self.player.score}", center=(WIDTH//2, 300), fontsize=50, color="white")
        screen.draw.text(f"VIDAS: {self.player.lives}", center=(WIDTH//2, 360), fontsize=40, color="red")

    def draw_game_over(self):
        # Tela de fim de jogo
        screen.clear()
        screen.draw.text("GAME OVER", center=(WIDTH//2, 200), fontsize=60, color="white")
        screen.draw.text(f"PONTUAÇÃO FINAL: {self.player.score}", center=(WIDTH//2, 300), fontsize=50, color="white")
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

    def on_mouse_down(self, pos):
        if self.state == "menu":
            if self.start_button.collidepoint(pos):
                self.start_game()
            elif self.sound_button.collidepoint(pos):
                self.sound_on = not self.sound_on
            elif self.quit_button.collidepoint(pos):
                quit()
        elif self.state == "gameover" and self.restart_button.collidepoint(pos):
            self.start_game()

# Instancia o jogo
game = Game()

def update():
    game.update()

def draw():
    game.draw()

def on_mouse_down(pos):
    game.on_mouse_down(pos)

def on_key_down(key):
    if key == keys.SPACE and game.state == "playing":
        new_bullet = game.player.shoot()
        if new_bullet:
            game.bullets.append(new_bullet)
    elif key == keys.S and game.state == "gameover":
        game.start_game()
