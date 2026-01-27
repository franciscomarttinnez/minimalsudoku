from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import json

app = Flask(__name__)
app.secret_key = "super-secret-key"

DATABASE = "database.db"

# ─────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────

def get_db():
    conn = sqlite3.connect(
        DATABASE,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn



def init_db():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            user_id INTEGER PRIMARY KEY,
            games_started INTEGER DEFAULT 0,
            games_won INTEGER DEFAULT 0,
            perfect_wins INTEGER DEFAULT 0,
            best_time INTEGER,
            best_score INTEGER,
            total_score INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS games (
            user_id INTEGER PRIMARY KEY,
            difficulty TEXT NOT NULL,
            board TEXT NOT NULL,
            solution TEXT NOT NULL,
            errors INTEGER DEFAULT 0,
            elapsed_time INTEGER DEFAULT 0,
            score INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)

    db.commit()
    db.close()


def get_active_game(user_id):
    db = get_db()
    game = db.execute(
        "SELECT * FROM games WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    db.close()
    return game

# ─────────────────────────────
# VALIDATIONS
# ─────────────────────────────

def is_valid_username(username):
    return 6 <= len(username) <= 20 and username.isalnum()


def is_valid_password(password):
    return 8 <= len(password) <= 16 and password.isalnum()

# ─────────────────────────────
# SUDOKU LOGIC
# ─────────────────────────────

DIFFICULTY_LEVELS = {
    "easy": 40,
    "medium": 32,
    "hard": 25
}


def is_valid(board, row, col, num):
    if num in board[row]:
        return False

    for i in range(9):
        if board[i][col] == num:
            return False

    start_row = (row // 3) * 3
    start_col = (col // 3) * 3

    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False

    return True


def solve_board(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                numbers = list(range(1, 10))
                random.shuffle(numbers)

                for num in numbers:
                    if is_valid(board, row, col, num):
                        board[row][col] = num

                        if solve_board(board):
                            return True

                        board[row][col] = 0

                return False
    return True


def generate_full_board():
    board = [[0 for _ in range(9)] for _ in range(9)]
    solve_board(board)
    return board


def remove_numbers(board, difficulty):
    cells_to_keep = DIFFICULTY_LEVELS[difficulty]
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    while len(cells) > cells_to_keep:
        row, col = cells.pop()
        board[row][col] = 0

    return board


def generate_sudoku(difficulty):
    solution = generate_full_board()
    board = json.loads(json.dumps(solution))
    board = remove_numbers(board, difficulty)
    return board, solution
def is_row_complete(board, row):
    return all(board[row][c] != 0 for c in range(9))


def is_column_complete(board, col):
    return all(board[r][col] != 0 for r in range(9))


def is_block_complete(board, row, col):
    start_row = (row // 3) * 3
    start_col = (col // 3) * 3

    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if board[r][c] == 0:
                return False
    return True

# ─────────────────────────────
# ROUTES — AUTH
# ─────────────────────────────

@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("menu"))

        error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not is_valid_username(username):
            error = "Username must be 6-20 characters and contain only letters and numbers."

        elif not is_valid_password(password):
            error = "Password must be 8-16 characters and contain only letters and numbers."

        elif password != confirm_password:
            error = "Passwords do not match."


        else:
            hashed_password = generate_password_hash(password)
            try:
                db = get_db()
                cursor = db.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_password)
                )

                user_id = cursor.lastrowid

                db.execute(
                    "INSERT INTO stats (user_id) VALUES (?)",
                    (user_id,)
                )

                db.commit()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                error = "Username already exists."
            finally:
                db.close()

    return render_template("register.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ─────────────────────────────
# ROUTES — GAME
# ─────────────────────────────

@app.route("/menu")
def menu():
    if "user_id" not in session:
        return redirect(url_for("login"))

    game = get_active_game(session["user_id"])

    return render_template(
        "menu.html",
        username=session["username"],
        has_active_game=bool(game)
    )

@app.route("/game")
def game():
    if "user_id" not in session:
        return redirect(url_for("login"))

    game = get_active_game(session["user_id"])

    if not game:
        return redirect(url_for("menu"))

    board = json.loads(game["board"])

    return render_template(
        "game.html",
        board=board,
        errors=game["errors"],
        elapsed_time=game["elapsed_time"],
        score=game["score"]
    )


POINTS = {
    "correct_number": 5,
    "complete_row": 20,
    "complete_column": 20,
    "complete_block": 30,
    "win_bonus": 100,
    "error_penalty": -5
}

@app.route("/play", methods=["POST"])
def play():
    if "user_id" not in session:
        return {"status": "error"}

    data = request.get_json()
    row = data["row"]
    col = data["col"]
    value = data["value"]

    db = get_db()
    try:
        game = db.execute(
            "SELECT board, solution, errors, score FROM games WHERE user_id = ?",
            (session["user_id"],)
        ).fetchone()

        board = json.loads(game["board"])
        solution = json.loads(game["solution"])
        errors = game["errors"]
        score = game["score"]

        # ✔ Número correcto
        if solution[row][col] == value:
            board[row][col] = value
            score_delta = POINTS["correct_number"]

            if is_row_complete(board, row):
                score_delta += POINTS["complete_row"]

            if is_column_complete(board, col):
                score_delta += POINTS["complete_column"]

            if is_block_complete(board, row, col):
                score_delta += POINTS["complete_block"]

            completed = all(
                all(cell != 0 for cell in r)
                for r in board
            )

            if completed:
                score_delta += POINTS["win_bonus"]

                db.execute(
                    "DELETE FROM games WHERE user_id = ?",
                    (session["user_id"],)
                )

                db.execute("""
                    UPDATE stats
                    SET
                        games_won = games_won + 1,
                        total_score = total_score + ?,
                        best_score = MAX(COALESCE(best_score, 0), ?)
                    WHERE user_id = ?
                """, (
                    score_delta,
                    score_delta,
                    session["user_id"]
                ))

                db.commit()
                return {"status": "win", "score": score_delta}

            db.execute("""
                UPDATE games
                SET board = ?, score = score + ?
                WHERE user_id = ?
            """, (
                json.dumps(board),
                score_delta,
                session["user_id"]
            ))

            db.commit()
            return {"status": "ok", "score": score_delta}

        # ❌ Error
        errors += 1
        score += POINTS["error_penalty"]

        if errors >= 3:
            db.execute(
                "DELETE FROM games WHERE user_id = ?",
                (session["user_id"],)
            )
            db.commit()
            return {"status": "game_over"}

        db.execute("""
            UPDATE games
            SET errors = ?, score = ?
            WHERE user_id = ?
        """, (
            errors,
            score,
            session["user_id"]
        ))

        db.commit()
        return {"status": "error", "errors": errors}

    finally:
        db.close()


@app.route("/new-game/<difficulty>")
def new_game(difficulty):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if difficulty not in DIFFICULTY_LEVELS:
        return redirect(url_for("menu"))

    board, solution = generate_sudoku(difficulty)

    db = get_db()
    try:
        db.execute(
            "DELETE FROM games WHERE user_id = ?",
            (session["user_id"],)
        )

        db.execute("""
            INSERT INTO games (user_id, difficulty, board, solution)
            VALUES (?, ?, ?, ?)
        """, (
            session["user_id"],
            difficulty,
            json.dumps(board),
            json.dumps(solution)
        ))

        db.execute("""
            UPDATE stats
            SET games_started = games_started + 1
            WHERE user_id = ?
        """, (session["user_id"],))

        db.commit()
    finally:
        db.close()

    return redirect(url_for("game"))

@app.route("/stats")
def stats():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    user_stats = db.execute(
        "SELECT * FROM stats WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()
    db.close()

    win_rate = 0
    if user_stats["games_started"] > 0:
        win_rate = round(
            (user_stats["games_won"] / user_stats["games_started"]) * 100,
            1
        )

    return render_template(
        "stats.html",
        stats=user_stats,
        win_rate=win_rate
    )
@app.route("/finish-game", methods=["POST"])
def finish_game():
    if "user_id" not in session:
        return {"status": "error"}

    data = request.get_json()
    elapsed_time = data["elapsed_time"]

    db = get_db()
    try:
        db.execute("""
            UPDATE stats
            SET
                best_time =
                    CASE
                        WHEN best_time IS NULL OR ? < best_time THEN ?
                        ELSE best_time
                    END
            WHERE user_id = ?
        """, (
            elapsed_time,
            elapsed_time,
            session["user_id"]
        ))
        db.commit()
    finally:
        db.close()

    return {"status": "ok"}

# ─────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
