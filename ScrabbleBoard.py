
import json
import random
"""module that creates a scrabble game board
"""

class ScrabbleBoard:
    """
    Represents a Scrabble board.
    """
    def __init__(self):
        """
        Initializes the Scrabble board as a 15x15 grid of empty squares.
        """
        self.board = [[' ' for _ in range(15)] for _ in range(15)]
        
        with open('letter_distribution.json', 'r') as f:
            self.letters_to_draw_from = json.load(f)
        with open('letter_points.json', 'r') as f:
            self.scores = json.load(f)


    def draw_letters(self, num_letters):
        """
        Draws random letters from the current distribution of letters.

        Args:
            num_letters (int): The number of letters to draw.

        Returns:
            list: A list of drawn letters.

        Raises:
            ValueError: If num_letters is greater than the total number of letters remaining.
        """
        # Flatten the dictionary into a list of letters
        letters = [letter for letter, count in self.letters_to_draw_from.items() for _ in range(count)]

        if num_letters > len(letters):
            num_letters = len(letters)

        drawn_letters = random.sample(letters, num_letters)

        # Update the counts of the drawn letters
        for letter in drawn_letters:
            self.letters_to_draw_from[letter] -= 1
            if self.letters_to_draw_from[letter] == 0:
                del self.letters_to_draw_from[letter]  # remove the letter if there's no more left

        return drawn_letters



    def place_word(self, row, col, word, direction):
        """
        Places a word on the Scrabble board.

        Args:
            row (int): The starting row to place the word.
            col (int): The starting column to place the word.
            word (str): The word to be placed.
            direction (str): The direction to place the word. Must be 'across' or 'down'.

        Returns:
            bool: True if the word was successfully placed, False otherwise.
        """
        if direction == 'across':
            if col + len(word) > 15:
                return False
            for i, letter in enumerate(word):
                self.board[row][col + i] = letter
        elif direction == 'down':
            if row + len(word) > 15:
                return False
            for i, letter in enumerate(word):
                self.board[row + i][col] = letter
        else:
            raise ValueError("Direction must be 'across' or 'down'.")

        return True


    def display_board(self):
        """
        Prints the current state of the Scrabble board.
        """
        for i in range(15):
            for j in range(15):
                print(self.board[i][j], end=' ')
            print()  # Newline after each row


    def calculate_score(self, letters, letter_multiplier_list, word_multiplier_list):
        """
        Calculates the score of a word based on letter scores and multipliers.

        This function computes the score by multiplying the score of each letter
        in the word by the corresponding letter multiplier, summing up these values,
        and then multiplying the result by the product of the word multipliers.

        If the length of the letters string does not match the length of the multiplier lists,
        the function returns -1 and prints an error message.

        Args:
            letters (str): The word for which to calculate the score.
            letter_multiplier_list (list of int): A list of multipliers corresponding to each
                letter in the word. The i-th multiplier is applied to the i-th letter in the word.
            word_multiplier_list (list of int): A list of multipliers applied to the total word
                score. All these multipliers are multiplied together and then the product is
                used to multiply the total score calculated so far.

        Returns:
            int: The total score of the word based on letter scores and multipliers, or -1
                if the input lists do not have the same length as the letters string.
        """
        if len(letters) != len(letter_multiplier_list) or len(letters) != len(word_multiplier_list):
            print('invalid letters/multipliers input')
            return -1
        else:
            score = 0
            for letter, multiplier in zip(letters, letter_multiplier_list):
                letter_score = self.scores[letter]
                score += letter_score * multiplier

            word_multiplier = 1
            for multiplier in word_multiplier_list:
                word_multiplier *= multiplier
            score *= word_multiplier
            return score
