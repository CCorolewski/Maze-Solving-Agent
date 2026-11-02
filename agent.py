#****************************************************************************
# agent.py - Build 2 agent file
# v1
# Boise State University CS 497
# Dr. Henderson
# Spring 2026
#
# Implements the agent that b2.py uses to solve the maze
#----------------------------------------------------------------------------
from typing import List, Tuple

from langchain.agents import create_agent
from langchain.tools import tool

import chatlib

#--------------------------------------------------------------------------------------------------
# TODO: Define your system prompt. (25 pts)
#--------------------------------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are an analytical maze solver that obeys all the rules.

The maze contains:
S = start
E = exit
# = wall
T = trap
. = path

You can move in four directions:
1 = North
2 = East
3 = South
4 = West

Strategy:
Use a depth-first search strategy.

Rules:
- Follow the path by moving at a step size of 1.
- Keep track of where you have been with path_stack.
- Don't travel to the last position visited.
- Always check all directions to find paths to travel before moving.
- Always call check for traps before you move.
- Move with a step size of 1.
- Do not move into walls or traps.
- When you come to a branch save its location.
- If you reach a dead end, only then should you backtrack to a branch and try another direction.
- Keep track of where you have been so you do not loop forever.
- If you come to a branching path record it so you can go back to it if you reach a deadend along one path of the branch.
- Keep track of traps and deadends so you do not repeat routes.
- Continue exploring until the exit is found.
"""

#--------------------------------------------------------------------------------------------------
# Global instance of the game object (set below and available for use in your tools)
#--------------------------------------------------------------------------------------------------
maze_game = None

#--------------------------------------------------------------------------------------------------
# TODO: Define any variables to keep track of state for your agent here. (10 pts)
#--------------------------------------------------------------------------------------------------
visited = set()
path_stack = []
dead_ends = set()
traps = set()
last_position = None
branches = set()
#--------------------------------------------------------------------------------------------------
# TODO: Define tools you want your agent to be able to use here. (150 pts)
#--------------------------------------------------------------------------------------------------
@tool('is_solved', description='Returns True if the maze has been solved', return_direct=False)
def is_solved():
    return maze_game.has_won()

@tool('game_over', description='Returns true if the game is over', return_direct=False)
def game_over():
    return maze_game.is_over()

@tool('current_position', description="Returns the player's current position", return_direct=False)
def current_position():
    return maze_game.get_position()

@tool('check_trap', description="Returns the number of cells to a trap in a given direction or 0 if no trap exists", return_direct=False)
def check_trap(direction: int)->int:
    return maze_game.check_trap(direction)

@tool('check_direction', description='Returns the number of free cells from the given cell for the given direction', return_direct=False)
def check_direction(row: int, col: int, direction: int)-> int:
    return maze_game.get_free_cells_at(row, col, direction)

@tool('check_direction_self', description='Returns the number of free cells from the current position for the given direction', return_direct=False)
def check_direction_self(direction: int)->int:
    return maze_game.get_free_cells(direction)

@tool('move', description='Moves the number of steps in the given direction', return_direct=False)
def move(direction: int, steps: int=1)-> int:
    return maze_game.move(direction, steps)

@tool('retrace_steps', description="Returns the player's move history as a list of (row,col) tuples", return_direct=False)
def retrace_steps():
    return maze_game.get_moves()

#--------------------------------------------------------------------------------------------------
# TODO: Create an array of functions to pass to your agent as tools. (5 pts)
#--------------------------------------------------------------------------------------------------
tools = [ is_solved, game_over, current_position, check_trap, check_direction, check_direction_self,
         move, retrace_steps ]

#--------------------------------------------------------------------------------------------------
# Uses chatlib to get a chat model to serve as your agent using your tools and system prompt
#--------------------------------------------------------------------------------------------------
maze_agent = create_agent(
     chatlib.get_chat_model().llm,
    tools = tools,
    system_prompt = SYSTEM_PROMPT
)

#--------------------------------------------------------------------------------------------------
# The agent function will be set to control the maze in b2.py. The maze instance is passed in.
#--------------------------------------------------------------------------------------------------
def agent(game):
    global maze_game
    maze_game = game

    # Get the starting position from the game object
    start_pos = maze_game.get_position() 
    
    # Update the prompt to include the starting coordinates
    initial_input = f"I am at position {start_pos}. Please solve the maze."
    
    # static approach
    #response = maze_agent.invoke({
    #    'messages': [ { 'role': 'user', 'content': 'Please solve the maze'  } ]
    #})
    #return

    # Send the initial prompt and print trace until the agent solves the maze
    for chunk in maze_agent.stream({
            'messages': [ {'role': 'user', 'content': 'Please solve the maze'} ]
        }):
        for key, value in chunk.items():
            if key == 'tools' and 'messages' in value:
                for msg in value['messages']:
                    print(f"   ↳ Result: {msg.content}")
            elif 'messages' in value:
                for msg in value['messages']:
                    if hasattr(msg, 'content') and msg.content:
                        print(f"💭  Agent: {msg.content}")

                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tc in msg.tool_calls:
                            print(f"🔧  Calling: {tc['name']}({tc['args']})")


# Total points: 190
