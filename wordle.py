from processing.state import WordleState

def main():
    game = WordleState()

    # scores = game.get_word_scores()

    # print("Top 10 words by entropic score:")
    # for word, score in scores[:10]:
    #     print(f"{word}: {score:.4f}")

    continue_game = True

    while continue_game:
        user_input = input("Enter your guess (or 'quit' to stop): ")
        if user_input.lower() == 'quit':
            continue_game = False
        else:
            continue_game = game(user_input)

        if not continue_game:
            game_state = game.get_state()
            print("Final game state:")
            print(game_state)

if __name__ == "__main__":
    main()