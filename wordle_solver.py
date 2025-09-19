import json
import random
import math
from collections import Counter


with open('valid_list.json', 'r') as f:
    words = [word.upper() for word in json.load(f)]
    ALLOWED_GUESSES = words

with open('seed_list.json', 'r') as g:
    words = [word.upper() for word in json.load(g)]
    POSSIBLE_ANSWERS = words


def calculate_pattern(guess: str, answer: str) -> str:
    pattern = ['b'] * 5
    answer_counts = Counter(answer)
    for i in range(5):
        if guess[i] == answer[i]:
            pattern[i] = 'g'
            answer_counts[guess[i]] -= 1
    for i in range(5):
        if pattern[i] == 'g': continue
        if guess[i] in answer_counts and answer_counts[guess[i]] > 0:
            pattern[i] = 'y'
            answer_counts[guess[i]] -= 1
    return "".join(pattern)


def calculate_entropy_for_guess(guess: str, possible_answers: list[str]) -> float:
    """Calculates the Shannon entropy for a single potential guess."""
    num_possible = len(possible_answers)
    if num_possible == 0: return 0.0
    
    partitions = Counter(calculate_pattern(guess, answer) for answer in possible_answers)
    entropy = 0.0
    for count in partitions.values():
        p = count / num_possible
        entropy += -p * math.log2(p)
    return entropy


class WordleEnv:
    """
    A Wordle environment for Reinforcement Learning.
    """
    def __init__(self, max_attempts=6):
        self.max_attempts = max_attempts
        self.all_possible_answers = POSSIBLE_ANSWERS
        self.all_allowed_guesses = ALLOWED_GUESSES

    def reset(self):
        """Resets the environment to a new game."""
        self.target_word = random.choice(self.all_possible_answers)
        self.possible_answers = self.all_possible_answers.copy()
        self.attempts = []
        self.num_attempts = 0
        self.num_valid_attempts = 0 

        # For debugging
        # print(f"(New Game - Target is {self.target_word})")
        
        observation = self._get_obs()
        info = self._get_info() # removed to speed up initialization
        return observation, info

    def _get_obs(self):
        """
        Constructs the observation for the agent.
        A proper implementation would be a numerical numpy array.
        For now, we'll return a descriptive dict.
        """
        return {
            "attempts_history": self.attempts,
            "num_possible_words": len(self.possible_answers),
            "round": self.num_valid_attempts
        }

    def _get_info(self):
        """
        Constructs the info dictionary with diagnostic data.
        This is where we put the compute-intensive entropy calculations.
        """
        if len(self.possible_answers) == 0:
            return {"entropies": {}}
        
        if len(self.possible_answers) == 1:
            return {
                "num_possible_answers": 1,
                "entropies": [(self.possible_answers[0], 0.0)]
            }

        # This is the compute-intensive part, in particular on the first turn.
        print("Calculating entropies for all possible guesses...")
        entropies = {
            guess: calculate_entropy_for_guess(guess, self.possible_answers) 
            for guess in self.all_allowed_guesses
        }
        
        return {
            "num_possible_answers": len(self.possible_answers),
            "entropies": sorted(entropies.items(), key=lambda item: item[1], reverse=True)
        }

    def step(self, guess_word: str):
        """
        Executes one step in the environment.
        - action: an integer representing the word to guess.
        """
        if self.num_valid_attempts >= self.max_attempts:
            raise Exception("Game is already over. Please call reset().")

        self.num_attempts += 1

        valid = guess_word in self.all_allowed_guesses
        info = {}
        pattern = None
        guess_entropy = None
        info_gain = 0.0
        
        # Handle Invalid Action
        if guess_word is None or not valid:
            reward = -2.0 # Penalty for invalid action index or word
            terminated = False
            observation = self._get_obs()
            self.attempts.append({
                'guess': guess_word, 
                'valid': valid,
                'pattern': pattern,
                'guess_entropy': guess_entropy,
                'info_gain': info_gain
            })
            print(f"Guess '{guess_word}' is invalid.")
            return observation, reward, terminated, info

        self.num_valid_attempts += 1
        
        # Calculate Game Logic
        num_possible_before = len(self.possible_answers)
        pattern = calculate_pattern(guess_word, self.target_word)
        guess_entropy = calculate_entropy_for_guess(guess_word, self.possible_answers)
        self.possible_answers = [
            word for word in self.possible_answers
            if calculate_pattern(guess_word, word) == pattern
        ]
        num_possible_after = len(self.possible_answers)

        # log2(N) is the entropy of a uniform distribution over N items.
        info_gain = math.log2(num_possible_before) - math.log2(max(1, num_possible_after))
        self.attempts.append({
            'guess': guess_word, 
            'valid': valid,
            'pattern': pattern,
            'guess_entropy': guess_entropy,
            'info_gain': info_gain
        })

        # Determine Reward and Termination
        terminated = False
        if guess_word == self.target_word:
            reward = 10.0 # Large reward for winning
            terminated = True
        elif self.num_valid_attempts >= self.max_attempts:
            reward = -10.0 # Large penalty for losing
            terminated = True
        else:
            # Intermediate Reward based on Information Gain
            # This rewards reducing uncertainty while slightly penalizing time
            time_penalty = -0.1
            reward = info_gain + time_penalty

        observation = self._get_obs()
        # recalculates entropies for next step to use
        info = self._get_info() if not terminated else {}
        
        return observation, reward, terminated, info


def main():
    env = WordleEnv()
    observation, info = env.reset()
    
    # # Get the initial info to pick the best first word
    best_first_guesses = info['entropies'][:20]
    print(f"\nBest first guess based on initial entropy calculation: {best_first_guesses}")

    terminated = False
    total_reward = 0
    
    while not terminated:
        print("\n" + "="*30)
        
        # # In a real RL setup, an agent (policy network) would choose the action
        # # Here, we'll "cheat" and use our solver logic to pick the best action
        
        # # If there's only one word left, guess it
        # if len(env.possible_answers) == 1:
        #     action_word = env.possible_answers[0]
        # else:
        #     # Use the pre-computed entropies from the last step's info dict
        #     action_word = info['entropies'][0][0]  # Pick the word with highest entropy

        action_word = input("Enter your guess (or 'quit' to stop): ")
        if action_word.lower() == 'quit':
            print("Exiting game.")
            break
        
        print(f"Agent chooses '{action_word}'")
        
        observation, reward, terminated, info = env.step(action_word.upper())
        
        total_reward += reward
        print(f"Current State: {observation}")
        print(f"--> Received Reward: {reward:.3f}")
        print(f"--> Game Terminated: {terminated}")
        if not terminated:
            best_guesses = info['entropies'][:min(5, len(info['entropies']))] if info['entropies'] else []
            print(f"Top 5 next guesses based on entropy: {best_guesses}")

    print("\n" + "="*30)
    print(f"Game Over!")
    print(f"Final State: {observation}")
    print(f"Total Reward: {total_reward:.3f}")

if __name__ == "__main__":
    main()