import pygame
import sys
import random
import math


class Level:
    def __init__(self, grid_size):
        self.grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        self.box_position = None
        self.obstacle_positions = []
        self.obstacle_types = []

    def generate_obstacles(self, num_obstacles):
        for _ in range(num_obstacles):
            # Generate a random position for the obstacle
            obstacle_position = (random.randint(0, len(self.grid) - 1), random.randint(0, len(self.grid) - 1))

            # Ensure the obstacle is not placed on the box or another obstacle
            while obstacle_position in self.obstacle_positions or obstacle_position == self.box_position:
                obstacle_position = (random.randint(0, len(self.grid) - 1), random.randint(0, len(self.grid) - 1))

            self.obstacle_positions.append(obstacle_position)
            self.obstacle_types.append(random.choice(['static', 'moving', 'bouncing']))

    def generate_box(self):
        # Generate a random position for the box
        self.box_position = (random.randint(0, len(self.grid) - 1), random.randint(0, len(self.grid) - 1))

        # Ensure the box is not placed on an obstacle
        while self.box_position in self.obstacle_positions:
            self.box_position = (random.randint(0, len(self.grid) - 1), random.randint(0, len(self.grid) - 1))

    def check_win_condition(self, banana_position):
        # The player wins if the banana is in the same position as the box
        return banana_position == self.box_position


class Banana:
    def __init__(self):
        self.position = (0, 0)  # Initial position
        self.velocity = (0, 0)  # Initial velocity
        self.is_golden = False  # By default, the banana is not golden

    def shoot(self, mouse_drag):
        # Calculate the new velocity based on the mouse drag
        # This is a simple implementation, you may need to adjust it based on your game's physics
        self.velocity = (-mouse_drag[0], -mouse_drag[1])

    def update_position(self):
        # Update the banana's position based on its velocity
        # This is a simple implementation, you may need to adjust it based on your game's physics
        self.position = (self.position[0] + self.velocity[0], self.position[1] + self.velocity[1])


class Obstacle:
    def __init__(self, obstacle_type):
        self.position = (0, 0)  # Initial position
        self.type = obstacle_type  # Type of the obstacle (static, moving, bouncing)
        self.velocity = (0, 0)  # Initial velocity (only for moving and bouncing obstacles)

    def update_position(self):
        # Update the obstacle's position based on its velocity
        # This only applies to moving and bouncing obstacles
        if self.type in ['moving', 'bouncing']:
            self.position = (self.position[0] + self.velocity[0], self.position[1] + self.velocity[1])

    def bounce(self):
        # Change the obstacle's direction
        # This only applies to bouncing obstacles
        if self.type == 'bouncing':
            self.velocity = (-self.velocity[0], -self.velocity[1])


class Box:
    def __init__(self, position):
        self.position = position  # Position of the box


class Player:
    def __init__(self):
        self.score = 0  # Initial score

    def update_score(self, points):
        # Add the given number of points to the player's score
        self.score += points


class Menu:
    def __init__(self):
        self.game_state = 'new game'  # Initial game state

    def display_menu(self):
        # Display the menu
        # This will depend on your game's user interface
        print('1. Start New Game')
        print('2. Continue Game')
        print('3. Display Scoreboard')

    def start_new_game(self, game):
        # Start a new game
        game.start_game()
        self.game_state = 'continue game'

    def continue_game(self, game):
        # Continue the game
        if self.game_state == 'continue game':
            game.resume_game()

    def display_scoreboard(self, player):
        # Display the scoreboard
        print('Score:', player.score)


class Game:
    def __init__(self):
        pygame.init()  # Initialize Pygame
        self.screen = pygame.display.set_mode((800, 600))  # Create the Pygame window
        self.clock = pygame.time.Clock()  # Create a clock object to control the frame rate
        self.current_banana = Banana()
        self.player = Player()
        self.level = Level(grid_size=10)
        self.menu = Menu()

    def start_game(self):
        self.level.generate_box()
        self.level.generate_obstacles(num_obstacles=5)
        self.game_loop()

    def pause_game(self):
        self.menu.game_state = 'paused'

    def resume_game(self):
        if self.menu.game_state == 'paused':
            self.menu.game_state = 'continue game'
            self.game_loop()

    def end_game(self):
        self.menu.game_state = 'end game'

    def check_collision(self):
        # Check if the banana has collided with an obstacle or the box
        if self.current_banana.position in self.level.obstacle_positions:
            return 'obstacle'
        elif self.current_banana.position == self.level.box_position:
            return 'box'
        else:
            return None

    def update_score(self, points):
        self.player.update_score(points)

    def generate_level(self):
        self.level = Level(grid_size=10)
        self.level.generate_box()
        self.level.generate_obstacles(num_obstacles=5)

    def draw_banana(self):
        pygame.draw.circle(self.screen, (255, 255, 0), self.current_banana.position, 10)

    def draw_box(self):
        pygame.draw.rect(self.screen, (255, 0, 0),
                         pygame.Rect(self.level.box_position[0], self.level.box_position[1], 50, 50))

    def draw_obstacles(self):
        for obstacle_position in self.level.obstacle_positions:
            pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(obstacle_position[0], obstacle_position[1], 50, 50))

    def game_loop(self):
        while self.menu.game_state == 'continue game':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.menu.game_state = 'end game'
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Get the mouse position when the user clicks
                    mouse_pos = pygame.mouse.get_pos()
                    self.current_banana.position = mouse_pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Get the mouse position when the user releases the mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    self.current_banana.shoot(mouse_pos)

            # Update the banana's position
            self.current_banana.update_position()

            # Check for collisions
            collision = self.check_collision()
            if collision == 'obstacle':
                # If the banana hit an obstacle, end the game
                self.end_game()
            elif collision == 'box':
                # If the banana hit the box, update the score and generate a new level
                self.update_score(1 if not self.current_banana.is_golden else 5)
                self.generate_level()

            # Render the game
            self.screen.fill((0, 0, 0))  # Clear the screen
            self.draw_banana()  # Draw the banana
            self.draw_box()  # Draw the box
            self.draw_obstacles()  # Draw the obstacles
            pygame.display.flip()  # Update the display
            self.clock.tick(60)  # Limit the frame rate to 60 FPS


if __name__ == "__main__":
    game = Game()
    game.start_game()

