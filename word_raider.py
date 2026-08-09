import random

game_name = "Word Raider"
word_bank = []

with open("words.txt") as word_file:
    for line in word_file:
        word_bank.append(line.rstrip().lower())

selected_word = random.choice(word_bank)

# Defining game information
incorrect_letters = []
misplaced_letters = []
max_turns = 6
used_turns = 0

print(f"Welcome to {game_name}!")
print(f"The word to guess has {len(selected_word)} letters.")
print(f"You have {max_turns} turns to guess the word!")

# Set up a loop with an exit condition
while used_turns < max_turns:
    guess = input("Guess a word (or type 'stop' to end the game): ").lower().strip()

    if guess == "stop":
        print("Thanks for playing!")
        break

    if len(guess) != len(selected_word) or not guess.isalpha():
        print(f"Please enter a 5 letter word.")
        continue

    index = 0

    for letter in guess:
        if letter == selected_word[index]:
            print(letter, end=" ")
            if letter in misplaced_letters:
                misplaced_letters.remove(letter)
        elif letter in selected_word:
            if letter not in misplaced_letters:
                misplaced_letters.append(letter)
            print("_", end=" ")
        else:
            if letter not in incorrect_letters:
                incorrect_letters.append(letter)
            print("_", end=" ")
        index += 1

    # Win condition
    if guess == selected_word:
        print(f"\nCongratulations! You guessed the word '{selected_word}' correctly!")
        break

    used_turns += 1

    # Lose condition
    if used_turns == max_turns:
        print(f"\nGame over! You've used all your turns. The correct word was '{selected_word}'.")
        break

    print("\n")
    print(f"Misplaced letters: {misplaced_letters}")
    print(f"Incorrect letters: {incorrect_letters}")
    print(f"You have {max_turns - used_turns} turns left.")
