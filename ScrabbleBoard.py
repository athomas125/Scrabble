import json
import random
from Trie import Trie
"""module that creates a scrabble game board
"""

class ScrabbleBoard:
    """
    Represents a Scrabble board.
    """
    def __init__(self, number_of_players, seed=10, dictionary='Collins Scrabble Words (2019).txt'):
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
        self.player_scores = [0] * number_of_players
        self.is_first_turn = True
        self.letter_locations = []
        # a list of board squares string values that are valid to play on top of
        self.valid_play_squares = ['3W', '3L', '2W', '2L', ' ']
        random.seed(seed)
        
        # load the words from the dictionary file into the brute's brain
        self.dictionary = self.load_words_into_trie(dictionary)


        with open('letter_distribution.json', 'r') as f:
            self.letters_to_draw_from = json.load(f)
        with open('letter_points.json', 'r') as f:
            self.letter_scores = json.load(f)


    def load_words_into_trie(self, file_name):
        """
        Reads words from a text file and inserts each word into the Trie.

        Args:
            file_name (str): The name of the file to read the words from.

        Returns:
            Trie: The Trie loaded with words.
        """
        trie = Trie()
        with open(file_name, 'r') as file:
            for line in file:
                word = line.strip()  # remove newline character
                trie.insert(word)
        return trie


    def get_player_scores(self):
        """return the list of scores of the players in the game

        Returns:
            list(int): list of integer scores
        """
        return self.player_scores


    def update_Player_scores(self, player_index, score):
        """updates the total score of a given player given a turn score

        Args:
            player_index (int): index of the player
            score (int): score to be added to the players total score
        """
        self.player_scores[player_index] += score
    
    
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


    def place_word(self, row, col, word, direction, player, hand, fl_ind, fl_let):
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
        score, word, letters_from_hand = self.calculate_turn_score(row, col, word, hand, direction, fl_ind, fl_let)
        
        if self.can_play_word(row, col, word, direction):
            if direction == 'across':
                for i, letter in enumerate(word):
                    if self.board[row][col + i] in self.valid_play_squares:
                        self.board[row][col + i] = letter
                        self.letter_locations.append((row, col + i))
            elif direction == 'down':
                for i, letter in enumerate(word):
                    if self.board[row + i][col] in self.valid_play_squares:
                        self.board[row + i][col] = letter
                        self.letter_locations.append((row + i, col))
        else:
            return False

        self.is_first_turn = False
        self.player_scores[player] += score

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
        if self.is_first_turn:
            return True
        elif direction == 'across':
            # if the length of the word plus the starting position is out of bounds, return False
            if col + len(word)-1 >= 15:
                return False
        elif direction == 'down':
            # if the length of the word plus the starting position is out of bounds, return False
            if row + len(word)-1 >= 15:
                return False
        else:
            raise ValueError("Direction must be 'across' or 'down'.")
        return True

    def calculate_word_score(self, letters, letter_multiplier_list, word_multiplier_list, num_letters_from_hand):
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
        if num_letters_from_hand == 0:
            return 0
        if len(letters) != len(letter_multiplier_list) or len(letters) != len(word_multiplier_list):
            print('invalid letters/multipliers input')
            return -1
        else:
            score = 0
            for letter, multiplier in zip(letters, letter_multiplier_list):
                letter_score = self.letter_scores[letter]
                score += letter_score * multiplier

            word_multiplier = 1
            for multiplier in word_multiplier_list:
                word_multiplier *= multiplier
            score *= word_multiplier
            if num_letters_from_hand == 7:
                score += 50
            return score


    def get_perp_words(self, row, col, word, direction):
        # intention for this is to check if any words that the placed word
        # combines with not in the direction of play are invalid
        # check for validity in cross directions
        perp_locations = []
        perp_words = []
        for i, letter in enumerate(word):
            if direction == 'across':
                perp_word, row_out = self.get_branched_word(row, col+i, 'down', letter)
                if len(perp_word) > 2 or len(perp_word) > 1 and perp_word[1] != '-':
                    perp_locations.append((row_out, col + i, 'down'))
                    perp_words.append(perp_word)
            elif direction == 'down':
                perp_word, col_out = self.get_branched_word(row+i, col, 'across', letter)
                if len(perp_word) > 2 or len(perp_word) > 1 and perp_word[1] != '-':
                    perp_locations.append((row + i, col_out, 'across'))
                    perp_words.append(perp_word)
            else:
                raise ValueError("direction must be 'across' or 'down'.")
        return perp_locations, perp_words


    def get_branched_word(self, row, col, direction, letter):
        # gets the word being formed by the letter placed in the row/col index in direction given
        out = ""
        if direction == 'down':
            start = row
            i = 1
            # get the first index of the branched word
            while row-i >= 0:
                if self.board[row-i][col] not in self.valid_play_squares:
                    start = row-i
                    i += 1
                else:
                    break
            ind = start
            # get the fully formed word
            while ind < 15 and (self.board[ind][col] not in self.valid_play_squares or ind == row):
                if ind == row:
                    out += letter
                else:
                    out += self.board[ind][col][0]
                ind += 1
        elif direction == 'across':
            start = col
            i = 1
            # get the first index of the branched word
            while col-i >= 0:
                if self.board[row][col-i] not in self.valid_play_squares:
                    start = col-i
                    i += 1
                else:
                    break
            ind = start
            # get the fully formed word
            while ind < 15 and (self.board[row][ind] not in self.valid_play_squares or ind == col):
                if ind == col:
                    out += letter
                else:
                    out += self.board[row][ind][0]
                ind += 1
        return out, start


    def check_validity(self, words):
        for word in words:
            word = word.replace('-','')
            valid_word = self.dictionary.search(word)
            if not valid_word[0]:
                return False
        return True
    
    
    def calculate_turn_score(self, row, col, word, hand, direction, fl_ind, fl_let):
        score = 0
        # this checks the validity of all the perpendicular words and adds them to a list of tuples
        # in order to calculate their contribution to the score
        perp_locations, perp_words = self.get_perp_words(row, col, word, direction)
        valid = self.check_validity(perp_words)
        if not valid:
            return 0, None, None
        else:
            for i in range(len(perp_words)):
                perp_row = perp_locations[i][0]
                perp_col = perp_locations[i][1]
                perp_dir = perp_locations[i][2]
                perp_word = perp_words[i]
                letter_multipliers, word_multipliers = self.get_multipliers(perp_row, perp_col, perp_word, perp_dir)
                perp_word, letters_from_hand = self.get_cross_score_input(row, col, perp_row, perp_col, perp_word, perp_dir, hand)
                score += self.calculate_word_score(perp_word, letter_multipliers, word_multipliers, len(letters_from_hand))
            
        letter_multipliers, word_multipliers = self.get_multipliers(row, col, word, direction)
        word, letters_from_hand = self.get_score_input(word, hand, fl_ind, fl_let)
        score += self.calculate_word_score(word, letter_multipliers, word_multipliers, len(letters_from_hand))
        return score, word, letters_from_hand


    def get_score_input(self, word, hand, fl_ind=[], fl_let=[]):
        # creating this function in order to handle blanks and create two output lists
        # first output list is the word as a list, and the second is the letters from the hand as a list
        # changing word from string to a list to properly handle blanks
        word = list(word)
        letters_from_hand = []
        for i, letter in enumerate(word):
            if i in fl_ind:
                word[i] = fl_let[fl_ind.index(i)]
            else:
                # adding in length check to prevent constant appending of '-'
                if letter not in hand and len(letter)==1:
                    word[i] = letter + '-'
                elif len(letter) == 1:
                    # TODO: need to add in a check here to handle if there are multiple of the same
                    # letter in the word, and one of them is a blank
                    instances_in_hand = len([i for i in range(len(hand)) if hand[i] == letter])
                    instances_in_lfh = len([i for i in range(len(letters_from_hand)) if letters_from_hand[i] == letter])
                    if instances_in_hand == instances_in_lfh:
                        word[i] = letter + '-'
                    
                letters_from_hand.append(word[i])

        return word, letters_from_hand


    def get_cross_score_input(self, row, col, perp_row, perp_col, perp_word, perp_dir, hand):
        # gets intersection between words and check if it is an already placed letter or not
        word = list(perp_word)
        if perp_dir == 'across':
            if self.board[perp_row][col] in self.valid_play_squares:
                if perp_word[col-perp_col] not in hand:
                    word[col-perp_col] = word[col-perp_col] + '-'
                return word, word[col-perp_col]
            else:
                return word, []
        elif perp_dir == 'down':
            if self.board[row][perp_col] in self.valid_play_squares:
                if perp_word[row-perp_row] not in hand:
                    word[row-perp_row] = word[row-perp_row] + '-'
                return word, word[row-perp_row]
            else:
                return word, []
            
        else:
            raise ValueError("direction must be 'across' or 'down'")