import os
import sys
import time
import getpass
from game_logic import HangmanGame, Fore, Style

class HangmanConsole:
    def __init__(self):
        self.game = HangmanGame()

    def play(self):
        self.clear_screen()
        welcome_frames = [
            f'{Fore.GREEN}B I E N V E N U E',
            f'{Fore.GREEN}B I E N V E N U E   D A N S',
            f'{Fore.GREEN}B I E N V E N U E   D A N S   H A N G M A N !'
        ]
        self.play_animation(welcome_frames, 0.3)
        time.sleep(1)
        
        while True:
            game_mode = self.choose_game_mode()
            difficulty = self.choose_difficulty()
            self.game.set_difficulty(difficulty)

            if game_mode == '1': # Local
                category = self.choose_category()
                self.game.start_new_round(game_mode, category)
            elif game_mode == '2': # Online
                self.game.start_new_round(game_mode)
            elif game_mode == '3': # Two Player
                self.get_player_word()
                self.game.start_new_round(game_mode)

            self.game.stats['played'] += 1
            while not self.game.game_is_done:
                self.display_board()
                guess = self.get_guess()
                result = self.game.guess_letter(guess)
                if result == 'incorrect':
                    print('\a', end='') # Bell sound
                elif result == 'no_hint':
                    print(f"{Fore.YELLOW}Indice non disponible.{Style.RESET_ALL}")
                    time.sleep(2)
                elif result == 'hint_used':
                    print(f"{Fore.CYAN}Indice utilisé!{Style.RESET_ALL}")
                    time.sleep(2)

            self.display_board() # Show final state
            if self.game.score > self.game.highscore:
                self.game.save_highscore()

            self.game.save_stats()

            if not self.play_again():
                print(f"{Fore.CYAN}Merci d'avoir joué! À bientôt!{Style.RESET_ALL}")
                break

    def display_board(self):
        self.clear_screen()
        border = f"{Fore.BLUE}{'=' * 70}{Style.RESET_ALL}"
        print(border)
        stats_line = f"{Fore.CYAN}Parties: {self.game.stats['played']} | Victoires: {self.game.stats['wins']} | Défaites: {self.game.stats['losses']}{Style.RESET_ALL}"
        header = f"{Fore.CYAN}Score: {self.game.score}  |  Meilleur Score: {self.game.highscore}  |  Difficulté: {self.game.difficulty}{Style.RESET_ALL}"
        print(stats_line.center(78))
        print(header.center(78))
        print(border)

        print(Fore.YELLOW + self.game.hangman_pics[min(len(self.game.missed_letters), self.game.max_guesses - 1)])
        print(f'La catégorie est : {Fore.MAGENTA}{self.game.secret_category}{Style.RESET_ALL}')
        print(f'{Fore.RED}Lettres manquées:', ' '.join(self.game.missed_letters))
        print()
        blanks = ''.join([f'{Fore.GREEN}{c}{Style.RESET_ALL} ' if c in self.game.correct_letters else '_ ' for c in self.game.secret_word])
        print(blanks)
        print(border)
        if self.game.game_is_done:
            if len(self.game.missed_letters) >= self.game.max_guesses:
                print(f'{Fore.RED}Vous avez perdu! Le mot était "{self.game.secret_word}".{Style.RESET_ALL}')
            else:
                print(f'{Fore.GREEN}Gagné! Le mot était "{self.game.secret_word}"{Style.RESET_ALL}')

    def get_guess(self):
        while True:
            print(f"Devinez une lettre ou tapez '{Fore.YELLOW}hint{Style.RESET_ALL}' pour un indice.")
            guess = input('> ').lower()
            if guess == 'hint':
                return 'hint'
            if len(guess) != 1:
                print(f'{Fore.RED}Veuillez entrer une seule lettre.')
            elif guess in self.game.missed_letters + self.game.correct_letters:
                print(f'{Fore.YELLOW}Vous avez déjà deviné cette lettre.')
            elif not 'a' <= guess <= 'z':
                print(f'{Fore.RED}Veuillez entrer une LETTRE.')
            else:
                return guess

    def get_player_word(self):
        self.clear_screen()
        print(f"{Fore.CYAN}Mode Deux Joueurs{Style.RESET_ALL}")
        print("Joueur 1, veuillez entrer un mot secret.")
        while True:
            try:
                word = getpass.getpass("Mot secret (sera caché) : ").lower()
                if word and all('a' <= c <= 'z' for c in word):
                    self.game.set_player_word(word)
                    return
                else:
                    print(f"{Fore.RED}Mot invalide. Veuillez n'utiliser que des lettres.{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Erreur : {e}{Style.RESET_ALL}")

    def choose_category(self):
        print('Choisissez une catégorie :')
        categories = list(self.game.words.keys())
        for i, category in enumerate(categories):
            print(f'{i + 1}. {category}')
        while True:
            choice = input(f'> (1-{len(categories)}): ')
            if choice.isdigit() and 1 <= int(choice) <= len(categories):
                return categories[int(choice) - 1]
            else:
                print(f'{Fore.RED}Choix invalide.')

    def choose_difficulty(self):
        self.clear_screen()
        print('Choisissez une difficulté :')
        print(f"1. {Fore.GREEN}Facile{Style.RESET_ALL} (8 vies)")
        print(f"2. {Fore.YELLOW}Moyen{Style.RESET_ALL} (6 vies)")
        print(f"3. {Fore.RED}Difficile{Style.RESET_ALL} (4 vies)")
        while True:
            choice = input('> (1-3): ')
            if choice in ['1', '2', '3']:
                return choice
            else:
                print(f'{Fore.RED}Choix invalide.')

    def choose_game_mode(self):
        self.clear_screen()
        print("Choisissez un mode de jeu :")
        print("1. Solo (Mots locaux)")
        print("2. Solo (Mots en ligne)")
        print("3. Deux Joueurs")
        while True:
            choice = input('> (1-3): ')
            if choice in ['1', '2', '3']:
                return choice
            else:
                print(f'{Fore.RED}Choix invalide.')

    def play_again(self):
        print('Voulez-vous rejouer? (oui ou non)')
        return input('> ').lower().startswith('o')

    def play_animation(self, frames, delay=0.1):
        for frame in frames:
            self.clear_screen()
            print(frame)
            time.sleep(delay)

    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == '__main__':
    try:
        console_game = HangmanConsole()
        console_game.play()
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}Partie interrompue. À bientôt!{Style.RESET_ALL}")
        sys.exit(0)
