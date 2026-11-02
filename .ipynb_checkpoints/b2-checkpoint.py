#****************************************************************************
# b2.py - Build 2 main file
# v1
# Boise State University CS 497
# Dr. Henderson
# Spring 2026
#
# Loads a maze file an starts the maze with the agent defined in agent.py
#
# Run with:
#  python b2.py <board num>
#
# where board num is 1,2,3, or 4
#----------------------------------------------------------------------------
import sys

from mazelib import MazeGame
from agent import agent
import mazes

maze_num = sys.argv[1] if len(sys.argv) > 1 else "1"
maze_attr = f"MAZE_{maze_num}"

try:
    maze_data = getattr(mazes, maze_attr)
    print(f"Loading {maze_attr}...")
except AttributeError:
    print(f"Error: {maze_attr} not found in mazes.py.")
    exit(1)

game = MazeGame(maze_data)
game.start_agent(agent)
game.run()
