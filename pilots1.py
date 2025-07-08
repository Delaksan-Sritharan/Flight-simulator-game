import pygame
import random
import sys
from pygame import mixer


# Pygame setup
pygame.init()
pygame.mixer.init()
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Endless Flight Game")
clock = pygame.time.Clock()

# Defined audios
try:
    plane_fx = pygame.mixer.Sound('audio/commercial-aircraft-in-flight-sounds-17309.wav')
    plane_fx.set_volume(0.5)
    enemy_fx = pygame.mixer.Sound('audio/jetSound.wav')
    enemy_fx.set_volume(0.3)
    level_up_fx = pygame.mixer.Sound('audio/Levelup-sound.wav')
    level_up_fx.set_volume(0.7)
except:
    # Create dummy sound objects if files aren't found
    plane_fx = pygame.mixer.Sound(buffer=bytearray(100))
    enemy_fx = pygame.mixer.Sound(buffer=bytearray(100))
    level_up_fx = pygame.mixer.Sound(buffer=bytearray(100))

# Define camera offset
camera_offset_x = 0


class BackgroundManager:
    def __init__(self):
        # Load background images for each season and location combination
        self.background_images = {}
        self.current_season = "sunny"
        self.current_location = "farmland"

        # Colors representing different seasons
        self.season_colors = {
            "sunny": (135, 206, 235),  # Light blue
            "rainy": (169, 169, 169),  # Gray
            "night": (25, 25, 112)  # Dark blue
        }

        self.border_weight = 20
        self.border_transparent = 50
        self.border_color = (255, 255, 255)


        # Create placeholder surfaces for each combination
        for season in ["sunny", "rainy", "night"]:
            for location in ["farmland", "city", "hill_country", "seaside"]:
                # In a real game, you would load actual images here
                # For this example, we'll create colored surfaces with text
                bg_surface = pygame.Surface((screen_width, screen_height))
                bg_surface.fill(self.season_colors[season])

                # Add text to identify the background
                font = pygame.font.SysFont(None, 48)
                text = font.render(f"{season.capitalize()} - {location.replace('_', ' ').title()}", True,
                                   (255, 255, 255))
                text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
                bg_surface.blit(text, text_rect)

                # Add location-specific elements
                if location == "farmland":
                    # Draw simple farmland elements
                    pygame.draw.rect(bg_surface, (34, 139, 34),
                                     (0, screen_height - 200, screen_width, 200))  # Green fields
                    pygame.draw.rect(bg_surface, (139, 69, 19), (300, screen_height - 220, 100, 20))  # Brown barn
                elif location == "city":
                    # Draw simple city skyline
                    for i in range(5):
                        x = 200 + i * 200
                        height = random.randint(100, 300)
                        pygame.draw.rect(bg_surface, (105, 105, 105),
                                         (x, screen_height - height, 80, height))  # Buildings
                elif location == "hill_country":
                    # Draw hills
                    pygame.draw.arc(bg_surface, (0, 100, 0),
                                    (0, screen_height - 300, 600, 600),
                                    0, 3.14, width=0)  # Green hill
                elif location == "seaside":
                    # Draw sea and beach
                    pygame.draw.rect(bg_surface, (0, 105, 148), (0, screen_height - 150, screen_width, 150))  # Sea
                    pygame.draw.rect(bg_surface, (238, 214, 175), (0, screen_height - 170, screen_width, 20))  # Sand

                self.background_images[(season, location)] = bg_surface

        # Current background
        self.current_bg = self.background_images[(self.current_season, self.current_location)]

        # Level to season/location mapping
        self.level_mapping = {
            1: ("sunny", "farmland"),
            2: ("sunny", "city"),
            3: ("rainy", "city"),
            4: ("rainy", "hill_country"),
            5: ("night", "hill_country"),
            6: ("night", "seaside")
        }

        # Weather effects
        self.rain_particles = []
        self.star_particles = []
        self.last_weather_update = 0
        self.weather_cooldown = 50  # ms

    def set_background_for_level(self, level):
        if level in self.level_mapping:
            season, location = self.level_mapping[level]
            self.current_season = season
            self.current_location = location
            self.current_bg = self.background_images[(season, location)]

            # Reset weather effects
            self.rain_particles = []
            self.star_particles = []

            # Initialize weather effects
            if season == "rainy":
                self._init_rain()
            elif season == "night":
                self._init_stars()

    def draw_transparent_border(self, surface):
        """Draws a transparent border around the game area"""
        border_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

        # Draw outer rectangle (semi-transparent)
        pygame.draw.rect(border_surface, (*self.border_color, self.border_transparent),
                         (0, 0, screen_width, screen_height))

        # Draw inner rectangle (fully transparent)
        pygame.draw.rect(border_surface, (0, 0, 0, 0),
                         (self.border_weight, self.border_weight,
                          screen_width - 2 * self.border_weight,
                          screen_height - 2 * self.border_weight))

        surface.blit(border_surface, (0, 0))

    def _init_rain(self):
        # Create rain particles
        for _ in range(200):
            x = random.randint(0, screen_width)
            y = random.randint(-screen_height, 0)
            speed = random.uniform(5, 15)
            self.rain_particles.append([x, y, speed])

    def _init_stars(self):
        # Create stars
        for _ in range(100):
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height // 2)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            self.star_particles.append([x, y, size, brightness])

    def update_weather(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_weather_update > self.weather_cooldown:
            self.last_weather_update = current_time

            if self.current_season == "rainy":
                # Update rain particles
                for i, particle in enumerate(self.rain_particles):
                    particle[1] += particle[2]  # Move down
                    if particle[1] > screen_height:
                        # Reset particle at top
                        self.rain_particles[i][0] = random.randint(0, screen_width)
                        self.rain_particles[i][1] = random.randint(-100, 0)

            elif self.current_season == "night":
                # Make stars twinkle
                for i, star in enumerate(self.star_particles):
                    # Randomly adjust brightness
                    self.star_particles[i][3] += random.randint(-20, 20)
                    self.star_particles[i][3] = max(100, min(255, self.star_particles[i][3]))

    def draw(self, camera_offset):
        # Draw repeating background for endless effect
        bg_width = self.current_bg.get_width()
        num_tiles = int(screen_width / bg_width) + 2
        for i in range(num_tiles):
            screen.blit(self.current_bg, (i * bg_width - camera_offset % bg_width, 0))

        # Draw weather effects
        if self.current_season == "rainy":
            self._draw_rain(camera_offset)
        elif self.current_season == "night":
            self._draw_stars(camera_offset)

        # Add the transparent border drawing
        self.draw_transparent_border(screen)

    def _draw_rain(self, camera_offset):
        for x, y, speed in self.rain_particles:
            # Adjust for camera offset
            display_x = (x - camera_offset) % screen_width
            pygame.draw.line(screen, (200, 200, 255),
                             (display_x, y),
                             (display_x - speed * 0.5, y + speed * 0.5), 1)

    def _draw_stars(self, camera_offset):
        for x, y, size, brightness in self.star_particles:
            # Adjust for camera offset
            display_x = (x - camera_offset) % screen_width
            color = (brightness, brightness, brightness)
            pygame.draw.circle(screen, color, (display_x, y), size)


class Flight(pygame.sprite.Sprite):
    level_enemy = {1: {"count": 5, "spacing": 500},
                   2: {"count": 10, "spacing": 400},
                   3: {"count": 15, "spacing": 300},
                   4: {"count": 20, "spacing": 250},
                   5: {"count": 25, "spacing": 200},
                   6: {"count": 30, "spacing": 150}}
    current_level_enemy_spawn = 0
    next_enemy_spawn_x = 0
    level_started = False
    border_size = 20

    def __init__(self, x, y, scale, velocity_vertical, velocity_horizontal, is_enemy=False):
        super().__init__()
        try:
            if is_enemy:
                img = pygame.image.load("images/enemy.png")
            else:
                img = pygame.image.load("images/TempFlightFigure.png")
            self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        except pygame.error:
            # Create placeholder if image not found
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 0, 0) if is_enemy else (0, 0, 255))

        if not is_enemy:
            self.max_health = 100
            self.current_health = self.max_health
            self.last_hit_time = 0
            self.distance_traveled = 0  # Track how far player has flown

        self.target_y = y
        self.move_smoothness = 0.1
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.altitude = velocity_vertical
        self.speed = velocity_horizontal
        self.is_enemy = is_enemy
        self.direction = random.choice([-1, 1]) if is_enemy else 1
        self.world_x = x
        self.world_y = y
        self.mask = pygame.mask.from_surface(self.image)
        self.collision_radius = min(self.rect.width, self.rect.height) // 2
        self.collision_center = (self.world_x, self.rect.centery)
        self.vertical_movement_timer = 0
        self.change_direction_delay = random.randint(60, 180)
        self.has_been_passed = False

    def draw(self, camera_offset_x=0):
        display_x = self.world_x - camera_offset_x
        screen.blit(self.image, (display_x, self.rect.y))

    def flight_movement(self, moves_up, moves_down, speed_up, speed_down):
        travel_distance_x = 0
        travel_distance_y = 0

        if moves_up:
            travel_distance_y = -self.altitude
        if moves_down:
            travel_distance_y = self.altitude
        if speed_up:
            travel_distance_x = self.speed
        if speed_down:
            travel_distance_x = -self.speed * 0.5  # Slower when moving left

        self.world_x += travel_distance_x
        self.world_y += travel_distance_y
        self.rect.y += travel_distance_y

        if not self.is_enemy:
            self.distance_traveled += travel_distance_x  # Track distance traveled

        # World boundaries (only vertical, horizontal is endless)
        if self.rect.top < self.border_size:
            self.rect.top = self.border_size
            self.world_y = self.rect.centery
        if self.rect.bottom > screen_height - self.border_size:
            self.rect.bottom = screen_height - self.border_size
            self.world_y = self.rect.centery

    def enemy_movement(self, player, level):
        if not self.is_enemy:
            return

        # Check if player has passed this enemy
        if not self.has_been_passed and player.world_x > self.world_x:
            self.has_been_passed = True

        # Vertical movement with level-based difficulty
        self.vertical_movement_timer += 1

        if self.vertical_movement_timer >= self.change_direction_delay:
            self.direction *= -1
            self.vertical_movement_timer = 0
            self.change_direction_delay = random.randint(max(30, 120 - level * 20), max(60, 180 - level * 30))

        # Faster vertical movement in higher levels
        vertical_speed = self.altitude * 0.5 * (1 + (level - 1) * 0.3)
        self.rect.y += self.direction * vertical_speed
        self.world_y = self.rect.y

        if self.rect.top < self.border_size:
            self.rect.top = self.border_size
            self.direction = 1
            self.vertical_movement_timer = 0
        if self.rect.bottom > screen_height - self.border_size:
            self.rect.bottom = screen_height - self.border_size
            self.direction = -1
            self.vertical_movement_timer = 0

    def update_collision_data(self):
        self.collision_center = (self.world_x, self.rect.centery)

    def draw_health_bar(self, surface, x, y, current_health, max_health):
        bar_width = 200
        bar_height = 20
        fill = (current_health / max_health) * bar_width
        outline_rect = pygame.Rect(x, y, bar_width, bar_height)
        fill_rect = pygame.Rect(x, y, fill, bar_height)
        pygame.draw.rect(surface, (255, 0, 0), fill_rect)
        pygame.draw.rect(surface, (255, 255, 255), outline_rect, 2)

    def play_sound(self, is_enemy):
        if not is_enemy:
            plane_fx.play()
        else:
            enemy_fx.play()

    @classmethod
    def level_begins(cls, level, player_x):
        if level in cls.level_enemy:
            cls.current_level_enemy_spawn = 0
            cls.next_enemy_spawn_x = player_x + cls.level_enemy[level]["spacing"]
            cls.level_started = True


class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.max_level = 6
        self.level_thresholds = {
            1: 0,
            2: 1000,
            3: 2000,
            4: 3000,
            5: 4000,
            6: 5000
        }
        self.level_completed = False
        self.level_transition_time = 0
        self.show_transition = False
        self.transition_duration = 3000  # 3 seconds

    def update(self, player_distance):
        # Determine the current level based on distance traveled
        for level in range(self.max_level, 0, -1):
            if player_distance >= self.level_thresholds[level]:
                if self.current_level < level:
                    # Level up!
                    self.current_level = level
                    self.show_transition = True
                    self.level_transition_time = pygame.time.get_ticks()
                    level_up_fx.play()
                break

        # Check if we're showing the transition and if it's time to hide it
        if self.show_transition:
            if pygame.time.get_ticks() - self.level_transition_time > self.transition_duration:
                self.show_transition = False

        # Check if we've completed the game
        if player_distance >= self.level_thresholds[self.max_level] + 1000:
            self.level_completed = True

        return self.current_level

    def draw_level_info(self, surface):
        font = pygame.font.SysFont(None, 36)
        level_text = font.render(f"Level: {self.current_level}", True, (255, 255, 255))
        surface.blit(level_text, (screen_width - 150, 10))

        if self.show_transition:
            # Create a semi-transparent overlay
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            surface.blit(overlay, (0, 0))

            # Display the level transition text
            big_font = pygame.font.SysFont(None, 72)
            level_announce = big_font.render(f"LEVEL {self.current_level}", True, (255, 255, 255))

            # Center the text
            text_rect = level_announce.get_rect(center=(screen_width / 2, screen_height / 2))
            surface.blit(level_announce, text_rect)

            # Add level description
            desc_font = pygame.font.SysFont(None, 36)
            descriptions = {
                1: "Clear skies over farmland!",
                2: "Approaching the city!",
                3: "Rainy cityscape ahead!",
                4: "Hills in the rain!",
                5: "Night flight over hills!",
                6: "Seaside at night!"
            }
            desc_text = desc_font.render(descriptions.get(self.current_level, ""), True, (255, 255, 255))
            desc_rect = desc_text.get_rect(center=(screen_width / 2, screen_height / 2 + 60))
            surface.blit(desc_text, desc_rect)

            # Add a "Continue" instruction during level transition
            continue_font = pygame.font.SysFont(None, 28)
            continue_text = continue_font.render("Keep flying! Game continues automatically", True, (255, 255, 255))
            continue_rect = continue_text.get_rect(center=(screen_width / 2, screen_height / 2 + 120))
            surface.blit(continue_text, continue_rect)


def spawn_enemy(enemies, player_x, spawn_distance, level):
    """Spawn new enemies ahead of the player in endless world with level-based difficulty"""
    x_pos = player_x + spawn_distance + random.randint(100, 300)
    y_pos = random.randint(Flight.border_size + 50, screen_height - Flight.border_size - 50)
    # Adjust enemy attributes based on level
    scale = 0.3 * (1 + (level - 1) * 0.1)  # Bigger enemies in higher levels
    vertical_speed = 2 + (level - 1)  # Faster vertical movement in higher levels

    new_enemy = Flight(x_pos, y_pos, scale, vertical_speed, 0, is_enemy=True)
    new_enemy.play_sound(is_enemy=True)
    enemies.append(new_enemy)


def check_collisions(player, enemies):
    current_time = pygame.time.get_ticks()
    damaged = False

    player.update_collision_data()

    for enemy in enemies[:]:
        enemy.update_collision_data()

        dx = enemy.collision_center[0] - player.collision_center[0]
        dy = enemy.collision_center[1] - player.collision_center[1]
        distance_squared = dx * dx + dy * dy

        min_distance = player.collision_radius + enemy.collision_radius
        if distance_squared < min_distance * min_distance:
            offset_x = int(enemy.world_x - player.world_x)
            offset_y = int(enemy.rect.y - player.rect.y)

            if player.mask.overlap(enemy.mask, (offset_x, offset_y)):
                if current_time - player.last_hit_time > 1000:
                    player.current_health -= 10
                    player.last_hit_time = current_time
                    enemies.remove(enemy)
                    damaged = True

    return damaged


# Game initialization
player_flight = Flight(screen_width // 4, screen_height // 2, 0.3, 5, 5, is_enemy=False)
enemy_flights = []
bg_manager = BackgroundManager()
level_manager = LevelManager()
game_over = False
game_completed = False
score = 0
font = pygame.font.SysFont(None, 36)
spawn_timer = 0
spawn_cooldown = 120  # 2 seconds at 60 FPS

# Initial enemy spawn
spawn_enemy(enemy_flights, player_flight.world_x, 800, level_manager.current_level)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                # Reset game
                player_flight = Flight(screen_width // 4, screen_height // 2, 0.3, 5, 5, is_enemy=False)
                enemy_flights = []
                game_over = False
                game_completed = False
                score = 0
                level_manager = LevelManager()
                bg_manager = BackgroundManager()
                spawn_enemy(enemy_flights, player_flight.world_x, 800, level_manager.current_level)

            if game_completed and event.key == pygame.K_r:
                # Reset game after completion
                player_flight = Flight(screen_width // 4, screen_height // 2, 0.3, 5, 5, is_enemy=False)
                enemy_flights = []
                game_over = False
                game_completed = False
                score = 0
                level_manager = LevelManager()
                bg_manager = BackgroundManager()
                spawn_enemy(enemy_flights, player_flight.world_x, 800, level_manager.current_level)

    # Get keyboard input regardless of transition state
    keys = pygame.key.get_pressed()
    moves_up = keys[pygame.K_UP]
    moves_down = keys[pygame.K_DOWN]
    speed_up = keys[pygame.K_RIGHT]
    speed_down = keys[pygame.K_LEFT]

    if not game_over and not game_completed:
        # Always play sound and allow movement, even during level transition
        player_flight.play_sound(is_enemy=False)
        player_flight.flight_movement(moves_up, moves_down, speed_up, speed_down)

        # Update camera (follow player horizontally)
        target_x = player_flight.world_x - screen_width // 4
        camera_offset_x = target_x

    # Update weather effects
    bg_manager.update_weather()

    # Update level and background
    current_level = level_manager.update(player_flight.distance_traveled)
    bg_manager.set_background_for_level(current_level)

    # Only spawn enemies and handle enemy-related logic when not in transition
    if not level_manager.show_transition and not game_over and not game_completed:
        # Enemy spawning with level-based timing
        spawn_timer += 1
        spawn_cooldown_for_level = max(30, 120 - current_level * 30)  # Spawn faster in higher levels

        if spawn_timer >= spawn_cooldown_for_level:
            spawn_enemy(enemy_flights, player_flight.world_x, 800, current_level)
            spawn_timer = 0

        # Remove enemies that are too far behind (do this even during transition)
        for enemy in enemy_flights[:]:
            if player_flight.world_x - enemy.world_x > screen_width:
                enemy_flights.remove(enemy)

        # Always update player collision data
        player_flight.update_collision_data()

        # Only handle enemy movement and collisions when not in transition
        if not level_manager.show_transition:
            for enemy in enemy_flights:
                enemy.enemy_movement(player_flight, current_level)
                enemy.update_collision_data()

            # Check collisions - damage increases with level
            if check_collisions(player_flight, enemy_flights):
                if player_flight.current_health <= 0:
                    game_over = True
                else:
                    current_time = pygame.time.get_ticks()
                    if current_time - player_flight.last_hit_time < 200:
                        flash_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                        flash_surface.fill((255, 0, 0, 50))
                        screen.blit(flash_surface, (0, 0))

        # Update score based on distance traveled
        score = int(player_flight.distance_traveled / 10)

        # Check if game is completed (passed all levels)
        if score >= 6000:
            game_completed = True

    # Drawing
    bg_manager.draw(camera_offset_x)

    for enemy in enemy_flights:
        enemy.draw(camera_offset_x)

    player_flight.draw(camera_offset_x)

    # UI Elements
    player_flight.draw_health_bar(screen, 10, 50, player_flight.current_health, player_flight.max_health)
    health_text = font.render(f"{player_flight.current_health}/{player_flight.max_health}", True, (255, 255, 255))
    screen.blit(health_text, (220, 50))

    score_text = font.render(f"Distance: {score}km", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Draw level information with season and location
    level_info = font.render(
        f"Level: {current_level} | {bg_manager.current_season.capitalize()} | {bg_manager.current_location.replace('_', ' ').title()}",
        True, (255, 255, 255))
    screen.blit(level_info, (screen_width - 450, 10))

    level_manager.draw_level_info(screen)

    if game_over:
        # Create a semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        game_over_text = font.render("GAME OVER! Press R to restart", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(game_over_text, text_rect)

    if game_completed:
        # Create a semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        complete_font = pygame.font.SysFont(None, 72)
        complete_text = complete_font.render("CONGRATULATIONS!", True, (0, 255, 0))
        text_rect = complete_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
        screen.blit(complete_text, text_rect)

        stats_text = font.render(f"You completed all {level_manager.max_level} levels with a distance of {score}km!",
                                 True, (255, 255, 255))
        stats_rect = stats_text.get_rect(center=(screen_width // 2, screen_height // 2 + 20))
        screen.blit(stats_text, stats_rect)

        restart_text = font.render("Press R to play again", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 70))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()