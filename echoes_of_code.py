import pygame
import sys
import time
import copy
from enum import Enum
from typing import List, Dict, Tuple, Optional

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
FPS = 60
LOOP_DURATION = 10  # seconds

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)

# Direction enum for movement
class Direction(Enum):
    NONE = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

# Action class to record player actions
class Action:
    def __init__(self, action_type: str, position: Tuple[int, int], time_stamp: float, direction: Direction = Direction.NONE):
        self.action_type = action_type  # "move", "interact", etc.
        self.position = position
        self.time_stamp = time_stamp
        self.direction = direction

    def __str__(self):
        return f"Action({self.action_type}, {self.position}, {self.time_stamp}, {self.direction})"

# Player class
class Player:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int] = BLUE):
        self.x = x
        self.y = y
        self.width = TILE_SIZE - 10
        self.height = TILE_SIZE - 10
        self.color = color
        self.speed = 5
        self.actions = []
        self.current_direction = Direction.NONE
        self.is_echo = False
        self.alpha = 255  # For transparency (255 = fully opaque)

    def move(self, direction: Direction, game_objects: List):
        old_x, old_y = self.x, self.y

        if direction == Direction.UP:
            self.y -= self.speed
        elif direction == Direction.DOWN:
            self.y += self.speed
        elif direction == Direction.LEFT:
            self.x -= self.speed
        elif direction == Direction.RIGHT:
            self.x += self.speed

        # Check for collisions with walls and objects
        if self.check_collision(game_objects):
            self.x, self.y = old_x, old_y
            return False

        # Keep player within screen bounds
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

        self.current_direction = direction
        return True

    def check_collision(self, game_objects: List) -> bool:
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        for obj in game_objects:
            if isinstance(obj, Wall):
                if player_rect.colliderect(pygame.Rect(obj.x, obj.y, obj.width, obj.height)):
                    return True

            # Gates block unless they're open
            if isinstance(obj, Gate) and not obj.is_open:
                if player_rect.colliderect(pygame.Rect(obj.x, obj.y, obj.width, obj.height)):
                    return True

        return False

    def record_action(self, action_type: str, time_stamp: float):
        self.actions.append(Action(action_type, (self.x, self.y), time_stamp, self.current_direction))

    def draw(self, screen):
        if self.is_echo:
            # Create a surface with per-pixel alpha
            s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # Draw with alpha
            pygame.draw.rect(s, (*self.color, self.alpha), (0, 0, self.width, self.height))
            screen.blit(s, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

# Echo class (inherits from Player)
class Echo(Player):
    def __init__(self, player: Player, color: Tuple[int, int, int], loop_number: int):
        super().__init__(player.x, player.y, color)
        self.actions = copy.deepcopy(player.actions)
        self.current_action_index = 0
        self.is_echo = True
        self.alpha = 128  # Semi-transparent
        self.loop_number = loop_number  # Which loop this echo is from

    def update(self, current_time: float, game_objects: List):
        # If we have actions to replay and haven't reached the end
        if self.current_action_index < len(self.actions):
            next_action = self.actions[self.current_action_index]

            # If it's time to perform this action
            if current_time >= next_action.time_stamp:
                if next_action.action_type == "move":
                    self.x, self.y = next_action.position
                    self.current_direction = next_action.direction
                elif next_action.action_type == "interact":
                    # Check if we're near any interactive objects
                    self.interact_with_objects(game_objects)

                self.current_action_index += 1

    def interact_with_objects(self, game_objects: List):
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        for obj in game_objects:
            if isinstance(obj, Switch) or isinstance(obj, Terminal):
                obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                if player_rect.colliderect(obj_rect):
                    obj.activate()

# Wall class
class Wall:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = GRAY

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

# Switch class
class Switch:
    def __init__(self, x: int, y: int, target_id: int):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.is_active = False
        self.target_id = target_id  # ID of the object this switch controls
        self.color_inactive = RED
        self.color_active = GREEN

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def draw(self, screen):
        color = self.color_active if self.is_active else self.color_inactive
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        # Draw a circle in the middle to make it look like a button
        pygame.draw.circle(screen, BLACK, (self.x + self.width // 2, self.y + self.height // 2), self.width // 3)

# Pressure Plate class
class PressurePlate:
    def __init__(self, x: int, y: int, target_id: int):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.is_active = False
        self.target_id = target_id
        self.color_inactive = YELLOW
        self.color_active = GREEN

    def update(self, players: List[Player]):
        # Check if any player is standing on the pressure plate
        self.is_active = False
        plate_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        for player in players:
            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            if plate_rect.colliderect(player_rect):
                self.is_active = True
                break

    def draw(self, screen):
        color = self.color_active if self.is_active else self.color_inactive
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        # Draw lines to make it look like a pressure plate
        for i in range(1, 4):
            offset = i * (self.width // 4)
            pygame.draw.line(screen, BLACK, (self.x + offset, self.y),
                            (self.x + offset, self.y + self.height), 2)

# Gate class
class Gate:
    def __init__(self, x: int, y: int, width: int, height: int, gate_id: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.gate_id = gate_id
        self.is_open = False
        self.color_closed = RED
        self.color_open = GREEN

    def update(self, switches: List):
        # Check if any switch controlling this gate is active
        for switch in switches:
            if switch.target_id == self.gate_id and switch.is_active:
                self.is_open = True
                return

        # If no active switch found, close the gate
        self.is_open = False

    def draw(self, screen):
        if not self.is_open:
            pygame.draw.rect(screen, self.color_closed, (self.x, self.y, self.width, self.height))
            # Add some lines to make it look like a gate
            for i in range(0, self.width, 10):
                pygame.draw.line(screen, BLACK, (self.x + i, self.y),
                                (self.x + i, self.y + self.height), 2)

# Terminal class
class Terminal:
    def __init__(self, x: int, y: int, target_id: int):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.target_id = target_id
        self.is_active = False
        self.color = CYAN

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw a terminal-like symbol
        inner_rect = (self.x + 5, self.y + 5, self.width - 10, self.height - 10)
        pygame.draw.rect(screen, BLACK, inner_rect)
        # Draw a cursor
        if self.is_active:
            cursor_x = self.x + 10
            cursor_y = self.y + self.height // 2
            pygame.draw.rect(screen, WHITE, (cursor_x, cursor_y, 10, 2))

# Exit class
class Exit:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.color = GREEN

    def check_player_reached(self, player: Player) -> bool:
        exit_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        return exit_rect.colliderect(player_rect)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw an exit symbol
        pygame.draw.polygon(screen, WHITE, [
            (self.x + self.width // 2, self.y + 5),
            (self.x + self.width - 5, self.y + self.height // 2),
            (self.x + self.width // 2, self.y + self.height - 5),
            (self.x + 5, self.y + self.height // 2)
        ])

# Timer Manager class
class TimerManager:
    def __init__(self, loop_duration: float, max_loops: int):
        self.loop_duration = loop_duration
        self.max_loops = max_loops
        self.start_time = time.time()
        self.current_loop = 1
        self.paused = False
        self.pause_time = 0
        self.total_pause_time = 0

    def get_elapsed_time(self) -> float:
        if self.paused:
            return self.pause_time - self.start_time - self.total_pause_time
        return time.time() - self.start_time - self.total_pause_time

    def get_loop_time(self) -> float:
        """Get time elapsed in the current loop"""
        return self.get_elapsed_time() % self.loop_duration

    def get_time_remaining(self) -> float:
        """Get time remaining in the current loop"""
        return self.loop_duration - self.get_loop_time()

    def should_reset_loop(self) -> bool:
        return self.get_loop_time() >= self.loop_duration

    def reset_loop(self):
        self.current_loop += 1

    def is_game_over(self) -> bool:
        return self.current_loop > self.max_loops

    def pause(self):
        if not self.paused:
            self.paused = True
            self.pause_time = time.time()

    def unpause(self):
        if self.paused:
            self.paused = False
            self.total_pause_time += time.time() - self.pause_time

# Level class
class Level:
    def __init__(self, level_number: int, player_start: Tuple[int, int], max_loops: int):
        self.level_number = level_number
        self.player_start = player_start
        self.max_loops = max_loops
        self.walls = []
        self.switches = []
        self.pressure_plates = []
        self.gates = []
        self.terminals = []
        self.exit = None
        self.completed = False

    def add_wall(self, x: int, y: int, width: int, height: int):
        self.walls.append(Wall(x, y, width, height))

    def add_switch(self, x: int, y: int, target_id: int):
        self.switches.append(Switch(x, y, target_id))

    def add_pressure_plate(self, x: int, y: int, target_id: int):
        self.pressure_plates.append(PressurePlate(x, y, target_id))

    def add_gate(self, x: int, y: int, width: int, height: int, gate_id: int):
        self.gates.append(Gate(x, y, width, height, gate_id))

    def add_terminal(self, x: int, y: int, target_id: int):
        self.terminals.append(Terminal(x, y, target_id))

    def set_exit(self, x: int, y: int):
        self.exit = Exit(x, y)

    def get_all_objects(self):
        return self.walls + self.gates

    def get_interactive_objects(self):
        return self.switches + self.pressure_plates + self.terminals

    def update(self, players: List[Player]):
        # Update pressure plates
        for plate in self.pressure_plates:
            plate.update(players)

        # Update gates based on switches and pressure plates
        for gate in self.gates:
            gate.update(self.switches + self.pressure_plates)

        # Check if player reached exit
        if self.exit and players and not self.completed:
            if self.exit.check_player_reached(players[0]):  # Check only the main player
                self.completed = True
                return True

        return False

# Level Manager class
class LevelManager:
    def __init__(self):
        self.levels = []
        self.current_level_index = 0
        self.create_levels()

    def create_levels(self):
        # Level 1: Simple pressure plate and gate
        level1 = Level(1, (100, 300), 3)  # Player starts at (100, 300), 3 loops max

        # Add walls (border)
        level1.add_wall(0, 0, SCREEN_WIDTH, 20)  # Top
        level1.add_wall(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)  # Bottom
        level1.add_wall(0, 0, 20, SCREEN_HEIGHT)  # Left
        level1.add_wall(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT)  # Right

        # Add internal walls
        level1.add_wall(200, 100, 20, 400)  # Vertical wall
        level1.add_wall(400, 100, 20, 300)  # Another vertical wall
        level1.add_wall(600, 200, 20, 300)  # Another vertical wall

        # Add pressure plate
        level1.add_pressure_plate(300, 200, 1)  # Controls gate with ID 1

        # Add gate
        level1.add_gate(400, 400, 20, 100, 1)  # Gate with ID 1

        # Add exit
        level1.set_exit(700, 300)

        self.levels.append(level1)

        # Level 2: More complex with terminal and multiple gates
        level2 = Level(2, (100, 300), 4)  # Player starts at (100, 300), 4 loops max

        # Add walls (border)
        level2.add_wall(0, 0, SCREEN_WIDTH, 20)  # Top
        level2.add_wall(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)  # Bottom
        level2.add_wall(0, 0, 20, SCREEN_HEIGHT)  # Left
        level2.add_wall(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT)  # Right

        # Add internal walls
        level2.add_wall(200, 100, 20, 200)  # Vertical wall
        level2.add_wall(200, 400, 20, 100)  # Another vertical wall
        level2.add_wall(400, 200, 20, 300)  # Another vertical wall
        level2.add_wall(600, 100, 20, 200)  # Another vertical wall
        level2.add_wall(600, 400, 20, 100)  # Another vertical wall

        # Add pressure plate
        level2.add_pressure_plate(300, 200, 1)  # Controls gate with ID 1

        # Add terminal
        level2.add_terminal(300, 400, 2)  # Controls gate with ID 2

        # Add gates
        level2.add_gate(400, 300, 20, 100, 1)  # Gate with ID 1
        level2.add_gate(600, 300, 20, 100, 2)  # Gate with ID 2

        # Add exit
        level2.set_exit(700, 300)

        self.levels.append(level2)

    def get_current_level(self) -> Level:
        return self.levels[self.current_level_index]

    def next_level(self) -> bool:
        if self.current_level_index < len(self.levels) - 1:
            self.current_level_index += 1
            return True
        return False

# Game class
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Echoes of Code")
        self.clock = pygame.time.Clock()
        self.level_manager = LevelManager()
        self.reset_game()

        # Load sounds
        self.load_sounds()

        # Font for UI
        self.font = pygame.font.SysFont(None, 36)

        # Game states
        self.game_state = "playing"  # "playing", "level_complete", "game_over", "game_complete"
        self.transition_timer = 0

    def load_sounds(self):
        # Placeholder for sound loading
        self.sounds = {
            "loop_reset": None,
            "victory": None,
            "interact": None
        }

        # Try to load sounds, but don't crash if they're not available
        try:
            self.sounds["loop_reset"] = pygame.mixer.Sound("sounds/loop_reset.wav")
            self.sounds["victory"] = pygame.mixer.Sound("sounds/victory.wav")
            self.sounds["interact"] = pygame.mixer.Sound("sounds/interact.wav")
        except:
            print("Warning: Could not load some sound files. Continuing without sound.")

    def reset_game(self):
        current_level = self.level_manager.get_current_level()
        self.player = Player(current_level.player_start[0], current_level.player_start[1])
        self.echoes = []
        self.timer_manager = TimerManager(LOOP_DURATION, current_level.max_loops)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_SPACE and self.game_state != "playing":
                    if self.game_state == "level_complete":
                        if self.level_manager.next_level():
                            self.reset_game()
                            self.game_state = "playing"
                        else:
                            self.game_state = "game_complete"
                    elif self.game_state in ["game_over", "game_complete"]:
                        self.level_manager.current_level_index = 0
                        self.reset_game()
                        self.game_state = "playing"
                elif event.key == pygame.K_e:
                    # Interact with objects
                    self.interact_with_objects()

        return True

    def interact_with_objects(self):
        if self.game_state != "playing":
            return

        current_level = self.level_manager.get_current_level()
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)

        for obj in current_level.get_interactive_objects():
            obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            if player_rect.colliderect(obj_rect):
                if isinstance(obj, Terminal) or isinstance(obj, Switch):
                    obj.activate()
                    # Record the interaction
                    self.player.record_action("interact", self.timer_manager.get_elapsed_time())
                    # Play sound
                    if self.sounds["interact"]:
                        self.sounds["interact"].play()

    def update(self):
        if self.game_state != "playing":
            return

        current_level = self.level_manager.get_current_level()

        # Handle player movement
        keys = pygame.key.get_pressed()
        direction = Direction.NONE

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction = Direction.UP
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction = Direction.DOWN
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction = Direction.LEFT
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction = Direction.RIGHT

        if direction != Direction.NONE:
            if self.player.move(direction, current_level.get_all_objects()):
                # Record the movement
                self.player.record_action("move", self.timer_manager.get_elapsed_time())

        # Update echoes
        for echo in self.echoes:
            echo.update(self.timer_manager.get_elapsed_time(), current_level.get_all_objects())

        # Update level objects
        all_players = [self.player] + self.echoes
        if current_level.update(all_players):
            # Level completed
            self.game_state = "level_complete"
            self.transition_timer = time.time()
            # Play victory sound
            if self.sounds["victory"]:
                self.sounds["victory"].play()

        # Check if loop should reset
        if self.timer_manager.should_reset_loop():
            self.reset_loop()

        # Check if game is over (max loops reached)
        if self.timer_manager.is_game_over():
            self.game_state = "game_over"
            self.transition_timer = time.time()

    def reset_loop(self):
        # Create a new echo from the current player
        echo_colors = [PURPLE, YELLOW, CYAN, RED, GREEN]
        echo_color = echo_colors[min(len(self.echoes), len(echo_colors) - 1)]
        self.echoes.append(Echo(self.player, echo_color, self.timer_manager.current_loop))

        # Reset player position
        current_level = self.level_manager.get_current_level()
        self.player.x, self.player.y = current_level.player_start

        # Clear player actions for the new loop
        self.player.actions = []

        # Reset interactive objects
        for obj in current_level.get_interactive_objects():
            if isinstance(obj, Switch) or isinstance(obj, Terminal):
                obj.deactivate()

        # Increment loop counter
        self.timer_manager.reset_loop()

        # Play loop reset sound
        if self.sounds["loop_reset"]:
            self.sounds["loop_reset"].play()

    def draw(self):
        self.screen.fill(BLACK)

        if self.game_state == "playing":
            current_level = self.level_manager.get_current_level()

            # Draw level objects
            for wall in current_level.walls:
                wall.draw(self.screen)

            for gate in current_level.gates:
                gate.draw(self.screen)

            for switch in current_level.switches:
                switch.draw(self.screen)

            for plate in current_level.pressure_plates:
                plate.draw(self.screen)

            for terminal in current_level.terminals:
                terminal.draw(self.screen)

            if current_level.exit:
                current_level.exit.draw(self.screen)

            # Draw echoes
            for echo in self.echoes:
                echo.draw(self.screen)

            # Draw player
            self.player.draw(self.screen)

            # Draw UI
            self.draw_ui()

        elif self.game_state == "level_complete":
            self.draw_message("Level Complete!", "Press SPACE to continue")

        elif self.game_state == "game_over":
            self.draw_message("Game Over!", "Press SPACE to restart")

        elif self.game_state == "game_complete":
            self.draw_message("Congratulations!", "You've completed all levels! Press SPACE to restart")

        pygame.display.flip()

    def draw_ui(self):
        # Draw timer
        time_remaining = self.timer_manager.get_time_remaining()
        timer_text = self.font.render(f"Time: {time_remaining:.1f}", True, WHITE)
        self.screen.blit(timer_text, (10, 10))

        # Draw loop counter
        loop_text = self.font.render(f"Loop: {self.timer_manager.current_loop}/{self.timer_manager.max_loops}", True, WHITE)
        self.screen.blit(loop_text, (SCREEN_WIDTH - 150, 10))

        # Draw level number
        level_text = self.font.render(f"Level: {self.level_manager.get_current_level().level_number}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 50, 10))

    def draw_message(self, title: str, subtitle: str):
        # Draw title
        title_text = self.font.render(title, True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(title_text, title_rect)

        # Draw subtitle
        subtitle_text = self.font.render(subtitle, True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(subtitle_text, subtitle_rect)

    def run(self):
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

# Main function
def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()