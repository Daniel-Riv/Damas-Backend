from input import *
from output import print_table
from position import Position
from math import inf
from time import time
from copy import deepcopy
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from schemas import Move, ValidMoves, Machin
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

# MIN MAX simple implementation

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def min_max(position, depth, max_player):
    if depth == 0 or position.get_game_end():
        return position.evaluate_state()
    if max_player:
        max_evaluation = -inf
        for child in position.get_next_moves():
            eval = min_max(child, depth - 1, False)
            max_evaluation = max(max_evaluation, eval)
        position.set_evaluation(max_evaluation)
        return max_evaluation
    else:
        min_evaluation = inf
        for child in position.get_next_moves():
            eval = min_max(child, depth - 1, True)
            min_evaluation = min(min_evaluation, eval)
        position.set_evaluation(min_evaluation)
        return min_evaluation

# MIN MAX with ALPHA-BETA pruning


def alpha_beta(position, depth, alpha, beta, max_player, forced_caputure):
    if depth == 0 or position.get_game_end():
        return position.evaluate_state()
    if max_player:
        max_evaluation = -inf
        for child in position.get_next_moves(forced_caputure):
            eval = alpha_beta(child, depth - 1, alpha,
                              beta, False, forced_caputure)
            max_evaluation = max(max_evaluation, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                # print("pruning max")
                break
        position.set_evaluation(max_evaluation)
        return max_evaluation
    else:
        min_evaluation = inf
        for child in position.get_next_moves(forced_caputure):
            eval = alpha_beta(child, depth - 1, alpha,
                              beta, True, forced_caputure)
            min_evaluation = min(min_evaluation, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                # print("pruning min")
                break
        position.set_evaluation(min_evaluation)
        return min_evaluation

# Alpha beta pruning minmax that calls a different function. It can be changed to take the function as a parameter


def alpha_beta_ending(position, depth, alpha, beta, max_player, forced_caputure):
    if depth == 0 or position.get_game_end():
        return position.evaluate_state_ending()
    if max_player:
        max_evaluation = -inf
        for child in position.get_next_moves(forced_caputure):
            eval = alpha_beta_ending(
                child, depth - 1, alpha, beta, False, forced_caputure)
            max_evaluation = max(max_evaluation, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                # print("pruning max")
                break
        position.set_evaluation(max_evaluation)
        return max_evaluation
    else:
        min_evaluation = inf
        for child in position.get_next_moves(forced_caputure):
            eval = alpha_beta_ending(
                child, depth - 1, alpha, beta, True, forced_caputure)
            min_evaluation = min(min_evaluation, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                # print("pruning min")
                break
        position.set_evaluation(min_evaluation)
        return min_evaluation


def determine_dynamic_depth(time_previous_move, depth, forced_caputure, num_moves):
    if forced_caputure:
        if time_previous_move < 0.5 and num_moves <= 6:
            return depth + 1
        if depth > 6 and (time_previous_move > 4 or num_moves > 6):
            return depth - 1
        return depth
    else:
        if time_previous_move < 0.5:
            return depth + 1
        if time_previous_move > 4.5:
            return depth - 1
        return depth


def ending_conditions(position, figure_counter, forced_caputure):
    moves = position.get_next_moves(forced_caputure)

    num_figures = position.count_pieces()
    if num_figures[0] == 0:
        return "FeliCidades las fichas negras han ganado!"
    if num_figures[1] == 0:
        return "FeliCidades las fichas blancas han ganado!"
    if num_figures[0] + num_figures[1] == figure_counter[0]:
        figure_counter[1] += 1
        if figure_counter[1] == 50:
            return "Tie!"
    else:
        figure_counter[0] = num_figures[0] + num_figures[1]
        figure_counter[1] = 0
    if not moves:
        return "There are no possible moves left! Game is finished!"

    return False

def alpha_to_index(coord: str):
    letter_to_num = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    letter, number = coord[0].lower(), int(coord[1]) - 1
    return letter_to_num[letter], number

@app.get("/board")
async def board():
    table = [['.', 'c', '.', 'c', '.', 'c', '.', 'c'],
             ['c', '.', 'c', '.', 'c', '.', 'c', '.'],
             ['.', 'c', '.', 'c', '.', 'c', '.', 'c'],
             ['.', '.', '.', '.', '.', '.', '.', '.'],
             ['.', '.', '.', '.', '.', '.', '.', '.'],
             ['b', '.', 'b', '.', 'b', '.', 'b', '.'],
             ['.', 'b', '.', 'b', '.', 'b', '.', 'b'],
             ['b', '.', 'b', '.', 'b', '.', 'b', '.']]
    position = Position(table,True)
    return position.get_table()

@app.post("/main")
async def main(play: Move):
    coord=play.name
    coord2=play.move
    table=play.position

    forced = "no"
    forcedM="yes"
    forced_caputure = input_forced_moves(forced)
    forced_captureM= input_forced_moves(forcedM)
    position = Position(table, True)
    time_previous_move = 4.5
    depth = 6
    without_capture = [0, 0]

    
    if ending_conditions(position, without_capture, forced_caputure):
        return position.get_table()

    available_pieces = position.find_capturing_moves()
    if forced_caputure:
        piece = input_choose_piece(position, coord, available_pieces)
    else:
        piece = input_choose_piece(position, coord)
    
    if not piece:
        return "Goodbye!"
    if isinstance (piece,str):
        return piece
    valid_moves = position.find_valid_moves_for_piece(
        piece, forced_caputure)
    new_position = input_choose_field(valid_moves,coord2)
    if not new_position:
        return "Taknuto maknuto! Doviđenja!"
    previous_table = deepcopy(position.get_table())
    position = position.play_move(piece, new_position)
    differences = position.find_move_played(previous_table)
    if ending_conditions(position, without_capture, forced_caputure):
        return position.get_table()
    num_moves = len(position.get_next_moves())
    depth = determine_dynamic_depth(
        time_previous_move, depth, forced_caputure, num_moves)
    previous_table = deepcopy(position.get_table())
    print("THINKING.....................................")
    t1 = time()
    num_figures = position.count_pieces()
    if num_figures[0] + num_figures[1] > 6:
        alpha_beta(position, depth, -inf, inf, True, forced_captureM)
        position = max(position.get_next_moves())
    else:
        alpha_beta_ending(position, 20, -inf, inf, True, forced_captureM)
        position = max(position.get_next_moves())
    t2 = time()
    time_previous_move = t2 - t1
    differences = position.find_move_played(previous_table)
    return position.get_table()

@app.post("/valid_moves")
async def valid_moves(valid: ValidMoves):
    coord=valid.name
    table=valid.position

    forced = "no"
    forced_caputure = input_forced_moves(forced)
    position = Position(table, True)

    depth = 6
    without_capture = [0, 0]

    
    if ending_conditions(position, without_capture, forced_caputure):
        return ending_conditions(position, without_capture, forced_caputure)


    available_pieces = position.find_capturing_moves()
    if forced_caputure:
        piece = input_choose_piece(position, coord, available_pieces)
    else:
        piece = input_choose_piece(position, coord)

    if not piece:
        return "Goodbye!"
    if isinstance (piece,str):
        return piece
    valid_moves = position.find_valid_moves_for_piece(
        piece, forced_caputure)
    return (valid_moves, position.get_table())

@app.get("/rendir")
async def rendir():
    message= "Gracias por jugar"
    table = [['.', 'c', '.', 'c', '.', 'c', '.', 'c'],
             ['c', '.', 'c', '.', 'c', '.', 'c', '.'],
             ['.', 'c', '.', 'c', '.', 'c', '.', 'c'],
             ['.', '.', '.', '.', '.', '.', '.', '.'],
             ['.', '.', '.', '.', '.', '.', '.', '.'],
             ['b', '.', 'b', '.', 'b', '.', 'b', '.'],
             ['.', 'b', '.', 'b', '.', 'b', '.', 'b'],
             ['b', '.', 'b', '.', 'b', '.', 'b', '.']]
    position = Position(table,True)
    return (message, position.get_table())

@app.post("/player")
async def player(move: Move):
    coord=move.name
    coord2= move.move
    table=move.position

    forced = "no"
    forced_caputure = input_forced_moves(forced)
    position = Position(table, True)
    without_capture = [0, 0]

    
    if ending_conditions(position, without_capture, forced_caputure):
        return ending_conditions(position, without_capture, forced_caputure)

    available_pieces = position.find_capturing_moves()
   
    if forced_caputure:
        piece = input_choose_piece(position, coord, available_pieces)
    else:
        piece = input_choose_piece(position, coord)
    
    if not piece:
        return "Goodbye!"
    if isinstance (piece,str):
        return piece
    valid_moves = position.find_valid_moves_for_piece(
        piece, forced_caputure)
    new_position = input_choose_field(valid_moves,coord2)
    if not new_position:
        return "Taknuto maknuto! Doviđenja!"
    previous_table = deepcopy(position.get_table())
    position = position.play_move(piece, new_position)
    differences = position.find_move_played(previous_table)
    if ending_conditions(position, without_capture, forced_caputure):
        return position.get_table()
    return position.get_table()


@app.post("/player2")
async def player2(move: Move):
    coord=move.name
    coord2= move.move
    table=move.position

    forced = "no"
    forced_caputure = input_forced_moves(forced)
    position = Position(table, False)
    without_capture = [0, 0]

    
    if ending_conditions(position, without_capture, forced_caputure):
        return ending_conditions(position, without_capture, forced_caputure)

    available_pieces = position.find_capturing_moves()
    if forced_caputure:
        piece = input_choose_piece(position, coord, available_pieces)
    else:
        piece = input_choose_piece(position, coord)
    
    if not piece:
        return "Goodbye!"
    if isinstance (piece,str):
        return piece
    valid_moves = position.find_valid_moves_for_piece(
        piece, forced_caputure)
    new_position = input_choose_field(valid_moves,coord2)
    if not new_position:
        return "Taknuto maknuto! Doviđenja!"
    previous_table = deepcopy(position.get_table())
    position = position.play_move(piece, new_position)
    differences = position.find_move_played(previous_table)
    if ending_conditions(position, without_capture, forced_caputure):
        return position.get_table()
    return position.get_table()

@app.post("/valid_moves_player2")
async def valid_moves_player2(valid: ValidMoves):
    coord=valid.name
    table=valid.position    
    forced = "no"
    forced_caputure = input_forced_moves(forced)
    position = Position(table, False)

    without_capture = [0, 0]

    
    if ending_conditions(position, without_capture, forced_caputure):
        return position.get_table()

    available_pieces = position.find_capturing_moves()
    if forced_caputure:
        piece = input_choose_piece(position, coord, available_pieces)
    else:
        piece = input_choose_piece(position, coord)

    if not piece:
        return "Goodbye!"
    if isinstance (piece,str):
        return piece
    valid_moves = position.find_valid_moves_for_piece(
        piece, forced_caputure)
    return (valid_moves, position.get_table())

@app.post("/machine")
async def machine(board: Machin):
    table=board.position

    forced = "no"
    forcedM= "yes"
    forced_caputure = input_forced_moves(forced)
    forced_captureM= input_forced_moves(forcedM)
    position = Position(table, True)
    time_previous_move = 4.5
    depth = 6
    without_capture = [0, 0]

    
    if ending_conditions(position, without_capture, forced_caputure):
        return ending_conditions(position, without_capture, forced_caputure)
    
    previous_table = deepcopy(position.get_table())
    t1 = time()
    num_figures = position.count_pieces()
    if num_figures[0] + num_figures[1] > 6:
        alpha_beta(position, depth, -inf, inf, True,forced_caputure)
        position = max(position.get_next_moves())
    else:
        alpha_beta_ending(position, 20, -inf, inf, True, forced_caputure)
        position = max(position.get_next_moves())
    t2 = time()
    time_previous_move = t2 - t1
    differences = position.find_move_played(previous_table)

    previous_table = deepcopy(position.get_table())
    t3 = time()
    num_figures = position.count_pieces()
    if num_figures[0] + num_figures[1] > 6:
        alpha_beta(position, depth, -inf, inf, True, forced_caputure)
        position = max(position.get_next_moves())
    else:
        alpha_beta_ending(position, 20, -inf, inf, True, forced_caputure)
        position = max(position.get_next_moves())
    t4 = time()
    time_previous_move = t4 - t3
    differences = position.find_move_played(previous_table)
    return position.get_table()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), log_level="info")