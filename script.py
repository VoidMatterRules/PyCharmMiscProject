import tkinter as tk
from tkinter import messagebox
import numpy as np

ROWS = 6
COLS = 7
CELL_SIZE = 80

class Connect4GUI:
    def __init__(self, root):
        # Initializes the GUI, game state, and sets up the canvas
        self.root = root
        self.root.title("4 Gewinnt")
        self.board = np.full((ROWS, COLS), ' ')
        self.turn = 0
        self.game_over = False

        self.canvas = tk.Canvas(root, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE, bg='blue')
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.click)

        self.draw_board()

        self.is_animating = False
        self.pending_click = None
        self.active_animation = None

    def draw_board(self):
        # Draws the current game board with pieces on the canvas
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x0 = c * CELL_SIZE
                y0 = r * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                self.canvas.create_oval(x0+5, y0+5, x1-5, y1-5, fill=self.get_color(self.board[r][c]))

    def get_color(self, piece):
        # Returns the corresponding color for each piece type
        return {"X": "red", "O": "yellow"}.get(piece, "white")

    def click(self, event):
        # Handles mouse click events to place a piece
        if self.game_over:
            return

        col = event.x // CELL_SIZE
        if col < 0 or col >= COLS or not self.is_valid_location(col):
            return

        if self.is_animating:
            self.skip_animation()
            self.pending_click = event
            return

        row = self.get_next_open_row(col)
        if row is None:
            return

        piece = 'X' if self.turn % 2 == 0 else 'O'
        self.is_animating = True
        self.active_animation = {"col": col, "row": row, "piece": piece, "current_row": 0}
        self.animate_drop()

    def is_valid_location(self, col):
        # Checks if the top cell in the column is empty
        return self.board[0][col] == ' '

    def get_next_open_row(self, col):
        # Returns the lowest empty row in a given column
        for r in range(ROWS - 1, -1, -1):
            if self.board[r][col] == ' ':
                return r
        return None

    def animate_drop(self):
        # Animates a piece dropping down to its position
        if not self.active_animation:
            return

        data = self.active_animation
        col = data["col"]
        target_row = data["row"]
        piece = data["piece"]
        current_row = data["current_row"]

        if current_row > 0:
            self.canvas.create_oval(
                col * CELL_SIZE + 5,
                (current_row - 1) * CELL_SIZE + 5,
                (col + 1) * CELL_SIZE - 5,
                current_row * CELL_SIZE - 5,
                fill="white", outline=""
            )

        self.canvas.create_oval(
            col * CELL_SIZE + 5,
            current_row * CELL_SIZE + 5,
            (col + 1) * CELL_SIZE - 5,
            (current_row + 1) * CELL_SIZE - 5,
            fill=self.get_color(piece)
        )

        if current_row < target_row:
            data["current_row"] += 1
            self.root.after(30, self.animate_drop)
        else:
            self.finish_turn(col, target_row, piece)

    def skip_animation(self):
        # Immediately places the piece and finishes the turn, skipping animation
        if self.active_animation:
            col = self.active_animation["col"]
            row = self.active_animation["row"]
            piece = self.active_animation["piece"]

            # Draw immediately
            self.canvas.create_oval(
                col * CELL_SIZE + 5,
                row * CELL_SIZE + 5,
                (col + 1) * CELL_SIZE - 5,
                (row + 1) * CELL_SIZE - 5,
                fill=self.get_color(piece)
            )
            self.finish_turn(col, row, piece)

    def finish_turn(self, col, row, piece):
        # Completes the player's turn by updating the board and checking game status
        self.board[row][col] = piece
        self.draw_board()
        self.active_animation = None
        self.is_animating = False

        if self.winning_move(piece):
            self.game_over = True
            messagebox.showinfo("Spiel beendet", f"Spieler {piece} gewinnt!")
            self.reset_game()
            return
        elif self.is_draw():
            self.game_over = True
            messagebox.showinfo("Spiel beendet", "Unentschieden!")
            self.reset_game()
            return
        else:
            self.turn += 1

        # Handle any click that occurred during animation
        if self.pending_click is not None:
            next_col = self.pending_click
            self.pending_click = None
            fake_event = type('Event', (object,), {'x': next_col * CELL_SIZE + 1})()
            self.click(fake_event)

    def winning_move(self, piece):
        # Checks for 4 connected pieces in all directions (horizontal, vertical, diagonal)
        for c in range(COLS - 3):
            for r in range(ROWS):
                if all(self.board[r][c + i] == piece for i in range(4)):
                    return True
        for c in range(COLS):
            for r in range(ROWS - 3):
                if all(self.board[r + i][c] == piece for i in range(4)):
                    return True
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if all(self.board[r + i][c + i] == piece for i in range(4)):
                    return True
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if all(self.board[r - i][c + i] == piece for i in range(4)):
                    return True
        return False

    def is_draw(self):
        # Checks if the board is full with no winner
        return all(self.board[0][c] != ' ' for c in range(COLS))

    def reset_game(self):
        # Resets the game state and redraws the board
        self.board = np.full((ROWS, COLS), ' ')
        self.turn = 0
        self.game_over = False
        self.is_animating = False
        self.active_animation = None
        self.pending_click = None
        self.draw_board()

if __name__ == "__main__":
    # Starts the game
    root = tk.Tk()
    game = Connect4GUI(root)
    root.mainloop()
