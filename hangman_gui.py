import tkinter as tk
from tkinter import messagebox, simpledialog
from game_logic import HangmanGame

class HangmanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Le Jeu du Pendu")
        self.root.geometry("800x600")
        self.game = HangmanGame()

        self.setup_ui()
        self.start_new_game()

    def setup_ui(self):
        # Main frames
        self.stats_frame = tk.Frame(self.root, pady=10)
        self.stats_frame.pack(fill=tk.X)

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack()

        self.word_frame = tk.Frame(self.root, pady=20)
        self.word_frame.pack()

        self.keyboard_frame = tk.Frame(self.root, pady=10)
        self.keyboard_frame.pack()

        # Stats Labels
        self.stats_label = tk.Label(self.stats_frame, text="", font=("Helvetica", 12))
        self.stats_label.pack()
        self.score_label = tk.Label(self.stats_frame, text="", font=("Helvetica", 12))
        self.score_label.pack()

        # Canvas for hangman drawing
        self.canvas = tk.Canvas(self.canvas_frame, width=400, height=250, bg="white")
        self.canvas.pack()

        # Word Label
        self.word_label = tk.Label(self.word_frame, text="", font=("Courier", 24))
        self.word_label.pack()

        # Keyboard Buttons
        self.keyboard_buttons = {}
        self.create_keyboard()

        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Jeu", menu=game_menu)
        game_menu.add_command(label="Nouvelle Partie", command=self.start_new_game)
        game_menu.add_separator()
        game_menu.add_command(label="Quitter", command=self.root.quit)

    def create_keyboard(self):
        for frame in self.keyboard_frame.winfo_children():
            frame.destroy()

        keys = 'abcdefghijklmnopqrstuvwxyz'
        for i, key in enumerate(keys):
            row = i // 9
            col = i % 9
            button = tk.Button(self.keyboard_frame, text=key.upper(), width=4, font=("Helvetica", 10),
                               command=lambda k=key: self.handle_guess(k))
            button.grid(row=row, column=col, padx=2, pady=2)
            self.keyboard_buttons[key] = button

    def start_new_game(self):
        game_mode = self.choose_game_mode()
        if not game_mode: return

        difficulty = self.choose_difficulty()
        if not difficulty: return

        self.game.set_difficulty(difficulty)

        if game_mode == '1': # Local
            category = self.choose_category()
            if not category: return
            self.game.start_new_round(game_mode, category)
        elif game_mode == '2': # Online
            self.game.start_new_round(game_mode)
        elif game_mode == '3': # Two Player
            word = self.get_player_word()
            if not word: return
            self.game.set_player_word(word)
            self.game.start_new_round(game_mode)

        self.game.stats['played'] += 1
        self.update_ui()
        for btn in self.keyboard_buttons.values():
            btn.config(state=tk.NORMAL)

    def choose_game_mode(self):
        return simpledialog.askstring("Mode de Jeu", "Choisissez un mode :\n1. Solo (Mots locaux)\n2. Solo (Mots en ligne)\n3. Deux Joueurs", parent=self.root)

    def choose_difficulty(self):
        return simpledialog.askstring("Difficulté", "Choisissez une difficulté :\n1. Facile\n2. Moyen\n3. Difficile", parent=self.root)

    def choose_category(self):
        categories = list(self.game.words.keys())
        cat_string = "\n".join([f"{i+1}. {cat}" for i, cat in enumerate(categories)])
        choice = simpledialog.askstring("Catégorie", f"Choisissez une catégorie :\n{cat_string}", parent=self.root)
        if choice and choice.isdigit() and 1 <= int(choice) <= len(categories):
            return categories[int(choice) - 1]
        return None

    def get_player_word(self):
        return simpledialog.askstring("Mot Secret", "Joueur 1, entrez le mot secret :", show='*', parent=self.root)

    def handle_guess(self, key):
        if self.game.game_is_done: return

        self.keyboard_buttons[key].config(state=tk.DISABLED)
        result = self.game.guess_letter(key)
        self.update_ui()

        if self.game.game_is_done:
            self.end_game()

    def update_ui(self):
        # Update stats
        stats_text = f"Parties: {self.game.stats['played']} | Victoires: {self.game.stats['wins']} | Défaites: {self.game.stats['losses']}"
        score_text = f"Score: {self.game.score} | Meilleur Score: {self.game.highscore} | Difficulté: {self.game.difficulty}"
        self.stats_label.config(text=stats_text)
        self.score_label.config(text=score_text)

        # Update word display
        blanks = ' '.join([c.upper() if c in self.game.correct_letters else '_' for c in self.game.secret_word])
        self.word_label.config(text=blanks)

        # Update hangman drawing
        self.draw_hangman(len(self.game.missed_letters))

    def draw_hangman(self, stage):
        self.canvas.delete("all")
        self.canvas.create_line(10, 230, 150, 230, width=2) # Base
        if stage > 0: self.canvas.create_line(80, 230, 80, 20, width=2) # Pole
        if stage > 1: self.canvas.create_line(80, 20, 200, 20, width=2) # Beam
        if stage > 2: self.canvas.create_line(200, 20, 200, 50, width=2) # Rope
        if stage > 3: self.canvas.create_oval(180, 50, 220, 90, width=2) # Head
        if stage > 4: self.canvas.create_line(200, 90, 200, 150, width=2) # Body
        if stage > 5: self.canvas.create_line(200, 110, 170, 140, width=2) # Left Arm
        if stage > 6: self.canvas.create_line(200, 110, 230, 140, width=2) # Right Arm
        if stage > 7: self.canvas.create_line(200, 150, 170, 180, width=2) # Left Leg
        if stage > 8 and self.game.max_guesses > 8: self.canvas.create_line(200, 150, 230, 180, width=2) # Right Leg
        elif stage > 6 and self.game.max_guesses <= 6: self.canvas.create_line(200, 150, 230, 180, width=2) # Right Leg

    def end_game(self):
        self.game.save_stats()
        if self.game.score > self.game.highscore:
            self.game.save_highscore()
        
        won = len(self.game.missed_letters) < self.game.max_guesses
        message = f"Vous avez gagné! Le mot était '{self.game.secret_word}'." if won else f"Vous avez perdu! Le mot était '{self.game.secret_word}'."
        
        if messagebox.askyesno("Fin de partie", f"{message}\nVoulez-vous rejouer?"):
            self.start_new_game()
        else:
            self.root.quit()

if __name__ == '__main__':
    root = tk.Tk()
    app = HangmanGUI(root)
    root.mainloop()
