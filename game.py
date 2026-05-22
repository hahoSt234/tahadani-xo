import math
import random
import time
from copy import deepcopy


class GameState:
    def __init__(self, board=None, current_player='X', x_history=None, o_history=None):
        self.board = board if board else [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = current_player
        self.x_history = x_history[:] if x_history else []
        self.o_history = o_history[:] if o_history else []

    def clone(self):
        return GameState(
            board=deepcopy(self.board),
            current_player=self.current_player,
            x_history=self.x_history[:],
            o_history=self.o_history[:]
        )

    def print_board(self):
        print("\n-------------")
        for i in range(3):
            print("|", end=" ")
            for j in range(3):
                print(self.board[i][j], end=" | ")
            print("\n-------------")

    def get_history(self, player):
        return self.x_history if player == 'X' else self.o_history

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def get_legal_moves(self):
        moves = []
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == ' ':
                    moves.append((i, j))
        return moves

    def apply_move(self, move):
        row, col = move
        if self.board[row][col] != ' ':
            raise ValueError("Invalid move: cell is not empty.")

        player = self.current_player
        new_state = self.clone()

        new_state.board[row][col] = player
        history = new_state.get_history(player)
        history.append((row, col))

        if len(history) > 3:
            old_row, old_col = history.pop(0)
            new_state.board[old_row][old_col] = ' '

        new_state.switch_player()
        return new_state

    def check_winner(self, player):
        b = self.board

        for i in range(3):
            if all(b[i][j] == player for j in range(3)):
                return True

        for j in range(3):
            if all(b[i][j] == player for i in range(3)):
                return True

        if b[0][0] == b[1][1] == b[2][2] == player:
            return True

        if b[0][2] == b[1][1] == b[2][0] == player:
            return True

        return False

    def is_terminal(self):
        return self.check_winner('X') or self.check_winner('O')

    def get_winner(self):
        if self.check_winner('X'):
            return 'X'
        if self.check_winner('O'):
            return 'O'
        return None


def evaluate_line(line, player):
    opponent = 'O' if player == 'X' else 'X'
    player_count = line.count(player)
    opponent_count = line.count(opponent)
    empty_count = line.count(' ')

    if player_count == 3:
        return 100
    if opponent_count == 3:
        return -100

    if player_count == 2 and empty_count == 1:
        return 10
    if opponent_count == 2 and empty_count == 1:
        return -10

    if player_count == 1 and empty_count == 2:
        return 2
    if opponent_count == 1 and empty_count == 2:
        return -2

    return 0


def heuristic(state, maximizing_player='X'):
    opponent = 'O' if maximizing_player == 'X' else 'X'

    if state.check_winner(maximizing_player):
        return 1000
    if state.check_winner(opponent):
        return -1000

    score = 0
    b = state.board

    lines = []

    for i in range(3):
        lines.append([b[i][0], b[i][1], b[i][2]])

    for j in range(3):
        lines.append([b[0][j], b[1][j], b[2][j]])

    lines.append([b[0][0], b[1][1], b[2][2]])
    lines.append([b[0][2], b[1][1], b[2][0]])

    for line in lines:
        score += evaluate_line(line, maximizing_player)

    center = b[1][1]
    if center == maximizing_player:
        score += 3
    elif center == opponent:
        score -= 3

    return score


def alpha_beta(state, depth, alpha, beta, maximizing, maximizing_player='X'):
    if depth == 0 or state.is_terminal():
        return heuristic(state, maximizing_player), None

    legal_moves = state.get_legal_moves()
    if not legal_moves:
        return heuristic(state, maximizing_player), None

    if maximizing:
        max_eval = -math.inf
        best_move = None
        for move in legal_moves:
            child = state.apply_move(move)
            eval_score, _ = alpha_beta(child, depth - 1, alpha, beta, False, maximizing_player)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        best_move = None
        for move in legal_moves:
            child = state.apply_move(move)
            eval_score, _ = alpha_beta(child, depth - 1, alpha, beta, True, maximizing_player)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move


class MCTSNode:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.untried_moves = state.get_legal_moves()
        self.visits = 0
        self.wins = 0.0

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c_param=1.41):
        best_score = -math.inf
        best_node = None

        for child in self.children:
            if child.visits == 0:
                score = math.inf
            else:
                exploitation = child.wins / child.visits
                exploration = c_param * math.sqrt(math.log(self.visits) / child.visits)
                score = exploitation + exploration

            if score > best_score:
                best_score = score
                best_node = child

        return best_node

    def expand(self):
        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)
        new_state = self.state.apply_move(move)
        child_node = MCTSNode(new_state, parent=self, move=move)
        self.children.append(child_node)
        return child_node

    def rollout(self, root_player):
        current_state = self.state.clone()
        max_steps = 30
        steps = 0

        while not current_state.is_terminal() and steps < max_steps:
            legal_moves = current_state.get_legal_moves()
            if not legal_moves:
                break
            move = random.choice(legal_moves)
            current_state = current_state.apply_move(move)
            steps += 1

        winner = current_state.get_winner()
        if winner == root_player:
            return 1
        elif winner is None:
            return 0.5
        else:
            return 0

    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)


def mcts_search(state, simulations=300, c_param=1.41):
    root_player = state.current_player
    root = MCTSNode(state)

    for _ in range(simulations):
        node = root

        while node.is_fully_expanded() and node.children:
            node = node.best_child(c_param)

        if not node.state.is_terminal() and node.untried_moves:
            node = node.expand()

        result = node.rollout(root_player)

        node.backpropagate(result)

    best_move = None
    best_visits = -1
    for child in root.children:
        if child.visits > best_visits:
            best_visits = child.visits
            best_move = child.move

    return best_move


def get_human_move(state):
    while True:
        raw = input("Enter your move as 'row col' (0-2 0-2): ").strip()
        parts = raw.split()
        if len(parts) != 2:
            print("Invalid input. Please enter two numbers like: 1 2")
            continue

        try:
            row, col = int(parts[0]), int(parts[1])
        except ValueError:
            print("Invalid input. Row and column must be integers.")
            continue

        if not (0 <= row <= 2 and 0 <= col <= 2):
            print("Invalid move. Row and column must be between 0 and 2.")
            continue

        move = (row, col)
        if move not in state.get_legal_moves():
            print("Invalid move. Cell is not available.")
            continue

        return move


# ──────────────────────────────────────────────
# TIME LIMIT CONSTANT  (20 minutes = 1200 seconds)
# ──────────────────────────────────────────────
TIME_LIMIT = 20 * 60   # 1200 seconds


def play_human_vs_ai(human_side='X', ai_type='alphabeta', ai_depth=5, mcts_sims=300):
    """
    Play a game where a human faces an AI agent.

    Parameters:
        human_side  : 'X' to go first, 'O' to go second
        ai_type     : 'alphabeta', 'mcts', or 'random'
        ai_depth    : search depth for Alpha-Beta (ignored for MCTS/random)
        mcts_sims   : number of simulations for MCTS (ignored for Alpha-Beta/random)
    """
    ai_side = 'O' if human_side == 'X' else 'X'

    print("\n=== 3-Pieces Tic-Tac-Toe: Human vs AI ===")
    print(f"  You are playing as : {human_side}")
    print(f"  AI is playing as   : {ai_side}  ({ai_type})")
    print(f"  Time limit         : 20 minutes")
    print("\nRules: Each player may only have 3 pieces on the board at once.")
    print("       Placing a 4th piece removes your oldest one.")
    print("       First player to get 3 in a row wins.\n")

    state = GameState()
    move_count = 0
    start_time = time.time()

    state.print_board()

    while not state.is_terminal():
        current = state.current_player

        # ── تعديل: فحص الوقت في كل دورة ──
        elapsed = time.time() - start_time
        remaining = TIME_LIMIT - elapsed
        if remaining <= 0:
            print(f"\n⏰ Time's up! 20-minute limit reached.")
            break
        print(f"  ⏱  Time remaining: {int(remaining // 60)}m {int(remaining % 60)}s")

        if current == human_side:
            print(f"\n--- Your turn ({human_side}) ---")
            history = state.get_history(human_side)
            if history:
                print(f"  Your pieces on board: {history}")
                if len(history) == 3:
                    print(f"  WARNING: Playing will remove your oldest piece at {history[0]}")
            move = get_human_move(state)
        else:
            print(f"\n--- AI's turn ({ai_side}) ---")
            print("  Thinking...", end="", flush=True)
            t0 = time.time()
            if ai_type == 'alphabeta':
                _, move = alpha_beta(state, ai_depth, -math.inf, math.inf, True, ai_side)
            elif ai_type == 'mcts':
                move = mcts_search(state, simulations=mcts_sims)
            else:
                move = random.choice(state.get_legal_moves())
            elapsed_move = time.time() - t0
            print(f"\r  AI plays: {move}  ({elapsed_move:.2f}s)")

        if move is None:
            print("No move available. Stopping.")
            break

        state = state.apply_move(move)
        move_count += 1
        state.print_board()

    winner = state.get_winner()
    total_time = time.time() - start_time
    print("\n" + "=" * 40)
    if winner == human_side:
        print("  Congratulations — YOU WIN!")
    elif winner == ai_side:
        print("  AI wins. Better luck next time!")
    else:
        print("  No winner / game stopped.")
    print(f"  Total moves : {move_count}")
    print(f"  Total time  : {total_time:.1f}s")
    print("=" * 40)

    return winner, move_count


def play_ai_vs_ai(player_x_type='alphabeta', player_o_type='mcts',
                  depth_x=5, depth_o=5, mcts_sim_x=300, mcts_sim_o=300,
                  show_board=True):
    state = GameState()
    move_count = 0
    start_time = time.time()

    if show_board:
        print("\n=== New Game Started ===")
        print(f"  Time limit: 20 minutes")
        state.print_board()

    while not state.is_terminal():
        current = state.current_player

        # ── تعديل: فحص الوقت بدل فحص عدد الحركات ──
        if time.time() - start_time >= TIME_LIMIT:
            print("⏰ Game stopped: 20-minute time limit reached.")
            break

        if current == 'X':
            if player_x_type == 'alphabeta':
                _, move = alpha_beta(state, depth_x, -math.inf, math.inf, True, 'X')
            elif player_x_type == 'mcts':
                move = mcts_search(state, simulations=mcts_sim_x)
            else:
                move = random.choice(state.get_legal_moves())
        else:
            if player_o_type == 'alphabeta':
                _, move = alpha_beta(state, depth_o, -math.inf, math.inf, True, 'O')
            elif player_o_type == 'mcts':
                move = mcts_search(state, simulations=mcts_sim_o)
            else:
                move = random.choice(state.get_legal_moves())

        if move is None:
            break

        print(f"\nPlayer {current} plays: {move}")
        state = state.apply_move(move)
        move_count += 1

        if show_board:
            state.print_board()

    end_time = time.time()
    winner = state.get_winner()

    if winner:
        print(f"\nWinner: {winner}")
    else:
        print("\nNo winner / stopped.")

    print(f"Total moves: {move_count}")
    print(f"Total time: {end_time - start_time:.4f} seconds")

    return winner, move_count, end_time - start_time


def run_experiments():
    print("\n==============================")
    print("Experiment 1: AlphaBeta vs AlphaBeta")
    print("==============================")
    play_ai_vs_ai(player_x_type='alphabeta', player_o_type='alphabeta', depth_x=2, depth_o=5)

    print("\n==============================")
    print("Experiment 2: AlphaBeta vs MCTS")
    print("==============================")
    play_ai_vs_ai(player_x_type='alphabeta', player_o_type='mcts', depth_x=10, mcts_sim_o=300)

    print("\n==============================")
    print("Experiment 3: MCTS vs MCTS")
    print("==============================")
    play_ai_vs_ai(player_x_type='mcts', player_o_type='mcts', mcts_sim_x=300, mcts_sim_o=300)


def main():
    while True:
        print("\n===== 3-Pieces Tic-Tac-Toe =====")
        print("1. AlphaBeta vs AlphaBeta")
        print("2. AlphaBeta vs MCTS")
        print("3. MCTS vs MCTS")
        print("4. Run all experiments")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            depth_x = int(input("Enter depth for X (2 / 5 / 10): "))
            depth_o = int(input("Enter depth for O (2 / 5 / 10): "))
            play_ai_vs_ai('alphabeta', 'alphabeta', depth_x=depth_x, depth_o=depth_o)

        elif choice == '2':
            depth_x = int(input("Enter AlphaBeta depth for X (2 / 5 / 10): "))
            sims = int(input("Enter MCTS simulations for O (e.g. 200 or 300): "))
            play_ai_vs_ai('alphabeta', 'mcts', depth_x=depth_x, mcts_sim_o=sims)

        elif choice == '3':
            sims_x = int(input("Enter MCTS simulations for X: "))
            sims_o = int(input("Enter MCTS simulations for O: "))
            play_ai_vs_ai('mcts', 'mcts', mcts_sim_x=sims_x, mcts_sim_o=sims_o)

        elif choice == '4':
            run_experiments()

        elif choice == '5':
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()