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
    def __init__(self):
        self.actor = Actor('enemy1_1', (WIDTH//2, 100))
        self.actor.scale = 0.8
        self.speed = ENEMY_SPEED
        self.health = 100
        self.frame = 0
        self.animation_timer = 0

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
            self.actor.image = f'enemy1_{self.frame+1}'

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
        self.enemy = None
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
        self.spawn_enemy()
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.wave = 1

    def spawn_enemy(self):
        self.enemy = Enemy()

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

        # Atualiza o inimigo
        if self.enemy:
            self.enemy.update()
            if new_bullet := self.enemy.shoot():
                self.enemy_bullets.append(new_bullet)

        # Verifica colisões
        self.check_collisions()

        # Cria novo inimigo se o anterior foi destruído
        if not self.enemy:
            self.wave += 1
            self.spawn_enemy()

    def check_collisions(self):
        # Verifica se alguma bala do jogador atingiu o inimigo
        for bullet in self.bullets[:]:
            if self.enemy and abs(bullet.actor.x - self.enemy.actor.x) < 30 and abs(bullet.actor.y - self.enemy.actor.y) < 30:
                self.enemy.health -= 50
                if self.enemy.health <= 0:
                    self.player.score += 30
                    sounds.invaderkilled.play()
                    self.enemy = None
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
        sound_text = "SOM: LIGADO" if self.sound_on else "SOM: DESLIGADO"
        screen.draw.text(sound_text, center=(WIDTH//2, 350), fontsize=40, color="white")
        screen.draw.filled_rect(self.quit_button, "red")
        screen.draw.text("SAIR", center=(WIDTH//2, 400), fontsize=40, color="white")
        screen.draw.text(f"RECORDE: {self.high_score}", center=(WIDTH//2, 470), fontsize=30, color="yellow")

    def draw_game(self):
        # Tela do jogo em execução
        screen.clear()
        screen.blit('background', (0, 0))
        if self.enemy:
            self.enemy.draw()
        for bullet in self.bullets + self.enemy_bullets:
            bullet.draw()
        self.player.draw()
        screen.draw.text(f"VIDAS: {self.player.lives}", topleft=(20, 20), fontsize=30, color="white")
        screen.draw.text(f"PONTOS: {self.player.score}", topleft=(20, 50), fontsize=30, color="white")
        screen.draw.text(f"ONDA: {self.wave}", topleft=(20, 80), fontsize=30, color="white")

    def draw_game_over(self):
        # Tela de fim de jogo
        screen.clear()
        screen.blit('background', (0, 0))
        screen.draw.text("FIM DE JOGO", center=(WIDTH//2, 200), fontsize=60, color="red")
        screen.draw.text(f"PONTUAÇÃO FINAL: {self.player.score}", center=(WIDTH//2, 280), fontsize=40, color="white")
        screen.draw.text(f"RECORDE: {self.high_score}", center=(WIDTH//2, 330), fontsize=40, color="yellow")
        screen.draw.text("PRESSIONE 'S' PARA RECOMEÇAR", center=(WIDTH//2, 380), fontsize=30, color="green")
        screen.draw.filled_rect(self.restart_button, "blue")
        screen.draw.text("REINICIAR", center=(WIDTH//2, 420), fontsize=40, color="white")

    def draw(self):
        # Desenha a tela correspondente ao estado atual
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "gameover":
            self.draw_game_over()

    def on_mouse_down(self, pos):
        # Clique em botões do menu
        if self.state == "menu":
            if self.start_button.collidepoint(pos):
                self.start_game()
            elif self.sound_button.collidepoint(pos):
                self.sound_on = not self.sound_on
                sounds._muted = not self.sound_on
            elif self.quit_button.collidepoint(pos):
                exit()
        elif self.state == "gameover":
            if self.restart_button.collidepoint(pos):
                self.start_game()

    def on_key_down(self, key):
        # Controles do teclado
        if key == keys.S and self.state == "gameover":
            self.start_game()
        elif key == keys.ESCAPE:
            self.state = "menu"
        elif key == keys.RETURN and self.state == "menu":
            self.start_game()
        elif key == keys.SPACE and self.state == "playing":
            if new_bullet := self.player.shoot():
                self.bullets.append(new_bullet)

# Instância do jogo
game = Game()

# Funções padrão do Pygame Zero
def update():
    game.update()

def draw():
    game.draw()

def on_mouse_down(pos):
    game.on_mouse_down(pos)

def on_key_down(key):
    game.on_key_down(key)
