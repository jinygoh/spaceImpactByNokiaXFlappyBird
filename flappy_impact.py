import pygame
import sys
import random
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
GREY = (128, 128, 128)

# Game States
MAIN_MENU = "MAIN_MENU"
LEVEL_TRANSITION = "LEVEL_TRANSITION"
GAMEPLAY = "GAMEPLAY"
PAUSE = "PAUSE"
GAME_OVER = "GAME_OVER"

# --- Asset Placeholders ---
# Player: Yellow Triangle (pointing right)
# Player Bullet: Small White Rectangle
# Enemies: Drone (Red Square), Weaver (Purple Circle), Shooter (Red Triangle), Homer (Orange Diamond)
# Hazard: Asteroid (Grey, irregular polygon)
# Power-ups: Rapid Fire (Blue 'R'), Spread Shot (Green 'S'), Shield (Cyan 'H'), 1-UP (Heart icon)
# Bosses: Use large, composite shapes.

# --- Sound Placeholder ---
def play_sound(sound_name):
    """Placeholder function for playing sounds."""
    print(f"Playing sound: {sound_name}") # In a real game, this would use pygame.mixer

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((30, 20), pygame.SRCALPHA) # Size of the triangle
        pygame.draw.polygon(self.image, YELLOW, [(0, 0), (30, 10), (0, 20)]) # Triangle pointing right
        self.rect = self.image.get_rect()
        self.rect.centery = SCREEN_HEIGHT / 2
        self.rect.left = 50 # Player horizontal position is fixed
        self.velocity_y = 0
        self.gravity = 0.5
        self.flap_strength = -10 # Negative for upward movement

        # Combat related
        self.fire_cooldown = 300 # milliseconds (0.3 seconds)
        self.last_shot_time = 0

        self.last_hit_time = 0
        self.invincibility_duration = 1500 # 1.5 seconds in milliseconds
        self.is_invincible = False
        self.flash_timer = 0
        self.flash_interval = 100 # ms for flashing

        # Power-up states
        self.active_power_up_type = None
        self.power_up_end_time = 0
        self.original_fire_cooldown = self.fire_cooldown

    def update(self):
        # Power-up timer check
        if self.active_power_up_type and pygame.time.get_ticks() > self.power_up_end_time:
            self.deactivate_power_up()

        # Apply gravity
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Boundary checks (top/bottom)
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
            self.lose_life()
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0 # Stop further falling through floor
            self.lose_life()

        # Invincibility flashing
        if self.is_invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_hit_time > self.invincibility_duration:
                self.is_invincible = False
                self.image.set_alpha(255) # Make sure player is fully visible
            else:
                # Flashing logic
                self.flash_timer += self.game.clock.get_time()
                if self.flash_timer > self.flash_interval:
                    self.flash_timer = 0
                    if self.image.get_alpha() == 255:
                        self.image.set_alpha(128)
                    else:
                        self.image.set_alpha(255)
        else:
             self.image.set_alpha(255) # Ensure player is visible when not invincible


    def flap(self):
        self.velocity_y = self.flap_strength
        play_sound("player_flap.wav")

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.fire_cooldown:
            self.last_shot_time = current_time
            # Spawn bullet from the "nose" of the triangle
            bullet = Bullet(self.rect.right, self.rect.centery, self.game)
            self.game.all_sprites.add(bullet)
            self.game.player_bullets.add(bullet)
            play_sound("player_shoot.wav")

    def activate_rapid_fire(self):
        print("Rapid Fire Activated!")
        if self.active_power_up_type: # If another power up is active, deactivate it first
            self.deactivate_power_up()
        self.active_power_up_type = "rapid_fire"
        self.power_up_end_time = pygame.time.get_ticks() + 10000 # 10 seconds
        self.fire_cooldown = 100 # 0.1 seconds
        self.game.active_power_up_hud_info = ("Rapid Fire", self.power_up_end_time)


    def deactivate_power_up(self):
        print(f"Deactivating power up: {self.active_power_up_type}")
        if self.active_power_up_type == "rapid_fire":
            self.fire_cooldown = self.original_fire_cooldown
        # Add deactivation for other power-ups here
        self.active_power_up_type = None
        self.power_up_end_time = 0
        self.game.active_power_up_hud_info = None


    def lose_life(self):
        if not self.is_invincible: # Only lose life if not invincible
            self.game.lives -= 1
            play_sound("player_hit.wav")
            if self.game.lives <= 0:
                self.game.game_state = GAME_OVER
                play_sound("game_over.wav") # Added game over sound
            else:
                # Become invincible
                self.is_invincible = True
                self.last_hit_time = pygame.time.get_ticks()
                self.flash_timer = 0 # Reset flash timer
                # Reset position slightly to avoid instant re-collision if possible
                self.rect.centery = SCREEN_HEIGHT / 2
                self.velocity_y = 0

# --- Bullet Class ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((15, 5)) # Small white rectangle
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.centery = y
        self.speed = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH: # Remove bullet if it goes off screen
            self.kill()

# --- Enemy Base Class ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.health = 1 # Default health for basic enemies

    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            enemy_center = self.rect.center
            self.kill()
            self.game.score += 10 # Example score increment
            play_sound("enemy_hit.wav")

            # Power-up spawn chance (15% for now, only Rapid Fire)
            if random.random() < 0.15: # 15% chance
                # For now, only rapid fire. Later, choose randomly from available types.
                # power_up_type = random.choice(["rapid_fire", "spread_shot", "shield"])
                power_up_type = "rapid_fire"
                pu = PowerUp(self.game, enemy_center, power_up_type)
                self.game.all_sprites.add(pu)
                self.game.power_ups.add(pu)
                print(f"Spawned {power_up_type} power-up at {enemy_center}")


    def update(self):
        # Basic movement from right to left
        self.rect.x -= self.speed
        if self.rect.right < 0: # Remove if it goes off screen to the left
            self.kill()

# --- Drone Enemy ---
class Drone(Enemy):
    def __init__(self, game):
        super().__init__(game)
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED) # Red Square
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH # Spawn off-screen to the right
        self.rect.y = random.randint(50, SCREEN_HEIGHT - 50) # Random Y position
        self.speed = random.randint(2, 5)
        self.health = 1

# --- Star for Background ---
class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(1, 3)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH)
        self.rect.y = random.randrange(SCREEN_HEIGHT)
        self.speed = random.randint(1, 3) # Different stars scroll at different speeds

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
            self.rect.y = random.randrange(SCREEN_HEIGHT) # Re-appear at a new y

# --- Boss Base Class ---
class Boss(Enemy): # Bosses are a type of Enemy
    def __init__(self, game, health, score_value):
        super().__init__(game)
        self.total_health = health
        self.health = health
        self.score_value = score_value
        self.is_boss = True # Flag to identify boss
        self.boss_fight_active = False # Controlled by game logic

    def hit(self, damage):
        if not self.boss_fight_active: return # Don't take damage if not active (e.g. during entry)
        self.health -= damage
        play_sound("enemy_hit.wav") # Bosses can use a different sound too
        if self.health <= 0:
            self.health = 0 # Ensure health doesn't go negative for display
            self.kill()
            self.game.score += self.score_value
            self.game.end_boss_fight(won=True)

    def update(self):
        # Boss specific movement and attack logic will be in subclasses
        # Base update might not move it, or define entry animation
        pass

# --- Boss 1: The Warden ---
class TheWarden(Boss):
    def __init__(self, game):
        super().__init__(game, health=100, score_value=1000) # Example health and score
        self.image = pygame.Surface((80, 150), pygame.SRCALPHA) # Large grey rectangle
        self.image.fill(GREY)
        # Cannon part
        cannon_image = pygame.Surface((30, 20))
        cannon_image.fill(BLACK)
        self.image.blit(cannon_image, (50, 65)) # Position cannon on the main body

        self.rect = self.image.get_rect()
        self.rect.right = SCREEN_WIDTH - 20 # Appears on the right edge
        self.rect.centery = SCREEN_HEIGHT / 2

        self.entry_speed = 2
        self.target_x = SCREEN_WIDTH - 100 # Final X position after entry
        self.is_entering = True

        # Attack pattern state
        self.attack_phase = 0 # 0: burst, 1: charge energy ball
        self.last_attack_time = 0
        self.burst_pause = 2000 # 2s
        self.energy_ball_pause = 3000 # 3s
        self.charge_time = 1000 # 1s to charge energy ball
        self.is_charging = False
        self.charge_start_time = 0
        self.bullets_fired_in_burst = 0

    def update(self):
        if self.is_entering:
            self.rect.x -= self.entry_speed
            if self.rect.right <= self.target_x: # Or just self.rect.x if using topleft
                self.rect.right = self.target_x
                self.is_entering = False
                self.boss_fight_active = True # Now can be damaged and attack
                self.last_attack_time = pygame.time.get_ticks()
            return # Don't attack while entering

        if not self.boss_fight_active:
            return

        current_time = pygame.time.get_ticks()

        if self.is_charging:
            if current_time - self.charge_start_time > self.charge_time:
                self.fire_energy_ball()
                self.is_charging = False
                self.attack_phase = 0 # Back to burst next
                self.last_attack_time = current_time
            return

        if self.attack_phase == 0: # Burst fire phase
            # Check if it's time for the next action in the burst sequence OR to end the burst phase
            if current_time - self.last_attack_time > self.burst_pause: # Total pause after burst completes
                self.attack_phase = 1 # Switch to energy ball charging
                self.last_attack_time = current_time # Reset timer for energy ball pause
                self.bullets_fired_in_burst = 0 # Reset for next burst cycle
            elif self.bullets_fired_in_burst < 3 and \
                 current_time - self.last_attack_time > (self.burst_pause / 4) * (self.bullets_fired_in_burst +1) : # Distribute shots within the first 3/4 of burst_pause
                self.fire_burst_bullet()
                # self.last_attack_time is NOT reset here to keep the overall phase timing consistent.
                # Individual bullet firing is paced by bullets_fired_in_burst count.

        elif self.attack_phase == 1: # Energy ball charge and fire phase
            if current_time - self.last_attack_time > self.energy_ball_pause: # Pause before charging
                self.is_charging = True
                self.charge_start_time = current_time
                # Visual cue for charging can be added here
                print("Warden Charging Energy Ball!")
                self.last_attack_time = current_time # Mark that charging has started
                self.attack_phase = 2 # Move to a dedicated charging state to avoid re-triggering charge logic immediately

        elif self.attack_phase == 2: # Actively charging
            if self.is_charging and current_time - self.charge_start_time > self.charge_time:
                self.fire_energy_ball()
                self.is_charging = False
                self.attack_phase = 0 # Cycle back to burst fire
                self.last_attack_time = current_time # Reset timer for burst pause


    def fire_burst_bullet(self):
        # Fires a standard bullet from its cannon
        print(f"Warden firing burst bullet {self.bullets_fired_in_burst + 1}")
        self.bullets_fired_in_burst +=1
        bullet = EnemyBullet(self.rect.left, self.rect.centery - 15 + (self.bullets_fired_in_burst * 15) , self.game, speed_x=-7, size=(15,5), color=RED) # Slight spread
        self.game.all_sprites.add(bullet)
        self.game.enemy_bullets.add(bullet)
        play_sound("boss_shoot_burst.wav") # Placeholder

    def fire_energy_ball(self):
        # Fires a large, slow-moving energy ball
        energy_ball = EnemyBullet(self.rect.left, self.rect.centery, self.game, speed_x=-3, size=(40,40), color=ORANGE, is_energy_ball=True)
        self.game.all_sprites.add(energy_ball)
        self.game.enemy_bullets.add(energy_ball)
        play_sound("boss_shoot_energy.wav") # Placeholder
        print("Warden Fired Energy Ball!")


# --- Enemy Bullet Class (can be generic for all enemies/bosses) ---
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, game, speed_x=-5, speed_y=0, size=(10,10), color=RED, is_energy_ball=False):
        super().__init__()
        self.game = game
        self.image = pygame.Surface(size)
        self.image.fill(color)
        if is_energy_ball: # Make it a circle
            pygame.draw.circle(self.image, color, (size[0]//2, size[1]//2), size[0]//2)
            self.image.set_colorkey(BLACK) # If surface was filled black first
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or \
           self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

# --- PowerUp Base Class ---
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, game, center_pos, type_name):
        super().__init__()
        self.game = game
        self.type = type_name
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA) # Placeholder size
        self.rect = self.image.get_rect(center=center_pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 10000 # Power-ups disappear after 10 seconds if not collected
        self.speed_x = -1 # Slowly drift left

        if self.type == "rapid_fire":
            self.image.fill(BLUE) # Blue 'R'
            self.game.draw_text("R", self.game.font, WHITE, self.image, self.image.get_width()/2, self.image.get_height()/2, center=True)
        # Add other types later (spread_shot, shield, extra_life)

    def update(self):
        self.rect.x += self.speed_x
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime or self.rect.right < 0:
            self.kill() # Remove if lifetime expires or moves off-screen

    def apply_effect(self):
        play_sound("powerup_collect.wav")
        if self.type == "rapid_fire":
            self.game.player.activate_rapid_fire()
        # Add other effects later
        self.kill()


# --- Main Game Class ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Impact")
        self.clock = pygame.time.Clock()
        self.game_state = MAIN_MENU
        self.font = pygame.font.Font(None, 36) # Default font
        self.large_font = pygame.font.Font(None, 72)

        # Game variables to be reset
        self.score = 0
        self.current_level_index = 0 # Index for levels list
        self.player = None
        self.lives = 3 # Player lives added to Game class for easier management
        self.level_start_time = 0 # For level transition timing
        self.last_enemy_spawn_time = 0
        self.enemy_spawn_interval = 2000 # milliseconds (e.g., spawn enemy every 2 seconds)


        # Placeholder for entities
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.stars = pygame.sprite.Group() # For starfield background

        # Level specific variables
        self.level_duration = 60000 # Default to Level 1: 60 seconds
        self.level_enemy_phase_active = True # True if regular enemies should spawn
        self.current_boss = None
        self.boss_active = False # Flag to indicate a boss fight is ongoing
        self.level_complete_message_active = False # For "LEVEL COMPLETE" display
        self.level_complete_start_time = 0
        self.active_power_up_hud_info = None # Tuple: (name, end_time)


    def new_game(self):
        """Resets game variables for a new game."""
        self.score = 0
        self.current_level_index = 0 # Start at level 1 (index 0)
        self.lives = 3 # Reset lives

        self.all_sprites.empty()
        self.enemies.empty()
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.power_ups.empty()
        self.stars.empty()

        self.player = Player(self)
        self.all_sprites.add(self.player)

        # Initialize stars for background
        for _ in range(50): # Number of stars
            star = Star()
            self.all_sprites.add(star) # Add to all_sprites for update
            self.stars.add(star)      # Add to a specific group for drawing order if needed

        self.load_level(self.current_level_index)

    def load_level(self, level_idx):
        """Loads settings for the current level."""
        self.current_level_index = level_idx
        self.level_start_time = pygame.time.get_ticks() # For level transition AND duration timer
        self.game_state = LEVEL_TRANSITION
        self.level_enemy_phase_active = True # Start with enemy spawning active
        self.last_enemy_spawn_time = pygame.time.get_ticks() # Reset spawn timer

        if self.current_level_index == 0: # Level 1
            self.level_duration = 60000 # 60 seconds
            self.enemy_spawn_interval = 2000 # Spawn Drones every 2s
            # Potentially change enemy types or spawn rates here
        elif self.current_level_index == 1: # Level 2 (placeholder)
            self.level_duration = 75000 # 75 seconds
            # ...
        elif self.current_level_index == 2: # Level 3 (placeholder)
            self.level_duration = 90000 # 90 seconds
            # ...

        # Clear existing non-player, non-star sprites from previous level if any
        for sprite in self.all_sprites:
            if sprite != self.player and not isinstance(sprite, Star):
                sprite.kill()
        self.enemies.empty()
        self.player_bullets.empty() # Usually cleared, but good practice
        self.enemy_bullets.empty()
        self.power_ups.empty()

        if self.current_boss: # Clear current boss if any during level load / new game
            self.current_boss.kill()
        self.current_boss = None
        self.boss_active = False
        self.level_complete_message_active = False


    def start_boss_fight(self):
        play_sound("boss_intro_music.mp3") # Placeholder
        self.boss_active = True
        if self.current_level_index == 0: # Level 1 Boss
            self.current_boss = TheWarden(self)
        # elif self.current_level_index == 1: # Level 2 Boss
            # self.current_boss = TheSwarmMother(self)
        # elif self.current_level_index == 2: # Level 3 Boss
            # self.current_boss = TheJuggernaut(self)

        if self.current_boss:
            self.all_sprites.add(self.current_boss)
            # No need to add to self.enemies if we handle boss separately for collisions/drawing
        else: # Should not happen if levels are defined correctly
            print(f"Error: No boss defined for level index {self.current_level_index}")
            self.boss_active = False # Can't have a boss fight without a boss
            # Potentially auto-complete level or go to error state

    def end_boss_fight(self, won):
        if not self.boss_active: return # Avoid multiple calls

        if self.current_boss:
            self.current_boss.kill() # Ensure boss sprite is removed
            self.current_boss = None
        self.boss_active = False

        if won:
            print(f"Level {self.current_level_index + 1} Complete!")
            play_sound("level_complete.wav")
            self.level_complete_message_active = True
            self.level_complete_start_time = pygame.time.get_ticks()
            # The update loop will handle transitioning to the next level after message display
        else:
            # Boss defeated player (e.g. player ran out of lives during boss fight)
            # This case is typically handled by player.lose_life() leading to GAME_OVER
            # This function is primarily for when the BOSS is defeated.
            pass


    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_input(event)

            self.update()
            self.draw()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def handle_input(self, event):
        if self.game_state == MAIN_MENU:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.new_game() # This will set game_state to LEVEL_TRANSITION
        elif self.game_state == GAMEPLAY:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.player: # Ensure player exists
                        self.player.flap()
                elif event.key == pygame.K_x: # X key for shooting
                    if self.player:
                        self.player.shoot()
        elif self.game_state == GAME_OVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game_state = MAIN_MENU
        elif self.game_state == PAUSE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.game_state = GAMEPLAY # Resume game

        # Global input handling (e.g., for pausing)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            if self.game_state == GAMEPLAY:
                self.game_state = PAUSE
            elif self.game_state == PAUSE:
                 self.game_state = GAMEPLAY


    def update(self):
        if self.game_state == GAMEPLAY:
            self.all_sprites.update()

            current_time = pygame.time.get_ticks()
            level_elapsed_time = current_time - self.level_start_time

            # Check if enemy spawning phase is over and no boss currently active
            if self.level_enemy_phase_active and not self.boss_active and level_elapsed_time > self.level_duration:
                self.level_enemy_phase_active = False
                self.start_boss_fight()

            # Spawn Drones (or other enemies based on level)
            if self.level_enemy_phase_active and not self.boss_active:
                if current_time - self.last_enemy_spawn_time > self.enemy_spawn_interval:
                    self.last_enemy_spawn_time = current_time
                    if self.current_level_index == 0: # Level 1 only spawns Drones for now
                        drone = Drone(self)
                        self.all_sprites.add(drone)
                        self.enemies.add(drone) # Regular enemies go into self.enemies
                    # Add more enemy types for other levels later

            # Player Bullet -> Enemy/Boss Collision
            # Check collision with regular enemies
            enemy_hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, False, True)
            for enemy_hit, bullets in enemy_hits.items():
                enemy_hit.hit(1) # Assuming bullet damage is 1 to regular enemies

            # Check collision with Boss
            if self.current_boss and self.boss_active:
                boss_hits = pygame.sprite.spritecollide(self.current_boss, self.player_bullets, True) # True to kill bullets
                for _ in boss_hits: # Each hit bullet deals damage
                    self.current_boss.hit(1) # Assuming bullet damage is 1 to boss

            # Player -> Enemy/Boss/Enemy Bullet Collision
            if self.player:
                # Player -> Regular Enemy
                enemy_collisions = pygame.sprite.spritecollide(self.player, self.enemies, True)
                if enemy_collisions:
                    if not self.player.is_invincible:
                        self.player.lose_life()
                    for _ in enemy_collisions:
                         self.score += 5 # Score for crashing

                # Player -> Boss (physical collision)
                if self.current_boss and self.boss_active and pygame.sprite.collide_rect(self.player, self.current_boss):
                    if not self.player.is_invincible:
                        self.player.lose_life()

                # Player -> Enemy Bullet
                enemy_bullet_collisions = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True) # True to kill bullets
                if enemy_bullet_collisions:
                    if not self.player.is_invincible: # And not shielded by power-up later
                        self.player.lose_life()

                # Player -> PowerUp
                power_up_collisions = pygame.sprite.spritecollide(self.player, self.power_ups, False, pygame.sprite.collide_rect) # False: don't kill powerup yet
                for pu in power_up_collisions:
                    pu.apply_effect() # Effect application will kill the powerup sprite

            # Player Bullet <-> Enemy Bullet Collision
            pygame.sprite.groupcollide(self.player_bullets, self.enemy_bullets, True, True)


            # Level Complete Message Timer
            if self.level_complete_message_active:
                if current_time - self.level_complete_start_time > 3000: # Display for 3 seconds
                    self.level_complete_message_active = False
                    self.current_level_index += 1
                    if self.current_level_index < 3: # Assuming 3 levels total
                        self.load_level(self.current_level_index)
                    else:
                        # TODO: Game complete state or loop back? For now, game over.
                        print("All levels complete! (Placeholder for game end screen)")
                        self.game_state = GAME_OVER # Or a new "YOU WIN" state

        elif self.game_state == LEVEL_TRANSITION:
            if pygame.time.get_ticks() - self.level_start_time > 3000: # 3 seconds for "LEVEL X"
                self.game_state = GAMEPLAY
                self.level_start_time = pygame.time.get_ticks() # Reset level timer for actual gameplay duration
                self.last_enemy_spawn_time = pygame.time.get_ticks()
                self.boss_active = False # Ensure boss is not active at start of level gameplay
                self.level_enemy_phase_active = True # Ensure enemies spawn


    def draw_text(self, text, font, color, surface, x, y, center=False):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def draw(self):
        self.screen.fill(BLACK) # Default background for space

        # Draw stars first (they are in all_sprites, but drawing them separately ensures they are behind everything else if needed)
        # However, since all_sprites.draw() respects order of addition, and stars are added first, this is okay.
        # If specific layering is needed later, self.stars.draw(self.screen) can be used before other groups.

        if self.game_state == MAIN_MENU:
            self.stars.draw(self.screen) # Show stars in menu too
            self.draw_text("Flappy Impact", self.large_font, YELLOW, self.screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3, center=True)
            self.draw_text("Press Enter to Start", self.font, WHITE, self.screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, center=True)
        elif self.game_state == LEVEL_TRANSITION:
            self.stars.draw(self.screen)
            self.draw_text(f"LEVEL {self.current_level_index + 1}", self.large_font, WHITE, self.screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, center=True)
        elif self.game_state == GAMEPLAY:
            # self.all_sprites.draw(self.screen) # This would draw stars too.
            # To ensure player and enemies are on top of stars, draw them in order:
            self.stars.draw(self.screen)
            self.enemies.draw(self.screen)
            self.player_bullets.draw(self.screen)
            self.enemy_bullets.draw(self.screen) # Though not used yet
            self.power_ups.draw(self.screen)     # Though not used yet
            if self.player:
                 self.screen.blit(self.player.image, self.player.rect) # Draw player last to be on top

            # Draw HUD
            self.draw_text(f"SCORE: {self.score:06d}", self.font, WHITE, self.screen, 10, 10)
            self.draw_text(f"LIVES: {'♥' * self.lives}", self.font, RED, self.screen, SCREEN_WIDTH - 100, 10) # Simple heart representation
            self.draw_text(f"LEVEL: {self.current_level_index + 1}", self.font, WHITE, self.screen, 10, SCREEN_HEIGHT - 40)

            # Power-up HUD
            if self.active_power_up_hud_info:
                name, end_time = self.active_power_up_hud_info
                remaining_time = (end_time - pygame.time.get_ticks()) / 1000
                if remaining_time > 0:
                    self.draw_text(f"POWER-UP: {name} {remaining_time:.1f}s", self.font, YELLOW, self.screen, SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT - 40)
                else: # Fallback if timer is somehow negative but not yet cleared
                    self.draw_text(f"POWER-UP: {name} 0.0s", self.font, YELLOW, self.screen, SCREEN_WIDTH / 2 -150, SCREEN_HEIGHT - 40)


            # Boss Health Bar
            if self.boss_active and self.current_boss:
                health_percentage = self.current_boss.health / self.current_boss.total_health
                bar_width = SCREEN_WIDTH / 2
                bar_height = 20
                fill_width = bar_width * health_percentage
                health_bar_rect = pygame.Rect((SCREEN_WIDTH - bar_width) / 2, 10, bar_width, bar_height)
                fill_rect = pygame.Rect((SCREEN_WIDTH - bar_width) / 2, 10, fill_width, bar_height)
                pygame.draw.rect(self.screen, RED, health_bar_rect)
                pygame.draw.rect(self.screen, GREEN, fill_rect)
                self.draw_text("BOSS", self.font, WHITE, self.screen, health_bar_rect.centerx, health_bar_rect.centery + 20, center=True)

            if self.level_complete_message_active:
                self.draw_text("LEVEL COMPLETE!", self.large_font, GREEN, self.screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, center=True)
                self.draw_text(f"Score: {self.score}", self.font, WHITE, self.screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, center=True)


        elif self.game_state == PAUSE:
            # Draw current game state (stars, enemies, player, bullets)
            self.stars.draw(self.screen)
            self.enemies.draw(self.screen)
            if self.current_boss: self.screen.blit(self.current_boss.image, self.current_boss.rect)
            self.player_bullets.draw(self.screen)
            self.enemy_bullets.draw(self.screen)
            self.power_ups.draw(self.screen)
            if self.player: self.screen.blit(self.player.image, self.player.rect)

            # Also draw HUD in pause
            self.draw_text(f"SCORE: {self.score:06d}", self.font, WHITE, self.screen, 10, 10)
            self.draw_text(f"LIVES: {'♥' * self.lives}", self.font, RED, self.screen, SCREEN_WIDTH - 100, 10)
            self.draw_text(f"LEVEL: {self.current_level_index + 1}", self.font, WHITE, self.screen, 10, SCREEN_HEIGHT - 40)
            self.draw_text("PAUSED", self.large_font, WHITE, self.screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, center=True)
            self.draw_text("Press P to Resume", self.font, WHITE, self.screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, center=True)

        elif self.game_state == GAME_OVER:
            self.draw_text("GAME OVER", self.large_font, RED, self.screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3, center=True)
            self.draw_text(f"Final Score: {self.score}", self.font, WHITE, self.screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, center=True)
            self.draw_text("Press Enter to Restart", self.font, WHITE, self.screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, center=True)

# --- Main Execution ---
if __name__ == "__main__":
    game = Game()
    game.run()
