#****************************************************************************
# playmaze.py - Runs a maze game and allows using the keyboard to move
# v1
# Boise State University CS 497
# Dr. Henderson
# Spring 2026
#
# This instantiates a MazeGame object and runst the game, passing in a
# function that handles keyboard events and moves the player's piece around
# the maze accordingly.
#
# Run with:
#  python playmaze <board num>
#
# where board num is 1,2,3, or 4
#----------------------------------------------------------------------------
import sys
import pygame

import mazes
from mazelib import MazeGame

maze_num = sys.argv[1] if len(sys.argv) > 1 else "1"
maze_attr = f"MAZE_{maze_num}"

try:
    maze_data = getattr(mazes, maze_attr)
    print(f"Loading {maze_attr}...")
except AttributeError:
    print(f"Error: {maze_attr} not found in mazes.py.")
    exit(1)

print("Use arrow keys to move. Press R to restart.")

game = MazeGame(maze_data)
game.run()
sys.exit(0)
