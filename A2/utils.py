###############################################################################
# This file contains helper functions and the heuristic functions
# for our AI agents to play the Mancala game.
#
# CSC 384 Fall 2023 Assignment 2
# version 1.0
###############################################################################

import sys

import mancala_game

###############################################################################
### DO NOT MODIFY THE CODE BELOW

### Global Constants ###
TOP = 0
BOTTOM = 1

### Errors ###
class InvalidMoveError(RuntimeError):
    pass

class AiTimeoutError(RuntimeError):
    pass

### Functions ###
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_opponent(player):
    if player == BOTTOM:
        return TOP
    return BOTTOM

### DO NOT MODIFY THE CODE ABOVE
###############################################################################


def heuristic_basic(board, player):
    """
    Compute the heuristic value of the current board for the current player 
    based on the basic heuristic function.

    :param board: the current board.
    :param player: the current player.
    :return: an estimated utility of the current board for the current player.
    """

    mancalas = board.mancalas
    curr_player_m = mancalas[player]
    oppo_player_m = mancalas[get_opponent(player)]
    return curr_player_m - oppo_player_m
    # raise NotImplementedError


def heuristic_advanced(board, player): 
    """
    Compute the heuristic value of the current board for the current player
    based on the advanced heuristic function.

    :param board: the current board object.
    :param player: the current player.
    :return: an estimated heuristic value of the current board for the current player.
    """

    curr_p = board.pockets[player]
    oppo_p = board.pockets[get_opponent(player)]

    mancalas = board.mancalas
    curr_player_m = mancalas[player]
    oppo_player_m = mancalas[get_opponent(player)]

    # Terminal heu
    if sum(curr_p) == 0:
        return curr_player_m - (oppo_player_m + sum(oppo_p))
    elif sum(oppo_p) == 0:
        return (curr_player_m + sum(curr_p)) - (oppo_player_m)
    else:
    # Check capture:
        # Easier version
        # return heuristic_basic(board, player) + sum(curr_p) - sum(oppo_p)
        # Complicated version
        total = sum(curr_p) + sum(oppo_p) + curr_player_m + oppo_player_m
        next_moves = board.get_possible_moves(player)
        if sum(curr_p) + sum(oppo_p) < total * 2 // 3: # Mid-game heu
            if count_empty(board, get_opponent(player)) >= count_empty(board, player) and curr_p[next_moves[-1]] > len(curr_p):
                if capture_exist(board, player):
                    return heuristic_basic(board, player) + curr_p[next_moves[-1]]
            
            max_heu = heuristic_basic(board, player)
            for move in next_moves:
                next_state = mancala_game.play_move(board, player, move)
                diff = next_state.mancalas[player] - curr_player_m
                max_heu = max(max_heu, diff)
            return heuristic_basic(board, player) + max_heu
        else: # Start-game heu
            for i in range(len(curr_p)):
                oppo = oppo_p[i]
                curr = curr_p[i]
                if oppo == 0 and curr != 0:
                    for j in range(i,len(oppo_p)):
                        if will_drop(board, get_opponent(player), j, i): # Can capture
                            next_step = mancala_game.play_move(board, player, i)
                            return heuristic_basic(next_step, player) + max(curr_p)
            return heuristic_basic(mancala_game.play_move(board, player, next_moves[0]), player) + max(curr_p)


    # raise NotImplementedError

######### Helper function ###########
def will_drop(board, player, stone_idx, empty_idx):
    bottom_pocket = board.pockets[player]
    return stone_idx + bottom_pocket[stone_idx] == empty_idx

def count_empty(board, player):
    count = 0
    for pocket in board.pockets[player]:
        if pocket == 0:
            count += 1
    return count

def capture_exist(board, player):
    curr_p = board.pockets[player]
    oppo_p = board.pockets[get_opponent(player)]
    for i in range(len(curr_p)):
                oppo = oppo_p[i]
                curr = curr_p[i]
                if oppo == 0 and curr != 0:
                    for j in range(i,len(oppo_p)):
                        if will_drop(board, get_opponent(player), j, i): # Can capture
                            return True
    return False
    