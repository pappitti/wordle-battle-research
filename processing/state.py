import json
import random

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class WordleState:

    def __init__(self):
        self.attempts = [] 
        self.round = 0
        self.valid_rounds = 0

        with open('seed_list.json', 'r') as f : 
            self.seeds = json.load(f)

        self.possible_values = self.seeds.copy()
        self.target : str = random.choice(self.seeds)
        # print(self.target)

        self.letter_sets = [ #  probability of possible letters for each spot in a 5-letter word
            {letter : {} for letter in ALPHABET} for _ in range(5)
        ]


    def _check_word(self, word : str):
        return word in self.seeds


    def _check_letters(self, word : str):

        colors=[]

        for i in range(5):
            letter = word[i]
            if self.target[i] == letter:
                color = 'g' # green if correct place
            elif letter in self.target:
                color = 'y' # yellow if present but wrong place
            else :
                color = 'b' # black if not present

            colors.append(color)

        return colors


    def _update_letter_probabilities(self, update : bool = True):
        '''
        Update the letter probabilities based on the current possible values.
        If update is False, return the calculated probabilities without updating self.letter_sets.
        '''

        total_possible = max(len(self.possible_values), 1)
        letter_probs = [ {} for _ in range(5) ]

        for i in range(5):
            for letter in self.letter_sets[i]:
                exact_count = sum(1 for pv in self.possible_values if pv[i] == letter)
                present_count = sum(
                    1 for pv in self.possible_values if letter in pv and pv[i] != letter
                )
                letter_probs[i][letter] = {
                    "exact": exact_count / total_possible,
                    "present": present_count / total_possible
                }

        if update :
            self.letter_sets = letter_probs
        else :
            return letter_probs
    
    
    def _calculate_entropic_score(self, word: str, letter_probs = None) -> float:
        '''
        Calculate the entropic_score of a given word based on letter probabilities.
        if not provided, use self.letter_sets
        IMPORTANT : always call _update_letter_probabilities before calling this function

        entropic score is defined as the sum, for each letter, of its probability-weighted share 
        of the possible words that could be eliminated by guessing that letter in that position.

        Returns the entropic score as a float.
        '''

        if letter_probs is None:
            letter_probs = self.letter_sets

        # TODO : below implementation is wrong, need to consider letters used multiple times
        # e.g. for "APPLE", if "P" is guessed once, it affects both positions
        # but the current implementation treats them independently
        # This can lead to overestimating the entropic score for words with repeated letters.

        entropic = 0.0
        for i in range(5):
            letter = word[i]
            if letter in letter_probs[i]:
                # probabilities of the letter being exact, present, or absent
                p_exact = letter_probs[i][letter]["exact"]
                p_present = letter_probs[i][letter]["present"]
                p_absent = 1 - p_exact - p_present

                # share of possible words eliminated by this guess
                eliminated_if_exact = 1 - p_exact
                eliminated_if_absent = p_absent
                eliminated_if_present = 1 - eliminated_if_exact - eliminated_if_absent

                # weighted contribution to entropic score
                entropic += p_exact * eliminated_if_exact + p_present * eliminated_if_present + p_absent * eliminated_if_absent

        return entropic
        

    def _update_possible_values(self, word: str, colors : list[str]):

        for i in range(5):
            color = colors[i]

            if color == 'b':
                for j in range(5):
                    self.letter_sets[j].pop(word[i], None)
            else: 
                self.letter_sets[i].pop(word[i], None)

            if color == 'g' :
                self.letter_sets[i] = {word[i]: {"exact": 1, "present": 0}}

        for i in range(5):
            for pv in self.possible_values:
                if pv[i] not in self.letter_sets[i]:
                    try: # pv may have been removed in the previous iteration
                        self.possible_values.remove(pv)
                    except ValueError:
                        pass


    def __call__(self, word:str) -> bool:

        word = word.upper()
        colors = None
        entropic_score = None
        
        if self.round >= 6:
            print(f"Sorry, you've used all your attempts. The word was {self.target}.")
            return False

        valid = self._check_word(word)

        if valid :
            # check if word is correct
            self.valid_rounds += 1

            # entropic_score calculation
            ## precomputing requires more memory and processing but we can use the values to find optimal words
            self._update_letter_probabilities() 
            entropic_score = self._calculate_entropic_score(word)

            colors = self._check_letters(word)

            # update possible values
            self._update_possible_values(word, colors)
            try:
                self.seeds.remove(word)
            except ValueError:
                pass
        else :
            print(f"{word} is not a valid word.")
            
        attempt = { 
            'word': word, 
            'valid': valid, 
            'colors': colors, 
            'entropic_score': entropic_score 
        }

        print(attempt)

        self.attempts.append(attempt)
        self.round += 1

        if word == self.target:
            print("Congratulations, you guessed the word!")
            return False

        return True


    def get_state(self):
        '''
        Returns a dictionary representing the current state of the game.
        '''

        state = {
            'word' : self.target,
            'attempts' : self.attempts,
            'valid_rounds' : self.valid_rounds
        }

        return state
    

    def get_word_scores(self):
        '''
        Returns a list of tuples containing each possible word and its corresponding entropic score.
        '''

        letter_probs = self._update_letter_probabilities(update=False)

        word_scores = [
            (word, self._calculate_entropic_score(word, letter_probs)) for word in self.possible_values
        ]
        word_scores.sort(key=lambda x: x[1], reverse=True)

        return word_scores
