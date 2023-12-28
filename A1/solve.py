############################################################
## CSC 384, Intro to AI, University of Toronto.
## Assignment 1 Starter Code
## v1.1
##
## Changes: 
## v1.1: removed the hfn paramete from dfs. Updated solve_puzzle() accordingly.
############################################################

from typing import List
import heapq
from heapq import heappush, heappop
import time
import argparse
import math # for infinity

from board import *

def is_goal(state):
    """
    Returns True if the state is the goal state and False otherwise.

    :param state: the current state.
    :type state: State
    :return: True or False
    :rtype: bool
    """

    # Get the board
    board = state.board

    # Check if each storage is filled
    # Get box positions
    boxes = board.boxes
    storages = board.storage

    # Count the number of boxes reach the goal position
    count = 0
    for box in boxes:
        if box in storages:
            count += 1
    
    return count == len(storages)


def get_path(state):
    """
    Return a list of states containing the nodes on the path 
    from the initial state to the given state in order.

    :param state: The current state.
    :type state: State
    :return: The path.
    :rtype: List[State]
    """

    # Create a result path
    result = [state]
    curr = state
    while curr.parent != None:
        curr = curr.parent
        result.insert(0, curr)
    return result

################### Helper functions ###################
def positions_around(target):
    x = target[0]
    y = target[1]
    to_left = (x-1, y)
    to_right = (x+1, y)
    to_up = (x, y+1)
    to_down = (x, y-1)
    return [to_left, to_right, to_up, to_down]

def create_new_board(move_list, board, robot):
    if len(move_list) == 1: #no box around
        new_robs = []
        for rob in board.robots:
            if rob == robot:
                new_robs.append(move_list[0])
            else:
                new_robs.append(rob)
        new_board = Board(board.name, board.width, board.height, new_robs, board.boxes, board.storage, board.obstacles)
        return new_board
    else: # box around -> next move with box
        new_robs = []
        new_boxes = []
        for rob in board.robots:
            if rob == robot:
                new_robs.append(move_list[0])
            else:
                new_robs.append(rob)
        for bo in board.boxes:
            if bo == move_list[0]: # prev position of box(next move)
                new_boxes.append(move_list[1])
            else:
                new_boxes.append(bo)
        new_board = Board(board.name, board.width, board.height, new_robs, new_boxes, board.storage, board.obstacles)
        return new_board
    
def create_new_state(nboard, state, board):
    if state.hfn == None:
        nstate = State(nboard, None, state.f, state.depth+1, state)
        return nstate
    else:
        new_f = (state.f - state.hfn(board) + 1) + state.hfn(nboard)
        nstate = State(nboard, state.hfn, new_f, state.depth + 1, state)
        return nstate
################### Helper functions ###################
            

def get_successors(state):
    """
    Return a list containing the successor states of the given state.
    The states in the list may be in any arbitrary order.

    :param state: The current state.
    :type state: State
    :return: The list of successor states.
    :rtype: List[State]
    """

    # successor states
    result = []

    # Get board
    board = state.board
    # Get position(s) of robots
    robots = board.robots
    # Get position(s) of obstacles
    obstacles = board.obstacles
    # Get position(s) of boxes
    boxes = board.boxes

    for robot in robots:
        # four directions of next move of the robot
        next_states = positions_around(robot)
        can_move = next_states.copy()
        # See if the robot can move
        for move in next_states:
            if move in obstacles:
                # Cannot move
                can_move.remove(move)
            elif move in robots:
                # Cannot move
                if move in can_move:
                    can_move.remove(move)
            elif move in boxes: # Means that robot is adjacent to a box, move = box position
                # Can move with boxes, but need to check box next move condition
                box_x = move[0]
                box_y = move[1]
                if box_x == robot[0]:
                    box_next = (box_x, box_y + (box_y - robot[1]))
                    if box_next in robots:
                        can_move.remove(move)
                    elif box_next in obstacles:
                        can_move.remove(move)
                    elif box_next in boxes:
                        can_move.remove(move)
                else:
                    box_next = (box_x + (box_x-robot[0]), box_y)
                    if box_next in robots:
                        can_move.remove(move)
                    elif box_next in obstacles:
                        can_move.remove(move)
                    elif box_next in boxes:
                        can_move.remove(move)
        # The result moves in can_move can move
        for states in can_move:
            if states in boxes:
                x = states[0]
                y = states[1]
                if x == robot[0]:
                    # Move vertically
                    box_move = (x, y+(y-robot[1]))
                    nboard = create_new_board([states, box_move], board, robot)
                    nstate = create_new_state(nboard, state, board)
                    result.append(nstate)
                else:
                    # Move horizontally
                    box_move = (x+(x-robot[0]), y)
                    nboard = create_new_board([states, box_move], board, robot)
                    nstate = create_new_state(nboard, state, board)
                    result.append(nstate)
            else:
                nboard = create_new_board([states], board, robot)
                nstate = create_new_state(nboard, state, board)
                result.append(nstate)
    return result


def dfs(init_board):
    """
    Run the DFS algorithm given an initial board.

    If the function finds a goal state, it returns a list of states representing
    the path from the initial state to the goal state in order and the cost of
    the solution found.
    Otherwise, it returns am empty list and -1.

    :param init_board: The initial board.
    :type init_board: Board
    :return: (the path to goal state, solution cost)
    :rtype: List[State], int
    """
    frontiors = []
    visited_board = set()

    init_state = State(init_board, heuristic_zero, 0, 0, None)
    # Add initial state to frontier
    frontiors.append(init_state)
    # Is frontior empty?
    while frontiors:
        # Select and remove curr state from frontier
        curr_state = frontiors.pop()
        curr_id = curr_state.id
            # is curr a goal state?
        if is_goal(curr_state):
                # Yes, return the path
            path = get_path(curr_state)
            total_cost = len(path) - 1
            return path, total_cost
        else:
            # No, add its successors
            visited_board.add(curr_id)
            successors = get_successors(curr_state)
            for successor in successors:
                if successor.id not in visited_board:
                    frontiors.append(successor)
    return [], -1
    # raise NotImplementedError


def a_star(init_board, hfn):
    """
    Run the A_star search algorithm given an initial board and a heuristic function.

    If the function finds a goal state, it returns a list of states representing
    the path from the initial state to the goal state in order and the cost of
    the solution found.
    Otherwise, it returns am empty list and -1.

    :param init_board: The initial starting board.
    :type init_board: Board
    :param hfn: The heuristic function.
    :type hfn: Heuristic (a function that consumes a Board and produces a numeric heuristic value)
    :return: (the path to goal state, solution cost)
    :rtype: List[State], int
    """

    
    frontiers = []
    heapq.heapify(frontiers)
    visited_board = set()
    init_state = State(init_board, hfn, hfn(init_board), 0, None)
    heappush(frontiers, (init_state.f, init_state))

    while frontiers:
        curr_state = heappop(frontiers)[1]# Always choose the one with least f value
        # Is curr a goal state
        if is_goal(curr_state):
            path = get_path(curr_state)
            total_cost = curr_state.f - hfn(curr_state.board)
            return path, total_cost
        else:
            successors = get_successors(curr_state)
            for successor in successors:
                if successor.id not in visited_board:
                    visited_board.add(successor.id)
                    heappush(frontiers, (successor.f, successor))
    
    return [], -1
    # raise NotImplementedError

################### Helper functions ###################
def manhattan_distance(box, storage):
    box_x = box[0]
    box_y = box[1]
    storage_x = storage[0]
    storage_y = storage[1]
    return abs(box_x - storage_x) + abs(box_y - storage_y)

def is_dead_state(box, board):
    obstacles = board.obstacles
    moves = positions_around(box)
    left = moves[0]
    right = moves[1]
    up = moves[2]
    down = moves[3]
    if left in obstacles and (up in obstacles or down in obstacles):
        return True
    if right in obstacles and (up in obstacles or down in obstacles):
        return True
    return False

################### Helper functions ###################


def heuristic_basic(board):
    """
    Returns the heuristic value for the given board
    based on the Manhattan Distance Heuristic function.

    Returns the sum of the Manhattan distances between each box 
    and its closest storage point.

    :param board: The current board.
    :type board: Board
    :return: The heuristic value.
    :rtype: int
    """


    box_positions = board.boxes
    storage_positions = board.storage

    sum_manhattan_distance = 0
    for box in box_positions:
        closest = math.inf
        closest_storage = None
        for storage in storage_positions:
            dist = manhattan_distance(box, storage)
            if dist < closest:
                closest = dist
        sum_manhattan_distance += closest
    return sum_manhattan_distance
    
    # raise NotImplementedError

def heuristic_advanced(board):
    """
    An advanced heuristic of your own choosing and invention.

    :param board: The current board.
    :type board: Board
    :return: The heuristic value.
    :rtype: int
    """
    boxes = board.boxes.copy()
    storages = board.storage.copy()
    sum_manhattan_distance = 0

    for box in boxes:
        # check if the box have two neighbours that are obstacles
        if is_dead_state(box, board):
            return math.inf
        closest = math.inf
        closest_storage = None
        for storage in storages:
            dist = manhattan_distance(box, storage)
            if dist < closest:
                closest = dist
                closest_storage = storage
        sum_manhattan_distance += closest
        storages.remove(closest_storage)
    return sum_manhattan_distance
    # raise NotImplementedError


def solve_puzzle(board: Board, algorithm: str, hfn):
    """
    Solve the given puzzle using the given type of algorithm.

    :param algorithm: the search algorithm
    :type algorithm: str
    :param hfn: The heuristic function
    :type hfn: Optional[Heuristic]

    :return: the path from the initial state to the goal state
    :rtype: List[State]
    """

    print("Initial board")
    board.display()

    time_start = time.time()

    if algorithm == 'a_star':
        print("Executing A* search")
        path, step = a_star(board, hfn)
    elif algorithm == 'dfs':
        print("Executing DFS")
        path, step = dfs(board)
    else:
        raise NotImplementedError

    time_end = time.time()
    time_elapsed = time_end - time_start

    if not path:

        print('No solution for this puzzle')
        return []

    else:

        print('Goal state found: ')
        path[-1].board.display()

        print('Solution is: ')

        counter = 0
        while counter < len(path):
            print(counter + 1)
            path[counter].board.display()
            print()
            counter += 1

        print('Solution cost: {}'.format(step))
        print('Time taken: {:.2f}s'.format(time_elapsed))

        return path


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The file that contains the puzzle."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The file that contains the solution to the puzzle."
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        required=True,
        choices=['a_star', 'dfs'],
        help="The searching algorithm."
    )
    parser.add_argument(
        "--heuristic",
        type=str,
        required=False,
        default=None,
        choices=['zero', 'basic', 'advanced'],
        help="The heuristic used for any heuristic search."
    )
    args = parser.parse_args()

    # set the heuristic function
    heuristic = heuristic_zero
    if args.heuristic == 'basic':
        heuristic = heuristic_basic
    elif args.heuristic == 'advanced':
        heuristic = heuristic_advanced

    # read the boards from the file
    board = read_from_file(args.inputfile)

    # solve the puzzles
    path = solve_puzzle(board, args.algorithm, heuristic)

    # save solution in output file
    outputfile = open(args.outputfile, "w")
    counter = 1
    for state in path:
        print(counter, file=outputfile)
        print(state.board, file=outputfile)
        counter += 1
    outputfile.close()