###############################################################################
# This file implements various alpha-beta pruning agents.
#
# CSC 384 Fall 2023 Assignment 2
# version 1.0
###############################################################################
from mancala_game import Board, play_move
from utils import *

########################## Helper Function ####################################
def terminal(board, player):
    curr_next = board.get_possible_moves(player)
    oppo_next = board.get_possible_moves(get_opponent(player))
    return curr_next == [] or oppo_next == []
###############################################################################


def alphabeta_max_basic(board, curr_player, alpha, beta, heuristic_func):
    """
    Perform Alpha-Beta Pruning for MAX player.
    Return the best move and its minimax value.
    If the board is a terminal state, return None as its best move.

    :param board: the current board
    :param curr_player: the current player
    :param alpha: current alpha value
    :param beta: current beta value
    :param heuristic_func: the heuristic function
    :return the best move and its minimax value.
    """

    oppo_player = get_opponent(curr_player)

    # If the board is a terminal state
    if terminal(board, curr_player):
        return None, heuristic_func(board, curr_player)
    
    best_move = None
    best_value = float('-inf')

    for move in board.get_possible_moves(curr_player):
        new_board = play_move(board, curr_player, move)
        _, value = alphabeta_min_basic(new_board, oppo_player, alpha, beta, heuristic_func)
        if value > best_value:
            best_value = value
            best_move = move
            if best_value > alpha:
                alpha = best_value
                if alpha >= beta:
                    return best_move, best_value

    return best_move, best_value
    # raise NotImplementedError

def alphabeta_min_basic(board, curr_player, alpha, beta, heuristic_func):
    """
    Perform Alpha-Beta Pruning for MIN player.
    Return the best move and its minimax value.
    If the board is a terminal state, return None as its best move.

    :param board: the current board
    :param curr_player: the current player
    :param alpha: current alpha value
    :param beta: current beta value
    :param heuristic_func: the heuristic function
    :return the best move and its minimax value.
    """

    oppo_player = get_opponent(curr_player)

    if terminal(board, curr_player):
        return None, heuristic_func(board, oppo_player)
    
    best_move = None
    best_value = float('inf')

    for move in board.get_possible_moves(curr_player):
        new_board = play_move(board, curr_player, move)
        _, value = alphabeta_max_basic(new_board, oppo_player, alpha, beta, heuristic_func)
        if value < best_value:
            best_value = value
            best_move = move
            if best_value < beta:
                beta = best_value
                if alpha >= beta:
                    return best_move, best_value

    return best_move, best_value

    # raise NotImplementedError

def alphabeta_max_limit(board, curr_player, alpha, beta, heuristic_func, depth_limit):
    """
    Perform Alpha-Beta Pruning for MAX player up to the given depth limit.
    Return the best move and its estimated minimax value.
    If the board is a terminal state, return None as its best move.

    :param board: the current board
    :param curr_player: the current player
    :param alpha: current alpha value
    :param beta: current beta value
    :param heuristic_func: the heuristic function
    :param depth_limit: the depth limit
    :return the best move and its estimated minimax value.
    """

    oppo_player = get_opponent(curr_player)

    # If the board is a terminal state
    if terminal(board, curr_player) or depth_limit == 0:
        return None, heuristic_func(board, curr_player)
    
    best_move = None
    best_value = float('-inf')

    for move in board.get_possible_moves(curr_player):
        new_board = play_move(board, curr_player, move)
        _, value = alphabeta_min_limit(new_board, oppo_player, alpha, beta, heuristic_func, depth_limit - 1)
        if value > best_value:
            best_value = value
            best_move = move
            if best_value > alpha:
                alpha = best_value
                if alpha >= beta:
                    return best_move, best_value

    return best_move, best_value


    # raise NotImplementedError

def alphabeta_min_limit(board, curr_player, alpha, beta, heuristic_func, depth_limit):
    """
    Perform Alpha-Beta Pruning for MIN player up to the given depth limit.
    Return the best move and its estimated minimax value.
    If the board is a terminal state, return None as its best move.

    :param board: the current board
    :param curr_player: the current player
    :param alpha: current alpha value
    :param beta: current beta value
    :param heuristic_func: the heuristic function
    :param depth_limit: the depth limit
    :return the best move and its estimated minimax value.
    """

    oppo_player = get_opponent(curr_player)

    if terminal(board, curr_player) or depth_limit == 0:
        return None, heuristic_func(board, oppo_player)
    
    best_move = None
    best_value = float('inf')

    for move in board.get_possible_moves(curr_player):
        new_board = play_move(board, curr_player, move)
        _, value = alphabeta_max_limit(new_board, oppo_player, alpha, beta, heuristic_func, depth_limit - 1)
        if value < best_value:
            best_value = value
            best_move = move
            if best_value < beta:
                beta = best_value
                if alpha >= beta:
                    return best_move, best_value

    return best_move, best_value

    # raise NotImplementedError

def alphabeta_max_limit_caching(board, curr_player, alpha, beta, heuristic_func, depth_limit, cache):
    """
    Perform Alpha-Beta Pruning for MAX player up to the given depth limit and the option of caching states.
    Return the best move and its estimated minimax value.
    If the board is a terminal state, return None as its best move.
    :param board: the current board
    :param curr_player: the current player
    :param alpha: current alpha value
    :param beta: current beta value
    :param heuristic_func: the heuristic function
    :param depth_limit: the depth limit
    :return the best move and its estimated minimax value.
    """
    opponent = get_opponent(curr_player)
    
    if (curr_player, board) in cache:
        c_move, c_value, depth, a, b =  cache[(curr_player, board)]
        if depth >= depth_limit and a <= alpha and b >= beta:
            return c_move, c_value
 
    if terminal(board, curr_player) or depth_limit == 0:
        return None, heuristic_func(board, curr_player)
    
    best_move = None
    best_value = float('-inf')
 
    moves = board.get_possible_moves(curr_player)
    for move in moves:
        next_state = play_move(board, curr_player, move)
        _, value = alphabeta_min_limit_caching(next_state, opponent, alpha, beta, heuristic_func, depth_limit-1, cache)
        if value > best_value:
            best_value = value
            best_move = move
            if best_value > alpha:
                alpha = best_value
                if alpha >= beta:
                    break
    cache[(curr_player, board)] = best_move, best_value, depth_limit, alpha, beta
    return best_move, best_value
        
 
    # raise NotImplementedError
 
def alphabeta_min_limit_caching(board, curr_player, alpha, beta, heuristic_func, depth_limit, cache):
    """
    Perform Alpha-Beta Pruning for MIN player up to the given depth limit and the option of caching states.
    Return the best move and its estimated minimax value.
    If the board is a terminal state, return None as its best move.
    :param board: the current board
    :param curr_player: the current player
    :param alpha: current alpha value
    :param beta: current beta value
    :param heuristic_func: the heuristic function
    :param depth_limit: the depth limit
    :return the best move and its estimated minimax value.
    """
 
    opponent = get_opponent(curr_player)
    
    if (curr_player, board) in cache:
        c_move, c_value, depth, a, b =  cache[(curr_player, board)]
        if depth >= depth_limit and a <= alpha and b >= beta:
            return c_move, c_value
 
    if terminal(board, curr_player) or depth_limit == 0:
        return None, heuristic_func(board, opponent)
    
    best_move = None
    best_value = float('inf')
 
    moves = board.get_possible_moves(curr_player)
    for move in moves:
        next_state = play_move(board, curr_player, move)
        _, value = alphabeta_max_limit_caching(next_state, opponent, alpha, beta, heuristic_func, depth_limit-1, cache)
        if value < best_value:
            best_value = value
            best_move = move
            if best_value < beta:
                beta = best_value
                if alpha >= beta:
                    break
    cache[(curr_player, board)] = best_move, best_value, depth_limit, alpha, beta
    return best_move, best_value

    # raise NotImplementedError


###############################################################################
## DO NOT MODIFY THE CODE BELOW.
###############################################################################

def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Mancala AI")  # First line is the name of this AI
    arguments = input().split(",")

    player = int(arguments[0])  # Player color
    limit = int(arguments[1])  # Depth limit
    caching = int(arguments[2])  # Depth limit
    hfunc = int(arguments[3]) # Heuristic Function

    if (caching == 1): 
        caching = True
        cache = {}
    else: 
        caching = False

    eprint("Running ALPHA-BETA")

    if limit == -1:
        eprint("Depth Limit is OFF")
    else:
        eprint("Depth Limit is ", limit)

    if caching:
        eprint("Caching is ON")
    else:
        eprint("Caching is OFF")

    if hfunc == 0:
        eprint("Using heuristic_basic")
        heuristic_func = heuristic_basic
    else:
        eprint("Using heuristic_advanced")
        heuristic_func = heuristic_advanced

    while True:  # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()

        if status == "FINAL":  # Game is over.
            print()
        else:
            pockets = eval(input())  # Read in the input and turn it into an object
            mancalas = eval(input())  # Read in the input and turn it into an object
            board = Board(pockets, mancalas)

            # Select the move and send it to the manager
            alpha = float("-Inf")
            beta = float("Inf")
            if caching:
                move, value = alphabeta_max_limit_caching(board, player, alpha, beta, heuristic_func, limit, cache)
            elif limit >= 0:
                move, value = alphabeta_max_limit(board, player, alpha, beta, heuristic_func, limit)
            else:
                move, value = alphabeta_max_basic(board, player, alpha, beta, heuristic_func)

            print("{}".format(move))


if __name__ == "__main__":
    run_ai()
