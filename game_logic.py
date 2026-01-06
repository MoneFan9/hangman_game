import random
import os
import json
import sys
import time
import getpass
import requests

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Dummy:
        def __getattr__(self, name): return ""
    Fore, Style = Dummy(), Dummy()

HIGHSCORE_FILE = 'highscore.txt'
STATS_FILE = 'stats.json'

class HangmanGame:
    def __init__(self):
        self.hangman_pics = [
            '''
               +---+
                   |
                   |
                   |
                  ===''', 
            '''
               +---+
               O   |
                   |
                   |
                  ===''', 
            '''
               +---+
               O   |
               |   |
                   |
                  ===''', 
            '''
               +---+
               O   |
              /|   |
                   |
                  ===''', 
            '''
               +---+
               O   |
              /|\  |
                   |
                  ===''', 
            '''
               +---+
               O   |
              /|\  |
              /    |
                  ===''', 
            '''
               +---+
               O   |
              /|\  |
              / \  |
                  ==='''
        ]
        self.words = {
            'Animaux': 'fourmi babouin blaireau chauve-souris ours castor chameau chat palourde cobra couguar coyote corbeau cerf chien âne canard aigle furet renard grenouille chèvre oie faucon lion lézard lama taupe singe orignal souris mulet triton loutre hibou panda perroquet pigeon python lapin bélier rat corbeau rhinocéros saumon phoque requin mouton mouffette paresseux serpent araignée cigogne cygne tigre crapaud truite dinde tortue belette baleine loup wombat zèbre'.split(),
            'Fruits': 'pomme banane orange fraise raisin ananas mangue myrtille framboise pastèque cerise pêche poire prune citron vert'.split(),
            'Pays': 'france allemagne italie espagne portugal belgique suisse autriche pologne russie chine japon inde brésil argentine canada mexique égypte nigéria australie'.split()
        }
        self.game_mode = ''
        self.missed_letters = ''
        self.correct_letters = ''
        self.secret_word = ''
        self.secret_category = ''
        self.game_is_done = False
        self.score = 0
        self.highscore = self.load_highscore()
        self.stats = self.load_stats()
        self.difficulty = 'Moyen'
        self.max_guesses = 6
        self.hint_used = False

    def load_highscore(self):
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, 'r') as f:
                try: return int(f.read())
                except (ValueError, TypeError): return 0
        return 0

    def save_highscore(self):
        if self.score > self.highscore:
            print(f"{Fore.YELLOW}Nouveau meilleur score ! {self.score}{Style.RESET_ALL}")
            self.highscore = self.score
            with open(HIGHSCORE_FILE, 'w') as f:
                f.write(str(self.highscore))

    def load_stats(self):
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                try: return json.load(f)
                except json.JSONDecodeError: return {'played': 0, 'wins': 0, 'losses': 0}
        return {'played': 0, 'wins': 0, 'losses': 0}

    def save_stats(self):
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=4)

    def get_random_word(self, word_list):
        return random.choice(word_list)

    def fetch_online_word(self):
        try:
            print(f"{Fore.CYAN}Récupération d'un mot en ligne...{Style.RESET_ALL}")
            response = requests.get("https://random-word-api.herokuapp.com/word?lang=fr&number=1")
            response.raise_for_status()
            word = response.json()[0].lower()
            if all('a' <= c <= 'z' for c in word):
                self.secret_word = word
                self.secret_category = 'En Ligne'
                return True
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Erreur réseau : {e}. Utilisation des mots locaux.{Style.RESET_ALL}")
        except (ValueError, IndexError):
            print(f"{Fore.RED}Erreur de l'API. Utilisation des mots locaux.{Style.RESET_ALL}")
        
        time.sleep(2)
        return False

    def set_player_word(self, word):
        self.secret_word = word.lower()
        self.secret_category = 'Deux Joueurs'

    def set_difficulty(self, choice):
        if choice == '1':
            self.difficulty = 'Facile'
            self.max_guesses = 8
        elif choice == '2':
            self.difficulty = 'Moyen'
            self.max_guesses = 6
        elif choice == '3':
            self.difficulty = 'Difficile'
            self.max_guesses = 4

    def start_new_round(self, game_mode, category=None):
        self.missed_letters = ''
        self.correct_letters = ''
        self.game_is_done = False
        self.hint_used = False
        self.score = 0
        self.game_mode = game_mode

        if self.game_mode == '1': # Local
            self.secret_category = category
            self.secret_word = self.get_random_word(self.words[self.secret_category])
        elif self.game_mode == '2': # Online
            if not self.fetch_online_word():
                # Fallback to local words
                self.secret_category = 'Animaux' # Default category
                self.secret_word = self.get_random_word(self.words[self.secret_category])
        # Mode 3 (Two Player) is handled by set_player_word

    def guess_letter(self, guess):
        if guess == 'hint':
            return self.use_hint()
        
        if guess in self.secret_word:
            if guess not in self.correct_letters:
                self.correct_letters += guess
                self.score += 10
                self.check_win()
            return 'correct'
        else:
            if guess not in self.missed_letters:
                self.missed_letters += guess
                self.check_loss()
            return 'incorrect'

    def use_hint(self):
        if self.hint_used or self.score < 50:
            return 'no_hint'
        
        self.score -= 50
        self.hint_used = True
        unguessed_letters = [letter for letter in self.secret_word if letter not in self.correct_letters]
        if unguessed_letters:
            hint_letter = random.choice(unguessed_letters)
            self.correct_letters += hint_letter
            self.check_win()
            return 'hint_used'
        return 'no_hint'

    def check_win(self):
        if all(c in self.correct_letters for c in self.secret_word):
            self.score += 100
            self.stats['wins'] += 1
            self.game_is_done = True

    def check_loss(self):
        if len(self.missed_letters) >= self.max_guesses:
            self.stats['losses'] += 1
            self.game_is_done = True
