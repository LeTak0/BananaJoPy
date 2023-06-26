import pygame
import random
import math

# Define some constants
GRID_CELL_SIZE = 50  # Size of each cell in the grid
SCREEN_WIDTH = 1920  # Width of the screen in pixels
SCREEN_HEIGHT = 1020  # Height of the screen in pixels

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
        self.position = (random.randint(0, SCREEN_WIDTH-100), random.randint(0, SCREEN_HEIGHT-100))
        self.velocity = (0, 0)  # Initial velocity
        self.is_golden = False  # By default, the banana is not golden

    def shoot(self, mouse_drag):
        # Calculate the new velocity based on the mouse drag
        # This is a simple implementation, you may need to adjust it based on your game's physics
        scaling_factor = 0.01  # Adjust this value to change the speed of the banana
        self.velocity = (-mouse_drag[0] * scaling_factor, -mouse_drag[1] * scaling_factor)

    def update_position(self):
        # Calculate the new position
        new_position = (self.position[0] + self.velocity[0], self.position[1] + self.velocity[1])

        # Check if the new position would be outside the screen
        if new_position[0] < 0 or new_position[0] > SCREEN_WIDTH:
            # If it would be, reverse the x-velocity to make the banana bounce off the edge
            self.velocity = (-self.velocity[0], self.velocity[1])
        if new_position[1] < 0 or new_position[1] > SCREEN_HEIGHT:
            # If it would be, reverse the y-velocity to make the banana bounce off the edge
            self.velocity = (self.velocity[0], -self.velocity[1])

        # Update the position
        self.position = (self.position[0] + self.velocity[0], self.position[1] + self.velocity[1])

        # Apply damping (reduce the velocity)
        damping_factor = 0.99  # Adjust this value to change how quickly the banana slows down
        self.velocity = (self.velocity[0] * damping_factor, self.velocity[1] * damping_factor)

    def respawn(self):
        # Set the position to a random point within the screen boundaries
        self.position = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        # Reset the velocity
        self.velocity = (0, 0)


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
        self.level = 1  # Initial level

    def update_score(self, points):
        # Add the given number of points to the player's score
        self.score += points

    def update_level(self):
        # Increase the level by 1
        self.level += 1


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
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Create the Pygame window
        self.clock = pygame.time.Clock()  # Create a clock object to control the frame rate
        self.current_banana = Banana()
        self.player = Player()
        self.level = Level(grid_size=8)
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
        for obstacle_position in self.level.obstacle_positions:
            # Convert the obstacle's position from grid cells to pixels
            obstacle_position_pixels = (obstacle_position[0] * GRID_CELL_SIZE, obstacle_position[1] * GRID_CELL_SIZE)
            distance = math.sqrt((self.current_banana.position[0] - obstacle_position_pixels[0]) ** 2 + (
                        self.current_banana.position[1] - obstacle_position_pixels[1]) ** 2)
            if distance < GRID_CELL_SIZE:
                return 'obstacle'
        # Convert the box's position from grid cells to pixels
        box_position_pixels = (self.level.box_position[0] * GRID_CELL_SIZE, self.level.box_position[1] * GRID_CELL_SIZE)
        distance = math.sqrt((self.current_banana.position[0] - box_position_pixels[0]) ** 2 + (
                    self.current_banana.position[1] - box_position_pixels[1]) ** 2)
        if distance < GRID_CELL_SIZE:
            return 'box'
        return None

    def update_score(self, points):
        self.player.update_score(points)

    def generate_level(self):
        self.level = Level(grid_size=15)
        self.level.generate_box()
        self.level.generate_obstacles(num_obstacles=5)
        self.current_banana.respawn()

    def draw_banana(self):
        pixel_position = (self.current_banana.position[0], self.current_banana.position[1])
        pygame.draw.circle(self.screen, (255, 255, 0), pixel_position, 10)

    def draw_box(self):
        pixel_position = (self.level.box_position[0] * GRID_CELL_SIZE, self.level.box_position[1] * GRID_CELL_SIZE)
        pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(pixel_position[0], pixel_position[1], 50, 50))

    def draw_obstacles(self):
        for obstacle_position in self.level.obstacle_positions:
            pixel_position = (obstacle_position[0] * GRID_CELL_SIZE, obstacle_position[1] * GRID_CELL_SIZE)
            pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(pixel_position[0], pixel_position[1], 50, 50))

    def draw_text(self):
        font = pygame.font.Font(None, 36)  # Choose the font for the text
        text = font.render(f"Level: {self.player.level} Score: {self.player.score}", 1,
                           (255, 255, 255))  # Create the text
        textpos = text.get_rect(centerx=self.screen.get_width() / 2,
                                y=self.screen.get_height() - 20)  # Position the text
        self.screen.blit(text, textpos)  # Draw the text on the screen

    def game_loop(self):
        mouse_down_pos = None  # Variable to store the position where the mouse button was pressed
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("QUIT event triggered")
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Store the mouse position when the user clicks
                    mouse_down_pos = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Calculate the mouse drag
                    mouse_drag = (
                        pygame.mouse.get_pos()[0] - mouse_down_pos[0], pygame.mouse.get_pos()[1] - mouse_down_pos[1])
                    # Shoot the banana
                    self.current_banana.shoot(mouse_drag)

            # Update the banana's position
            self.current_banana.update_position()

            # Check for collisions
            collision = self.check_collision()
            if collision == 'obstacle':
                print("Obstacle collision detected")
                # If the banana hit an obstacle, end the game
                running = False
            elif collision == 'box':
                # If the banana hit the box, update the score and generate a new level
                self.update_score(1 if not self.current_banana.is_golden else 5)
                self.player.update_level() # Update the player's level
                self.generate_level()

            # Render the game
            self.screen.fill((0, 0, 0))  # Clear the screen
            self.draw_banana()  # Draw the banana
            self.draw_box()  # Draw the box
            self.draw_obstacles()  # Draw the obstacles
            self.draw_text()  # Draw the text
            pygame.display.flip()  # Update the display
            self.clock.tick(60)  # Limit the frame rate to 60 FPS


if __name__ == "__main__":
    game = Game()
    game.menu.display_menu()
    game.menu.start_new_game(game)
    game.start_game()

