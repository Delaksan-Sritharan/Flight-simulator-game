import pygame
import random
import sys
from pygame import mixer

# Pygame setup
pygame.init()
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Endless Flight Game")
clock = pygame.time.Clock()

# Defined audios
plane_fx = pygame.mixer.Sound('audio/commercial-aircraft-in-flight-sounds-17309.wav')
plane_fx.set_volume(0.5)
enemy_fx = pygame.mixer.Sound('audio/jetSound.wav')
enemy_fx.set_volume(0.3)
level_up_fx = pygame.mixer.Sound('audio/Levelup-sound.wav')
level_up_fx.set_volume(0.7)

# Define camera offset
camera_offset_x = 0


class BackgroundManager:
    def __init__(self):
        # Base backgrounds for seasons
        self.seasons = {
            "sunny": (135, 206, 235),  # Light blue sky
            "rainy": (105, 105, 105),  # Dark gray sky
            "night": (25, 25, 112)  # Dark blue sky
        }

        # Base colors for places
        self.places = {
            "farmland": (76, 187, 23),  # Green
            "city": (169, 169, 169),  # Gray
            "hill_country": (139, 115, 85),  # Brown
            "seaside": (0, 105, 148)  # Deep blue
        }

        # All possible environment combinations
        self.all_environments = [
            {"season": "sunny", "place": "farmland"},
            {"season": "sunny", "place": "city"},
            {"season": "sunny", "place": "hill_country"},
            {"season": "sunny", "place": "seaside"},
            {"season": "rainy", "place": "farmland"},
            {"season": "rainy", "place": "city"},
            {"season": "rainy", "place": "hill_country"},
            {"season": "rainy", "place": "seaside"},
            {"season": "night", "place": "farmland"},
            {"season": "night", "place": "city"},
            {"season": "night", "place": "hill_country"},
            {"season": "night", "place": "seaside"}
        ]

        # Load images for different elements - in a full implementation, you'd use actual images
        # For now, we'll create colored surfaces
        self.cloud_img = pygame.Surface((100, 60))
        self.cloud_img.fill((255, 255, 255))
        self.rain_img = pygame.Surface((2, 20))
        self.rain_img.fill((200, 200, 255))
        self.star_img = pygame.Surface((3, 3))
        self.star_img.fill((255, 255, 255))

        # Specific location elements
        self.farm_elements = []  # Would contain farm buildings, trees, etc.
        self.city_elements = []  # Would contain buildings, roads, etc.
        self.hill_elements = []  # Would contain mountains, hills, etc.
        self.sea_elements = []  # Would contain waves, boats, etc.

        # Pick a random starting environment
        self.randomize_environment()

        # Generate stars for night sky
        self.stars = []
        for _ in range(100):
            self.stars.append((random.randint(0, screen_width),
                               random.randint(0, screen_height // 2)))

        # Generate clouds
        self.clouds = []
        for _ in range(10):
            self.clouds.append((random.randint(0, screen_width * 2),
                                random.randint(50, screen_height // 3)))

        # Generate raindrops for rainy season
        self.raindrops = []
        for _ in range(200):
            self.raindrops.append([random.randint(0, screen_width),
                                   random.randint(0, screen_height)])

        # For scrolling effect
        self.scroll_offset = 0

        # For smooth background transitions
        self.transition_timer = 0
        self.transition_duration = 60  # frames (1 second at 60 FPS)
        self.is_transitioning = False
        self.old_season = self.current_season
        self.old_place = self.current_place
        self.transition_progress = 0

    def randomize_environment(self):
        """Pick a random environment from all possible combinations"""
        env = random.choice(self.all_environments)
        self.current_season = env["season"]
        self.current_place = env["place"]

    def get_level_environment(self, level):
        """Return the environment settings for a specific level"""
        # We'll create a sequence of predetermined environments for levels
        level_environments = [
            {"season": "sunny", "place": "farmland"},  # Level 1
            {"season": "rainy", "place": "city"},  # Level 2
            {"season": "night", "place": "hill_country"},  # Level 3
            {"season": "sunny", "place": "seaside"},  # Level 4
            {"season": "night", "place": "city"},  # Level 5
            {"season": "rainy", "place": "seaside"}  # Level 6
        ]

        # Get the environment for the specified level (1-indexed)
        if 1 <= level <= len(level_environments):
            return level_environments[level - 1]
        else:
            # For levels beyond our predefined set, return a random environment
            return random.choice(self.all_environments)

    def set_background_for_level(self, level, force=False):
        """Change the background for the current level with smooth transition"""
        new_env = self.get_level_environment(level)
        new_season = new_env["season"]
        new_place = new_env["place"]

        # Only start a transition if the environment is actually changing
        if (new_season != self.current_season or new_place != self.current_place) or force:
            self.old_season = self.current_season
            self.old_place = self.current_place
            self.current_season = new_season
            self.current_place = new_place
            self.is_transitioning = True
            self.transition_timer = 0
            self.transition_progress = 0

    def update_transition(self):
        """Update the background transition animation"""
        if self.is_transitioning:
            self.transition_timer += 1
            self.transition_progress = min(1.0, self.transition_timer / self.transition_duration)

            if self.transition_timer >= self.transition_duration:
                self.is_transitioning = False

    def draw(self, camera_offset):
        # Update transition if active
        self.update_transition()

        # Update scroll offset for parallax effect
        self.scroll_offset = camera_offset // 2

        # Handle drawing with potential transition
        if self.is_transitioning:
            # Draw the old background with fading opacity
            self.draw_environment(self.old_season, self.old_place, camera_offset, 1.0 - self.transition_progress)
            # Draw the new background with increasing opacity
            self.draw_environment(self.current_season, self.current_place, camera_offset, self.transition_progress)
        else:
            # Draw the current background at full opacity
            self.draw_environment(self.current_season, self.current_place, camera_offset, 1.0)

    def draw_environment(self, season, place, camera_offset, opacity=1.0):
        """Draw the environment with specified season and place at given opacity"""
        # Create a surface for this layer
        layer = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

        # Fill with season color (sky)
        sky_color = self.seasons[season]
        sky_color_with_alpha = (sky_color[0], sky_color[1], sky_color[2], int(255 * opacity))
        layer.fill(sky_color_with_alpha)

        # Draw stars if it's night
        if season == "night":
            for star_x, star_y in self.stars:
                # Apply parallax effect
                display_x = (star_x - self.scroll_offset * 0.2) % screen_width
                star_surface = pygame.Surface((3, 3), pygame.SRCALPHA)
                star_surface.fill((255, 255, 255, int(255 * opacity)))
                layer.blit(star_surface, (display_x, star_y))

        # Draw clouds for sunny and rainy
        if season != "night":
            for cloud_x, cloud_y in self.clouds:
                # Apply parallax effect
                display_x = (cloud_x - self.scroll_offset * 0.5) % (screen_width * 2)
                if display_x < screen_width:
                    cloud_surface = pygame.Surface((100, 60), pygame.SRCALPHA)
                    cloud_surface.fill((255, 255, 255, int(200 * opacity)))
                    layer.blit(cloud_surface, (display_x, cloud_y))

        # Draw rain if it's rainy
        if season == "rainy":
            for rain_x, rain_y in self.raindrops:
                # Draw raindrop
                rain_surface = pygame.Surface((2, 20), pygame.SRCALPHA)
                rain_surface.fill((200, 200, 255, int(200 * opacity)))
                layer.blit(rain_surface, (rain_x, rain_y))

        # Draw ground (place-dependent)
        ground_height = screen_height // 3
        ground_color = self.places[place]
        ground_color_with_alpha = (ground_color[0], ground_color[1], ground_color[2], int(255 * opacity))

        ground_surface = pygame.Surface((screen_width, ground_height), pygame.SRCALPHA)
        ground_surface.fill(ground_color_with_alpha)
        layer.blit(ground_surface, (0, screen_height - ground_height))

        # Draw place-specific elements
        self.draw_place_elements(layer, place, camera_offset, opacity)

        # Blit the entire layer to the screen
        screen.blit(layer, (0, 0))

        # Update rain positions if it's rainy (we do this outside the surface blitting)
        if season == "rainy" and opacity > 0.5:  # Only update positions for the dominant background
            for i, (rain_x, rain_y) in enumerate(self.raindrops):
                # Update raindrop position
                rain_y += random.randint(5, 15)
                if rain_y > screen_height:
                    rain_y = 0
                    rain_x = random.randint(0, screen_width)
                self.raindrops[i] = [rain_x, rain_y]

    def draw_place_elements(self, surface, place, camera_offset, opacity=1.0):
        # Draw specific elements based on the current place
        if place == "farmland":
            # Draw farms, fields, etc.
            self.draw_farmland(surface, camera_offset, opacity)
        elif place == "city":
            # Draw buildings, roads, etc.
            self.draw_city(surface, camera_offset, opacity)
        elif place == "hill_country":
            # Draw hills, mountains, etc.
            self.draw_hills(surface, camera_offset, opacity)
        elif place == "seaside":
            # Draw ocean, beach, etc.
            self.draw_seaside(surface, camera_offset, opacity)

    def draw_farmland(self, surface, camera_offset, opacity=1.0):
        # Draw farmland elements
        ground_y = screen_height - screen_height // 3

        # Draw fields with crops (simple rectangles)
        field_width = 300
        num_fields = screen_width // field_width + 2

        for i in range(num_fields):
            field_x = i * field_width - camera_offset % field_width
            field_rect = pygame.Rect(field_x, ground_y, field_width, 50)
            field_color = (194, 178, 128, int(255 * opacity))  # Wheat field color with alpha

            field_surface = pygame.Surface((field_width, 50), pygame.SRCALPHA)
            field_surface.fill(field_color)
            surface.blit(field_surface, (field_x, ground_y))

            # Draw crop rows
            crop_color = (139, 115, 85, int(255 * opacity))
            for j in range(10):
                row_x = field_x + j * 30
                crop_surface = pygame.Surface((10, 50), pygame.SRCALPHA)
                crop_surface.fill(crop_color)
                surface.blit(crop_surface, (row_x, ground_y))

        # Draw farm houses every 1000 pixels
        house_spacing = 1000
        scroll_offset_houses = camera_offset // 1
        house_start = (scroll_offset_houses // house_spacing) * house_spacing

        for i in range(3):  # Draw 3 houses in view
            house_x = house_start + i * house_spacing - scroll_offset_houses
            if 0 <= house_x <= screen_width:
                # House body
                house_color = (255, 0, 0, int(255 * opacity))
                house_surface = pygame.Surface((150, 100), pygame.SRCALPHA)
                house_surface.fill(house_color)
                surface.blit(house_surface, (house_x, ground_y - 100))

                # Roof
                roof_color = (139, 69, 19, int(255 * opacity))
                roof_points = [(0, 0), (95, -50), (190, 0)]
                roof_surface = pygame.Surface((190, 50), pygame.SRCALPHA)
                pygame.draw.polygon(roof_surface, roof_color, roof_points)
                surface.blit(roof_surface, (house_x - 20, ground_y - 100))

    def draw_city(self, surface, camera_offset, opacity=1.0):
        # Draw city elements
        ground_y = screen_height - screen_height // 3

        # Draw road
        road_color = (50, 50, 50, int(255 * opacity))
        road_surface = pygame.Surface((screen_width, 80), pygame.SRCALPHA)
        road_surface.fill(road_color)
        surface.blit(road_surface, (0, ground_y + 50))

        # Draw road markings
        marking_width = 50
        num_markings = screen_width // marking_width + 2
        for i in range(num_markings):
            marking_x = i * marking_width * 2 - camera_offset % (marking_width * 2)
            marking_color = (255, 255, 255, int(255 * opacity))
            marking_surface = pygame.Surface((marking_width, 10), pygame.SRCALPHA)
            marking_surface.fill(marking_color)
            surface.blit(marking_surface, (marking_x, ground_y + 90))

        # Draw buildings
        building_width = 120
        building_spacing = 150
        num_buildings = screen_width // building_spacing + 2

        for i in range(num_buildings):
            building_x = i * building_spacing - camera_offset % building_spacing
            height = random.randint(100, 250)
            building_color = (100, 100, 100, int(255 * opacity))
            building_surface = pygame.Surface((building_width, height), pygame.SRCALPHA)
            building_surface.fill(building_color)
            surface.blit(building_surface, (building_x, ground_y - height))

            # Draw windows
            for y in range(5):
                for x in range(3):
                    # Some windows are lit based on random chance and season
                    if random.random() > 0.3:  # Some windows are lit
                        if self.current_season == "night":
                            window_color = (255, 255, 0, int(255 * opacity))
                        else:
                            window_color = (200, 200, 200, int(255 * opacity))
                    else:
                        window_color = (50, 50, 50, int(255 * opacity))

                    window_surface = pygame.Surface((20, 30), pygame.SRCALPHA)
                    window_surface.fill(window_color)
                    surface.blit(window_surface, (building_x + 20 + x * 30, ground_y - height + 20 + y * 40))

    def draw_hills(self, surface, camera_offset, opacity=1.0):
        # Draw hill country elements
        ground_y = screen_height - screen_height // 3

        # Draw hills in the background
        hill_points = []
        parallax_factor = 0.3  # Hills move slower than the camera
        adjusted_offset = camera_offset * parallax_factor

        # First, establish base points across the width
        for x in range(0, screen_width + 100, 100):
            hill_points.append((x, ground_y - random.randint(50, 150)))

        # Connect the points with a smooth line
        hill_color = (100, 160, 100, int(255 * opacity))
        pygame.draw.lines(surface, hill_color, False, hill_points, 5)

        # Fill the area under the hills
        for i in range(len(hill_points) - 1):
            hill_segment = [
                hill_points[i],
                hill_points[i + 1],
                (hill_points[i + 1][0], ground_y + 100),
                (hill_points[i][0], ground_y + 100)
            ]
            hill_fill_color = (110, 170, 110, int(255 * opacity))
            pygame.draw.polygon(surface, hill_fill_color, hill_segment)

        # Draw trees on hills
        tree_spacing = 150
        num_trees = screen_width // tree_spacing + 2

        for i in range(num_trees):
            tree_x = i * tree_spacing - camera_offset % tree_spacing
            # Find the y position on the hill
            hill_idx = min(len(hill_points) - 1, int(tree_x / 100))
            tree_base_y = hill_points[hill_idx][1]

            # Draw tree trunk
            trunk_color = (139, 69, 19, int(255 * opacity))
            trunk_surface = pygame.Surface((10, 40), pygame.SRCALPHA)
            trunk_surface.fill(trunk_color)
            surface.blit(trunk_surface, (tree_x, tree_base_y - 40))

            # Draw tree foliage (circle)
            foliage_color = (34, 139, 34, int(255 * opacity))
            foliage_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(foliage_surface, foliage_color, (30, 30), 30)
            surface.blit(foliage_surface, (tree_x - 25, tree_base_y - 90))

    def draw_seaside(self, surface, camera_offset, opacity=1.0):
        # Draw seaside elements
        ground_y = screen_height - screen_height // 3

        # Draw ocean
        ocean_color = (0, 105, 148, int(255 * opacity))
        ocean_surface = pygame.Surface((screen_width, screen_height // 3), pygame.SRCALPHA)
        ocean_surface.fill(ocean_color)
        surface.blit(ocean_surface, (0, ground_y))

        # Draw waves
        wave_spacing = 50
        num_waves = screen_width // wave_spacing + 2

        for i in range(num_waves):
            wave_x = i * wave_spacing - camera_offset % wave_spacing
            wave_height = 10
            wave_points = [
                (wave_x, ground_y),
                (wave_x + wave_spacing // 2, ground_y - wave_height),
                (wave_x + wave_spacing, ground_y)
            ]
            wave_color = (173, 216, 230, int(255 * opacity))
            pygame.draw.lines(surface, wave_color, False, wave_points, 3)

        # Draw sand
        sand_color = (194, 178, 128, int(255 * opacity))
        sand_surface = pygame.Surface((screen_width, 20), pygame.SRCALPHA)
        sand_surface.fill(sand_color)
        surface.blit(sand_surface, (0, ground_y - 20))

        # Draw boats
        boat_spacing = 800
        num_boats = 3

        for i in range(num_boats):
            boat_x = i * boat_spacing - camera_offset % (boat_spacing * num_boats)
            boat_y = ground_y + 30

            # Boat body
            boat_points = [
                (0, 0),
                (100, 0),
                (80, 30),
                (20, 30)
            ]
            boat_color = (139, 69, 19, int(255 * opacity))
            boat_surface = pygame.Surface((100, 30), pygame.SRCALPHA)
            pygame.draw.polygon(boat_surface, boat_color, boat_points)
            surface.blit(boat_surface, (boat_x, boat_y))

            # Boat sail (only in sunny or night weather)
            if self.current_season != "rainy":
                sail_points = [
                    (0, 0),
                    (0, -70),
                    (40, -20)
                ]
                sail_color = (255, 255, 255, int(255 * opacity))
                sail_surface = pygame.Surface((40, 70), pygame.SRCALPHA)
                pygame.draw.polygon(sail_surface, sail_color, sail_points)
                surface.blit(sail_surface, (boat_x + 50, boat_y))


class Flight(pygame.sprite.Sprite):
    level_enemy = {1: {"count": 5, "spacing": 500},
                   2: {"count": 10, "spacing": 400},
                   3: {"count": 15, "spacing": 300}
                   }
    current_level_enemy_spawn = 0
    next_enemy_spawn_x = 0
    level_started = False

    def __init__(self, x, y, scale, velocity_vertical, velocity_horizontal, is_enemy=False):
        super().__init__()
        try:
            if is_enemy:
                img = pygame.image.load("images/jet_fighter_PNG7.png")
            else:
                img = pygame.image.load("images/TempFlightFigure.png")
            self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        except pygame.error:
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
        if self.rect.top < 0:
            self.rect.top = 0
            self.world_y = self.rect.height / 2
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.world_y = screen_height - self.rect.height / 2

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

        if self.rect.top < 0:
            self.rect.top = 0
            self.direction = 1
            self.vertical_movement_timer = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
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
        self.max_level = 6  # Increased to 6 levels for all combinations
        self.level_thresholds = {
            1: 0,  # Starting level
            2: 1000,  # Threshold to reach level 2
            3: 2000,  # Threshold to reach level 3
            4: 3000,  # Threshold to reach level 4
            5: 4000,  # Threshold to reach level 5
            6: 5000  # Threshold to reach level 6
        }
        self.level_completed = False
        self.level_transition_time = 0
        self.show_transition = False
        self.transition_duration = 3000  # milliseconds for level text display
        self.background_changed = False  # Flag to track background changes
        self.last_level = 1

    def update(self, player_distance, bg_manager):
        # Determine the current level based on distance traveled
        old_level = self.current_level

        for level in range(self.max_level, 0, -1):
            if player_distance >= self.level_thresholds[level]:
                if self.current_level < level:
                    # Level up!
                    self.current_level = level
                    self.show_transition = True
                    self.level_transition_time = pygame.time.get_ticks()
                    self.background_changed = False  # Reset flag for new level
                    level_up_fx.play()
                break

        # If level changed or background hasn't been set for this level
        if old_level != self.current_level or not self.background_changed:
            bg_manager.set_background_for_level(self.current_level)
            self.background_changed = True
            self.last_level = self.current_level

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
                1: "Sunny day over farmland!",
                2: "Rainy weather in the city!",
                3: "Night flight over the hills!",
                4: "Beautiful day at the seaside!",
                5: "Night flight over the city!",
                6: "Stormy weather at sea!"
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
    y_pos = random.randint(100, screen_height - 100)

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
                # Reset game with random starting background
                player_flight = Flight(screen_width // 4, screen_height // 2, 0.3, 5, 5, is_enemy=False)
                enemy_flights = []
                bg_manager = BackgroundManager()  # This creates a new random background
                level_manager = LevelManager()
                game_over = False
                game_completed = False
                score = 0
                spawn_enemy(enemy_flights, player_flight.world_x, 800, level_manager.current_level)

            if game_completed and event.key == pygame.K_r:
                # Reset game after completion with random starting background
                player_flight = Flight(screen_width // 4, screen_height // 2, 0.3, 5, 5, is_enemy=False)
                enemy_flights = []
                bg_manager = BackgroundManager()  # This creates a new random background
                level_manager = LevelManager()
                game_over = False
                game_completed = False
                score = 0
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

    # Always update the level based on distance, even during transition
    current_level = level_manager.update(score, bg_manager)

    # Enemy spawning with level-based timing
    spawn_timer += 1
    spawn_cooldown_for_level = max(30, 120 - current_level * 30)  # Spawn faster in higher levels

    if spawn_timer >= spawn_cooldown_for_level:
        spawn_enemy(enemy_flights, player_flight.world_x, 800, current_level)
        spawn_timer = 0

    # Remove enemies that are too far behind
    for enemy in enemy_flights[:]:
        if player_flight.world_x - enemy.world_x > screen_width:
            enemy_flights.remove(enemy)

    # Update player collision data
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
    if score >= level_manager.level_thresholds[level_manager.max_level] + 1000:
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

    # Draw level information
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