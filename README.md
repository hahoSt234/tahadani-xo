# 🎮 TAHADANI — 3-Pieces Tic-Tac-Toe with AI

An innovative and strategic twist on the classic Tic-Tac-Toe game, built using **Python** and **Flask**. This project features a unique continuous-movement mechanic and an advanced AI opponent utilizing sophisticated search algorithms.

## 🚀 Live Demo
You can play the game instantly in your browser without installing anything!
🔗 **[hanoo.pythonanywhere.com](http://hanoo.pythonanywhere.com)**

---

## 📌 Game Concept & Rules
This is not your average Tic-Tac-Toe. *TAHADANI* forces players to think ahead and manage their board presence carefully:
* **Max 3 Pieces:** Each player can only have a maximum of 3 pieces on the board at any given time.
* **The 4th Piece Rule:** When you place your 4th piece, your **oldest piece** currently on the board will automatically disappear!
* **Winning Condition:** The first player to form a straight line (horizontal, vertical, or diagonal) with 3 active pieces wins the match.

---

## 🤖 AI & Algorithms Used
The game features a powerful built-in AI capable of playing at different difficulty levels using two main algorithms:
1. **Alpha-Beta Pruning:** An optimized minimax search algorithm that evaluates potential future moves up to a specific depth to make the best tactical decisions.
2. **MCTS (Monte Carlo Tree Search):** A probabilistic heuristic algorithm that runs randomized simulations to build a decision tree, choosing the path with the highest win rate.

---

## 💻 Tech Stack
* **Back-End:** Python & Flask Framework (Handles the game states, AI calculations, and RESTful APIs).
* **Front-End:** HTML5, CSS3, and JavaScript (Provides a modern, fully responsive UI with dynamic visual feedback for piece expiration and AI thinking states).

---

## 🛠️ Local Setup & Installation

If you are a developer and want to run this project locally on your machine, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
   cd your-repo-name
