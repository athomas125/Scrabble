
import json
import random
"""module that creates a scrabble game board
"""

class ScrabbleBoard:
    """
    Represents a Scrabble board.
    """
    def __init__(self, number_of_players):
        """
        Initializes the Scrabble board as a 15x15 grid of empty squares, and the multiplier board.
        """
        self.board = [
            ['3W', ' ', ' ', '2L', ' ', ' ', ' ', '3W', ' ', ' ', ' ', '2L', ' ', ' ', '3W'],
            [' ', '2W', ' ', ' ', ' ', '3L', ' ', ' ', ' ', '3L', ' ', ' ', ' ', '2W', ' '],
            [' ', ' ', '2W', ' ', ' ', ' ', '2L', ' ', '2L', ' ', ' ', ' ', '2W', ' ', ' '],
            ['2L', ' ', ' ', '2W', ' ', ' ', ' ', '2L', ' ', ' ', ' ', '2W', ' ', ' ', '2L'],
            [' ', ' ', ' ', ' ', '2W', ' ', ' ', ' ', ' ', ' ', '2W', ' ', ' ', ' ', ' '],
            [' ', '3L', ' ', ' ', ' ', '3L', ' ', ' ', ' ', '3L', ' ', ' ', ' ', '3L', ' '],
            [' ', ' ', '2L', ' ', ' ', ' ', '2L', ' ', '2L', ' ', ' ', ' ', '2L', ' ', ' '],
            ['3W', ' ', ' ', '2L', ' ', ' ', ' ', '2W', ' ', ' ', ' ', '2L', ' ', ' ', '3W'],
            [' ', ' ', '2L', ' ', ' ', ' ', '2L', ' ', '2L', ' ', ' ', ' ', '2L', ' ', ' '],
            [' ', '3L', ' ', ' ', ' ', '3L', ' ', ' ', ' ', '3L', ' ', ' ', ' ', '3L', ' '],
            [' ', ' ', ' ', ' ', '2W', ' ', ' ', ' ', ' ', ' ', '2W', ' ', ' ', ' ', ' '],
            ['2L', ' ', ' ', '2W', ' ', ' ', ' ', '2L', ' ', ' ', ' ', '2W', ' ', ' ', '2L'],
            [' ', ' ', '2W', ' ', ' ', ' ', '2L', ' ', '2L', ' ', ' ', ' ', '2W', ' ', ' '],
            [' ', '2W', ' ', ' ', ' ', '3L', ' ', ' ', ' ', '3L', ' ', ' ', ' ', '2W', ' '],
            ['3W', ' ', ' ', '2L', ' ', ' ', ' ', '3W', ' ', ' ', ' ', '2L', ' ', ' ', '3W']
        ]
        self.scores = [0] * number_of_players
        self.is_first_turn = True
        self.letter_locations = []
        # a list of board squares string values that are valid to play on top of
        self.valid_play_squares = ['3W', '3L', '2W', '2L', ' ']


        with open('letter_distribution.json', 'r') as f:
            self.letters_to_draw_from = json.load(f)
        with open('letter_points.json', 'r') as f:
            self.scores = json.load(f)

    
    def get_scores(self):
        """return the list of scores of the players in the game

        Returns:
            list(int): list of integer scores
        """
        return self.scores


    def update_scores(self, player_index, score):
        """updates the total score of a given player given a turn score

        Args:
            player_index (int): index of the player
            score (int): score to be added to the players total score
        """
        self.scores[player_index] += score
    
    
    def get_is_first_turn(self):
        """Returns whether it is the first turn

        Returns:
            bool: is it the first turn?
        """
        return self.is_first_turn

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


    def get_multipliers(self, row, col, word, direction):
        """
        Gets the letter and word multipliers for a potential word.

        Args:
            row (int): The starting row to place the word.
            col (int): The starting column to place the word.
            word (str): The word to be placed.
            direction (str): The direction to place the word. Must be 'across' or 'down'.

        Returns:
            tuple: Two lists of integers representing the letter and word multipliers respectively.
        """
        letter_multiplier_list = []
        word_multiplier_list = []

        for i in range(len(word)):
            if direction == 'across':
                multiplier = self.board[row][col + i]
            elif direction == 'down':
                multiplier = self.board[row + i][col]
            else:
                raise ValueError("Direction must be 'across' or 'down'.")

            # Convert multiplier to number
            if multiplier == '2L':
                letter_multiplier_list.append(2)
                word_multiplier_list.append(1)
            elif multiplier == '3L':
                letter_multiplier_list.append(3)
                word_multiplier_list.append(1)
            elif multiplier == '2W':
                letter_multiplier_list.append(1)
                word_multiplier_list.append(2)
            elif multiplier == '3W':
                letter_multiplier_list.append(1)
                word_multiplier_list.append(3)
            else:  # No multiplier
                letter_multiplier_list.append(1)
                word_multiplier_list.append(1)

        return letter_multiplier_list, word_multiplier_list


    def place_word(self, row, col, word, direction, player, num_letters_from_hand):
        """
        Places a word on the Scrabble board.

        Args:
            row (int): The starting row to place the word.
            col (int): The starting column to place the word.
            word (str): The word to be placed.
            direction (str): The direction to place the word. Must be 'across' or 'down'.
            player(int): The player index
            num_letters_from_hand(int): number of letters in the word coming from the players hand

        Returns:
            bool: True if the word was successfully placed, False otherwise.
        """
        if self.can_play_word(row, col, word, direction):
            letter_multipliers, word_multipliers = self.get_multipliers(row, col, word, direction)
            if direction == 'across':
                for i, letter in enumerate(word):
                    self.board[row][col + i] = letter
                    self.letter_locations.append((row, col + i))
            elif direction == 'down':
                for i, letter in enumerate(word):
                    self.board[row + i][col] = letter
                    self.letter_locations.append((row + i, col))
        
        self.is_first_turn = False
        self.scores[player] = self.calculate_score(word, letter_multipliers, word_multipliers, num_letters_from_hand)
        
        return True


    def display_board(self):
        """
        Prints the current state of the Scrabble board.
        """
        # print to put on a new line
        print()
        # Find the maximum length of the strings in the 2D list
        max_length = max(len(item) for row in self.board for item in row)

        # Iterate over the rows in the 2D list
        for row in self.board:
            # For each item in the row, print it left-justified to the max_length
            # Also add a space for readability
            print(' '.join(item.ljust(max_length) for item in row))
        # for i in range(15):
        #     for j in range(15):
        #         print(self.board[i][j], end=' ')
        #     print()  # Newline after each row
    
    
    def get_board(self):
        """outputs the board

        Returns:
            List[List(str)]: its the board
        """
        return self.board


    def can_play_word(self, row, col, word, direction):
        """checks if a given word can be played from a certain direction

        Args:
            row (int): starting row index
            col (int): starting column index
            word (str): wrod to play
            direction (str): direction of play

        Returns:
            bool: whether the word is valid or not
        """
        word_len = len(word)
        
        # TODO: add a check for valid words from attached words
        
        valid  = False
        # currently limiting search to avoid any crossovers
        if self.is_first_turn:
            return True
        elif direction == 'across':
            # if the length of the word plus the starting position is out of bounds, return False
            if col + len(word) >= 15:
                return False
            # check if there is anything above/below
            for i in range(len(word)):
                if col + 1 < 15 and self.board[row+i][col+1] not in self.valid_play_squares or \
                col - 1 > 0 and self.board[row+i][col+1] not in self.valid_play_squares:
                    return False
                if (row, col + i) in self.letter_locations:
                    valid = True
        elif direction == 'down':
            # if the length of the word plus the starting position is out of bounds, return False
            if row + len(word) >= 15:
                return False
            # check if there is anything above/below
            for i in range(len(word)):
                if row + 1 < 15 and self.board[row+1][col] not in self.valid_play_squares or \
                row - 1 > 0 and self.board[row+1][col] not in self.valid_play_squares:
                    return False
                if (row + i, col) in self.letter_locations:
                    valid = True
        else:
            raise ValueError("Direction must be 'across' or 'down'.")
        return valid

    def calculate_score(self, letters, letter_multiplier_list, word_multiplier_list, num_letters_from_hand):
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
            if num_letters_from_hand == 7:
                score += 50
            return score
