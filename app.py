import math
import random
from flask import Flask, request, jsonify, render_template
from game import GameState, alpha_beta, mcts_search

app = Flask(__name__)

game = GameState()
game_cfg = {
    "mode": "hva",
    "humanSide": "X",
    "aiType": "alphabeta",
    "diff": "k5",
    "avaX": "alphabeta",
    "avaO": "mcts",
    "avaDx": "k5",
    "avaDo": "k5",
}

DEPTH_MAP = {"k2": 2, "k5": 5, "k10": 10}

def board_flat(state):
    return [state.board[i][j] for i in range(3) for j in range(3)]

def history_flat(state, player):
    return [r * 3 + c for r, c in state.get_history(player)]

def get_win_line_flat(state, player):
    b = state.board
    lines = [
        [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)],
    ]
    for line in lines:
        if all(b[r][c] == player for r, c in line):
            return [r * 3 + c for r, c in line]
    return None

def make_response(state, ai_move=None, last_move_player=None, last_move=None):
    winner = state.get_winner()
    win_line = get_win_line_flat(state, winner) if winner else None
    return jsonify({
        "board":            board_flat(state),
        "current_player":   state.current_player,
        "x_history":        history_flat(state, 'X'),
        "o_history":        history_flat(state, 'O'),
        "winner":           winner,
        "win_line":         win_line,
        "ai_move":          ai_move,
        "last_move_player": last_move_player,
        "last_move":        last_move,
    })

def pick_ai_move(state, player, ai_type, depth_key):
    depth = DEPTH_MAP.get(depth_key, 5)
    legal = state.get_legal_moves()
    if not legal:
        return None
    if ai_type == "alphabeta":
        _, move = alpha_beta(state, depth, -math.inf, math.inf, True, player)
        return move
    elif ai_type == "mcts":
        return mcts_search(state, simulations=200)
    else:
        return random.choice(legal)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/reset", methods=["POST"])
def reset():
    global game, game_cfg
    data = request.json or {}
    for key in game_cfg:
        if key in data:
            game_cfg[key] = data[key]
    game = GameState()

    # لو الـ AI يبدأ أول (اللاعب اختار O)، خليه يحرك
    ai_side = 'O' if game_cfg["humanSide"] == 'X' else 'X'
    ai_move_flat = None
    if game_cfg["mode"] == "hva" and game.current_player == ai_side:
        ai_rc = pick_ai_move(game, ai_side, game_cfg["aiType"], game_cfg["diff"])
        if ai_rc:
            r, c = ai_rc
            ai_move_flat = r * 3 + c
            game = game.apply_move(ai_rc)

    return make_response(game, ai_move=ai_move_flat)

@app.route("/move", methods=["POST"])
def move():
    global game
    data = request.json or {}
    row = data.get("row", -1)
    col = data.get("col", -1)
    ai_move_flat = None

    if not game.is_terminal():
        # حركة اللاعب
        if row >= 0 and col >= 0:
            move_rc = (row, col)
            if move_rc not in game.get_legal_moves():
                return jsonify({"error": "Invalid move"}), 400
            game = game.apply_move(move_rc)

        # حركة الـ AI
        ai_side = 'O' if game_cfg["humanSide"] == 'X' else 'X'
        if not game.is_terminal() and game.current_player == ai_side:
            ai_rc = pick_ai_move(game, ai_side, game_cfg["aiType"], game_cfg["diff"])
            if ai_rc:
                ar, ac = ai_rc
                ai_move_flat = ar * 3 + ac
                game = game.apply_move(ai_rc)

    return make_response(game, ai_move=ai_move_flat)

@app.route("/ava_step", methods=["POST"])
def ava_step():
    global game
    if game.is_terminal():
        return make_response(game)

    player    = game.current_player
    ai_type   = game_cfg["avaX"] if player == 'X' else game_cfg["avaO"]
    depth_key = game_cfg["avaDx"] if player == 'X' else game_cfg["avaDo"]

    move_rc   = pick_ai_move(game, player, ai_type, depth_key)
    last_flat = None
    if move_rc:
        r, c      = move_rc
        last_flat = r * 3 + c
        game      = game.apply_move(move_rc)

    return make_response(game, last_move_player=player, last_move=last_flat)

if __name__ == "__main__":
    app.run(debug=True)