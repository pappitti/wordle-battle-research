# Wordle Solver and Reinforcement Learning Environment

This repository contains a Python-based Wordle solver that uses information theory to determine the optimal guess at each step. The project is designed with a dual purpose:

1.  **An Interactive Command-Line Game**: You can play Wordle in your terminal, and the solver will provide you with the top-ranked word suggestions at each turn.
2.  **A Reinforcement Learning (RL) Environment**: The code is structured to set a perfect foundation for training an AI agent to play Wordle.

The core of the solver is its ability to calculate the **Shannon entropy** for every possible guess, choosing the word that is expected to provide the most information and reduce the list of possible answers most effectively.

## Key Features

-   **Information-Theoretic Solver**: Implements a robust algorithm based on Shannon entropy to find the mathematically optimal guess.
-   **Reinforcement Learning Ready**: Provides a `WordleEnv` class with a standard API (`step`, `reset`) for easy integration with RL libraries.
-   **Shaped Reward Function**: The environment includes a  reward function (WIP) that provides dense feedback to an RL agent, rewarding information gain and penalizing invalid or slow moves.
-   **Interactive Mode**: A simple `main` function allows you to play the game manually and see the solver's suggestions in real-time.
-   **Detailed Analytics**: At each step, the environment provides detailed diagnostic information, including the entropy scores for all possible guesses.

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/pappitti/wordle-battle-research.git
    cd wordle-battle-research
    ```

2.  **Prepare the Word Lists:**
    This project requires two JSON files containing word lists. These were included in the repository but may have been deleted to respect the copyright of the original game.

    -   `seed_list.json`: A list of all possible secret words (the answers).
    -   `valid_list.json`: A comprehensive list of all valid guesses allowed by the game.

    You can typically find these lists by inspecting the source code of the Wordle website or from public datasets on GitHub. The files should be simple JSON arrays of strings, in CAPITAL LETTERS:
    ```json
    // Example format for both files
    ["CIGAR", "REBUT", "SISSY", "HUMPH", ...]
    ```
    Place both files in the root directory of the project.

3.  **Run the Game:**
    No external Python libraries are required. You can run the interactive game directly with Python 3.
    ```bash
    python wordle.py
    ```

## How to Play

When you run the script, the game will start automatically:
1.  A secret word is chosen. For debugging, the word is printed to the console at the start.
2.  The program will calculate and display the top 20 best starting words based on entropy. This may take up to one minute depending on your machine.  
3.  You will be prompted to enter your 5-letter guess.
4.  After each guess, the game will show you:
    - The state of your attempt (the colors, information gain, etc.).
    - The reward your guess would have generated in an RL setting.
    - The number of possible answers remaining.
5.  The game continues until you guess the word or run out of attempts. Type `quit` to exit.

```
(New Game - Target is SLATE)
Calculating entropies for all possible guesses...

Best first guess based on initial entropy calculation: [('SOARE', 6.18...), ('RAISE', 6.17...), ...]

==============================
Enter your guess (or 'quit' to stop): RAISE
Agent chooses 'RAISE'
Calculating entropies for all possible guesses...
Current State: {'attempts_history': [{'guess': 'RAISE', 'valid': True, 'pattern': 'bygyb', 'guess_entropy': 6.17..., 'info_gain': 3.99...}], 'num_possible_words': 148, 'round': 1}
--> Received Reward: 3.899
--> Game Terminated: False
```

## Core Concepts Explained

### 1. Shannon Entropy

The solver's "intelligence" comes from information theory. The best guess is the one that provides the most information, meaning it reduces the uncertainty about the target word as much as possible.

The amount of information (or uncertainty) is measured by **Shannon entropy**:
`Entropy = Σ -p(outcome) * log2(p(outcome))`

In our case:
-   An **outcome** is a specific color pattern (e.g., `'gybbg'`).
-   `p(outcome)` is the probability of seeing that pattern for a given guess. We calculate this by seeing how many of the `possible_answers` would produce that pattern.

The word with the highest entropy is the one that, on average, will split the remaining `possible_answers` into the smallest, most numerous groups, thus maximizing the information we gain from the guess.

### 2. Reinforcement Learning Environment

The `WordleEnv` class is designed to train an AI. It follows a standard structure:

-   **State (`observation`)**: A dictionary representing the current game state, including guess history, number of remaining words, and the current round. This would be converted to a numerical vector or tensor for a real agent.
-   **Action (`step(word)`)**: The agent's action is to choose a word to guess.
-   **Reward (WIP)**: The feedback signal the agent learns from. The reward function is carefully shaped:
    -   **+10.0** for winning the game.
    -   **-10.0** for losing the game.
    -   **-2.0** for making an invalid guess.
    -   **`information_gain - 0.1`** for each valid step. The `information_gain` is `log2(words_before) - log2(words_after)`, directly rewarding the agent for making high-entropy guesses. The `-0.1` is a small time penalty to encourage faster solutions.

## Future Work and Roadmap

This project is a strong starting point for a full-fledged Wordle AI. The next steps are:

-   [ ] **Train an RL Agent**: Rebuild an actual RL environment based on `WordleEnv` and learn to play the game.
-   [ ] **Develop a Numerical State Representation**: Convert the dictionary-based observation into a numerical `numpy` array suitable for a neural network (e.g., using one-hot encoding for letters and board state).
-   [ ] **Performance Optimization**: The entropy calculation for all ~13,000 words can be slow. For the first turn, this value can be cached. For later turns, parallelization (multiprocessing) could be used to speed up calculations.
-   [ ] **Analyze Agent Performance**: Once an agent is trained, analyze its strategies. Does it learn to use high-entropy words? Does it discover common starting words like `SOARE` or `RAISE` on its own?

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.  

## Inspiration
- Will Brown's work and in particular his [wordle environment](https://github.com/willccbb/verifiers/tree/main/environments/wordle) 
- Quanta Magazine : [Why Claude Shannon Would Have Been Great at Wordle](https://www.quantamagazine.org/how-math-can-improve-your-wordle-score-20220525/)