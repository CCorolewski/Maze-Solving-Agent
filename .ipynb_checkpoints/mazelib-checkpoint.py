#****************************************************************************
# mazelib.py - Build 2 maze class
# v1
# Boise State University CS 497
# Dr. Henderson
# Spring 2026
#
# Implements a maze UI with methods to control a player's movement
# Uses the pygame library
#----------------------------------------------------------------------------
import pygame
import sys
import threading
import queue

# Initialize Pygame
pygame.init()

# Constants
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
LIGHT_BLUE = (173, 216, 230)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

class MazeGame:
    # Directions
    DIR_NORTH = 1
    DIR_EAST = 2
    DIR_SOUTH = 3
    DIR_WEST = 4

    # Cell types
    CELL_WALL = '#'
    CELL_START = 'S'
    CELL_EXIT = 'E'
    CELL_TRAP = 'T'
    CELL_PATH = '.'
    CELL_OOB = '-'
    CELL_BREADCRUMB = '+'

    def __init__(self, maze, cell_size=30):
        self.maze = [row[:] for row in maze]  # Deep copy
        self.grid_size = len(maze)
        
        # Find start and exit positions
        self.start_pos = None
        self.exit_pos = None
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.maze[row][col] == 'S':
                    self.start_pos = (row, col)
                elif self.maze[row][col] == 'E':
                    self.exit_pos = (row, col)
        
        self.lock = threading.RLock()
        self.reset()
        self.message = "Game started"
        # Display
        self.cell_size = cell_size
        self.window_size = self.grid_size * cell_size
        self.screen = pygame.display.set_mode((self.window_size, self.window_size + 30))
        pygame.display.set_caption("Maze Navigator - Agent Mode")
        self.clock = pygame.time.Clock()
        self._is_quit = False

    def reset(self):
        """Reset game state"""
        with self.lock:
            self.moves = [self.start_pos]
            self.running = True
            self.message = "Game reset"

    def quit(self):
        self._is_quit = True
        pygame.quit()
    
    def has_won(self):
        """Returns True if game is over and player has won"""
        row, col = self.moves[-1]
        return not self.running and self.maze[row][col]

    def is_over(self):
        """Returns True if game is over"""
        return not self.running

    def is_quit(self):
        """Returns True if game has been quit"""
        return self._is_quit
    
    def get_position(self):
        """Returns the player's current position"""
        with self.lock:
            return self.moves[-1]

    def get_moves(self):
        """Returns the player's move history as a list of (row,col) tuples"""
        with self.lock:
            return self.moves

    def get_cell(self):
        with self.lock:
            return self.maze[ self.moves[-1][0] ][ self.moves[-1][1] ]

    def check_trap(self, direction):
        """Returns number of cells to a trap in the given direction or 0 if no trap exists"""
        with self.lock:
            dr, dc = (0,0)
            match direction:
                case self.DIR_NORTH: dr = -1
                case self.DIR_EAST: dc = 1
                case self.DIR_SOUTH: dr = 1
                case self.DIR_WEST: dc = -1
                case _:
                    return 0

            row, col = self.moves[-1]
            free_cells = 0
            while True:
                row += dr
                col += dc
                if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
                    break
                cell = self.maze[row][col]
                if cell == self.CELL_WALL:
                    break
                free_cells += 1
                if cell == self.CELL_TRAP:
                    return free_cells

            return 0


    def get_free_cells_at(self, row, col, direction):
        """Returns the number of free cells from the given cell for the given direction"""
        with self.lock:
            dr, dc = (0,0)
            match direction:
                case self.DIR_NORTH: dr = -1
                case self.DIR_EAST: dc = 1
                case self.DIR_SOUTH: dr = 1
                case self.DIR_WEST: dc = -1
                case _:
                    return 0

            free_cells = 0
            while True:
                row += dr
                col += dc
                if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
                    break
                cell = self.maze[row][col]
                if cell == self.CELL_WALL:
                    break
                free_cells += 1

            return free_cells

    def get_free_cells(self, direction):
        """Returns the number of free cells from the current position for the given direction"""
        return self.get_free_cells_at(self.moves[-1][0], self.moves[-1][1], direction)

    def move(self, direction, steps=1):
        """Attempt to move in given direction"""
        allowed = min(self.get_free_cells(direction), steps)
        with self.lock:
            if not self.running or allowed == 0:
                return 0

            dr, dc = (0,0)
            match direction:
                case self.DIR_NORTH: dr = -1
                case self.DIR_EAST: dc = 1
                case self.DIR_SOUTH: dr = 1
                case self.DIR_WEST: dc = -1
                case _:
                    return 0


            for m in range(allowed):
              new_row = self.moves[-1][0] + dr
              new_col = self.moves[-1][1] + dc
              self.moves.append( (new_row, new_col) )
              cell_type = self.get_cell()
            
              # Check for trap
              if cell_type == 'T':
                  self.running = False
                  self.message = f"Hit trap! Game Over in {len(self.moves) - 1} moves"
                  return m + 1

              # Check for exit
              if cell_type == 'E':
                  self.running = False
                  self.message = f"Won in {len(self.moves) - 1} moves!"
                  return m + 1

            self.message = f"Moved {direction}"
            return allowed


    def draw_maze(self):
        """Draw the maze grid"""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = col * self.cell_size
                y = row * self.cell_size
                
                cell = self.maze[row][col]

                match cell:
                    case '#': color = BLACK
                    case 'S': color = GREEN
                    case 'E': color = YELLOW
                    case 'T': color = RED
                    case _: color = WHITE
                
                pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, GRAY, (x, y, self.cell_size, self.cell_size), 1)
    
    def draw_path(self, visited_path):
        """Draw the player's path"""
        for i in range(len(visited_path) - 1):
            start = visited_path[i]
            end = visited_path[i + 1]
            
            start_x = start[1] * self.cell_size + self.cell_size // 2
            start_y = start[0] * self.cell_size + self.cell_size // 2
            end_x = end[1] * self.cell_size + self.cell_size // 2
            end_y = end[0] * self.cell_size + self.cell_size // 2
            
            pygame.draw.line(self.screen, LIGHT_BLUE, (start_x, start_y), (end_x, end_y), 3)
    
    def draw_player(self, player_pos):
        """Draw the player"""
        x = player_pos[1] * self.cell_size + self.cell_size // 2
        y = player_pos[0] * self.cell_size + self.cell_size // 2
        pygame.draw.circle(self.screen, BLUE, (x, y), self.cell_size // 3)
    
    def draw_message(self, message):
        """Draw status message"""
        font = pygame.font.Font(None, 24)
        text = font.render(message, True, BLACK)
        text_rect = text.get_rect(center=(self.window_size // 2, self.window_size + 15))
        
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, WHITE, bg_rect)
        pygame.draw.rect(self.screen, BLACK, bg_rect, 2)
        
        self.screen.blit(text, text_rect)
    
    def update(self):
        """Update display with current game state"""
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.message = "User quit game"
                self.running = False
                self.quit();
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_UP:
                    self.move(self.DIR_NORTH)
                elif event.key == pygame.K_DOWN:
                    self.move(self.DIR_SOUTH)
                elif event.key == pygame.K_LEFT:
                    self.move(self.DIR_WEST)
                elif event.key == pygame.K_RIGHT:
                    self.move(self.DIR_EAST)

        if not self.is_quit():
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_maze()
            self.draw_path(self.moves)
            self.draw_player(self.moves[-1])
        
        status = f"{self.message} | Moves: {len(self.moves)}"
        if not self.running:
            if self.has_won():
                status = f"WON in {len(self.moves)} moves!"
            else:
                status = f"LOST in {len(self.moves)} moves!"

        if not self.is_quit():
            self.draw_message(status)
        
        if not self.is_quit():
            pygame.display.flip()
            self.clock.tick(FPS)
        
        #return self.running
        return True

    def run(self):
        while not self.is_quit():
            self.update()

        print(self.message)


    def start_agent(self, agent):
        # Start agent in a separate thread
        agent_thread = threading.Thread(target=agent, args=(self,), daemon=True)
        agent_thread.start()
