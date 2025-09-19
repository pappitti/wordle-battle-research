from transformers import AutoTokenizer, AutoModelForCausalLM
import re
from wordle_solver import WordleEnv, calculate_pattern 

tokenizer = AutoTokenizer.from_pretrained("willcb/Qwen3-1.7B-Wordle")
model = AutoModelForCausalLM.from_pretrained("willcb/Qwen3-1.7B-Wordle")

def run_model(messages):

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )

    outputs = model.generate(**inputs, max_new_tokens=500)
    model_response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])
    return model_response

    
def start_game():
    env = WordleEnv()
    observation, info = env.reset()

    max_attempts = 6
    target_word = env.target_word
    print(f"(New Game - Target is {target_word})")

    messages = [
        {
            "content": "You are a competitive game player. Make sure you read the game instructions carefully, and always follow the required format.\n\nIn each turn, think step-by-step inside <think>...</think> tags, then follow the instructions inside <guess>...</guess> tags.",
            "role": "system"
        },
        {
            "content": "You are Player 0 in Wordle.\nA secret 5-letter word has been chosen. You have 6 attempts to guess it.\nFor each guess, wrap your word in square brackets (e.g., [apple]).\nFeedback for each letter will be given as follows:\n - G (green): correct letter in the correct position\n - Y (yellow): letter exists in the word but in the wrong position\n - X (wrong): letter is not in the word\nEnter your guess to begin.\n",
            "role": "user"
        }
    ]

    guesses = []

    while True:
        model_response = run_model(messages)
        print(messages)
        guess = re.search(r"<guess>\s*\[(\w{5})\]\s*</guess>", model_response)
        if guess:
            guess = guess.group(1).upper()
        else:
            print("[GAME] Player 0 failed to provide a valid guess. Wrong response format or guess with too few or many letters. Trying again.")
            continue

        if guess == target_word:
            print(f"[GAME] Player 0 won the game. Reason: Player 0 guessed the word correctly!")
            break

        valid = guess in env.all_allowed_guesses
        if not valid:
            print(f"[GAME] Player 0 failed to provide a valid guess.'{guess}'. Trying again")
            continue

        print(f"GUESS: {guess}")
        pattern = calculate_pattern(guess, target_word)
        max_attempts -= 1
        
        if max_attempts == 0:
            print(f"[GAME] Player 0 lost the game. Reason: Max attempts reached.")
            break

        converted_pattern = ' '.join(['G' if c == 'g' else 'Y' if c == 'y' else 'X' for c in pattern])

        guesses.append(f"{' '.join(list(guess))}\n{converted_pattern}")

        messages.append({
            "content": f"{model_response}",
            "role": "assistant"
        })
        messages.append({
            "content": f"\n" + "\n".join([f"{g}\n" for g in guesses]) + f"\nYou have {max_attempts} guesses left.",
            "role": "user"
        })


example_completions = [
{
"content": "<think>\nI'll start with a common 5-letter word that includes several vowels to gather initial feedback. A good starting word is \"CRANE\" because it has common letters (C, R, A, N, E) that can help identify the presence and positions of letters in the secret word.\n</think>\n<guess>[crane]</guess>",
"role": "assistant"
},
{
"content": "\nC R A N E\nX X Y X Y\n\nYou have 5 guesses left.",
"role": "user"
},
{
"content": "<think>\nThe feedback for \"CRANE\" is X X Y X Y, which means:\n- A (3rd letter) is in the word but not in the 3rd position (Y).\n- E (5th letter) is in the word but not in the 5th position (Y).\n- C, R, and N are not in the word (X).\n\nFrom this, I know:\n1. The word contains A and E but not in the 3rd or 5th positions.\n2. The word does not contain C, R, or N.\n\nNext, I'll try a word that includes A and E in different positions and avoids C, R, and N. A good option is \"SLATE\" (a variant of \"slate\"), which tests S, L, T and repositions A and E.\n</think>\n<guess>[slate]</guess>",
"role": "assistant"
},
{
"content": "\nC R A N E\nX X Y X Y\n\nS L A T E\nG X Y Y Y\n\nYou have 4 guesses left.",
"role": "user"
},
{
"content": "<think>\nThe feedback for \"SLATE\" is G X Y Y Y, which means:\n- S (1st letter) is correct and in the 1st position (G).\n- A (3rd letter) is in the word but not in the 3rd position (Y).\n- T (4th letter) is in the word but not in the 4th position (Y).\n- E (5th letter) is in the word but not in the 5th position (Y).\n- L (2nd letter) is not in the word (X).\n\nFrom this, combined with the previous guess:\n1. The word starts with S (from \"SLATE\" feedback).\n2. The word contains A, T, and E, but:\n - A is not in the 3rd position (from both \"CRANE\" and \"SLATE\" feedback).\n - T is not in the 4th position (from \"SLATE\" feedback).\n - E is not in the 5th position (from both guesses).\n3. The word does not contain C, R, N, or L (from \"CRANE\" and \"SLATE\" feedback).\n\nNow, let's think of a word that starts with S, includes A, T, and E, and fits the constraints:\n- S must be in the 1st position.\n- A cannot be in the 3rd position.\n- T cannot be in the 4th position.\n- E cannot be in the 5th position.\n\nPossible candidates: \"STEAM\", \"STEAK\", \"STAGE\", \"STALE\". But:\n- \"STALE\" has E in the 5th position, which is invalid (E cannot be there).\n- \"STEAM\" has E in the 2nd position, A in the 4th, and M is untested.\n- \"STEAK\" has E in the 2nd, A in the 3rd (but A cannot be in the 3rd position), so invalid.\n- \"STAGE\" has A in the 3rd position (invalid), so ruled out.\n\n\"STEAM\" seems promising. Let's try it.\n</think>\n<guess>[steam]</guess>",
"role": "assistant"
},
{
"content": "\nC R A N E\nX X Y X Y\n\nS L A T E\nG X Y Y Y\n\nYou have 4 guesses left.\n[Player 0] [steam]\n[GAME] Player 0 won the game. Reason: Player 0 guessed the word correctly!",
"role": "user"
}
]

if __name__ == "__main__":
    start_game()