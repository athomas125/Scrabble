import json
import random
from Trie import Trie
"""module that creates a scrabble game board
"""

class ScrabbleBoard:
    """
    Represents a Scrabble board.
    """
    def __init__(self,
                 number_of_players,
                 seed=10,
                 dictionary='Collins Scrabble Words (2019).txt'):
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
        self.number_of_players = number_of_players
        self.player_scores = [0] * number_of_players
        self.is_first_turn = True
        self.is_game_over = False
        # a list of tuples containing a the row and column locations of letters on the board
        self.letter_locations = []
        # a dictionary with a tuple as the key, where the tuple is the row and column of a
        # playable location on the board
        # initializing with 7,7 because you must start playing on the central square
        self.required_play_locations = {(7,7): True}
        # a list of board squares string values that are valid to play on top of
        self.valid_play_contents = {'3W': True, '3L': True, '2W': True, '2L': True, ' ': True}
        random.seed(seed)

        # load the words from the dictionary file into the brute's brain
        self.dictionary = self.load_words_into_trie(dictionary)


        with open('letter_distribution.json', 'r') as f:
            self.letters_to_draw_from = json.load(f)
        with open('letter_points.json', 'r') as f:
            self.letter_scores = json.load(f)


    def load_words_into_trie(self,
                             file_name):
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


    def update_player_scores(self,
                             player_index,
                             score):
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


    def draw_letters(self,
                     num_letters):
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


    def get_num_letters_left(self):
        """Returns the number of letters left in the draw pile

        Returns:
            int: number of letters left in the draw pile
        """
        # Flatten the dictionary into a list of letters
        letters_left = [letter for letter, count in self.letters_to_draw_from.items() for _ in range(count)]
        return len(letters_left)


    def get_multipliers(self,
                        row,
                        col,
                        word,
                        direction):
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


    def place_word(self,
                   row,
                   col,
                   word,
                   direction,
                   player,
                   hand):
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
        score, word, letters_from_hand = self.calculate_turn_score(row, col, word, hand, direction)
        if self.can_play_word(row, col, word, direction):
            if direction == 'across':
                for i, letter in enumerate(word):
                    if self.board[row][col + i] in self.valid_play_contents:
                        self.board[row][col + i] = letter
                        self.letter_locations.append((row, col + i))
                        if (row, col+i) in self.required_play_locations:
                            del self.required_play_locations[(row,col+i)]
            elif direction == 'down':
                for i, letter in enumerate(word):
                    if self.board[row + i][col] in self.valid_play_contents:
                        self.board[row + i][col] = letter
                        self.letter_locations.append((row + i, col))
                        if (row+i, col) in self.required_play_locations:
                            del self.required_play_locations[(row+i,col)]
        else:
            return False

        self.add_new_valid_locations(row, col, direction, len(word))

        self.is_first_turn = False
        self.player_scores[player] += score

        if len(letters_from_hand) == len(hand):
            if self.get_num_letters_left() == 0:
                print("Final Word: " + str(word))
                self.game_over()
                return True
        else:
            return True


    def add_new_valid_locations(self,
                                row,
                                col,
                                direction,
                                num_squares):
        """this function evaluates the letters adjacent to a newly placed word
        and determines if they should be added to the valid_play_squares dict

        Args:
            row (int): placement row
            col (int): placement columns
            direction (str): direction of play
            num_squares (int): length of played word

        Raises:
            ValueError: raises when direction is not 'across' or 'down'
        """

        for j in [-1, 1]:
            if direction == 'across':
                # this code checks the squares along the word perpendicular to the play direction
                if row + j >= 0 and row + j <= 14:
                    row_eval = row + j
                    for i in range(num_squares):
                        col_eval = col + i
                        if self.board[row_eval][col_eval] in self.valid_play_contents:
                            self.required_play_locations[(row_eval,col_eval)] = True
                # this code checks the squares before and after the word in the play direction
                if j == -1:
                    col_eval = col+j
                    if col_eval < 0:
                        continue
                    elif self.board[row][col_eval] in self.valid_play_contents:
                        self.required_play_locations[(row,col_eval)] = True
                else:
                    col_eval = col+num_squares
                    if col_eval > 14:
                        continue
                    elif self.board[row][col_eval] in self.valid_play_contents:
                        self.required_play_locations[(row,col_eval)] = True

            elif direction == 'down':
                if col + j >= 0 and col + j <= 14:
                    col_eval = col + j
                    for i in range(num_squares):
                        row_eval = row + i
                        if self.board[row_eval][col_eval] in self.valid_play_contents:
                            self.required_play_locations[(row_eval,col_eval)] = True
                # this code checks the squares before and after the word in the play direction
                if j == -1:
                    row_eval = row+j
                    if row_eval < 0:
                        continue
                    elif self.board[row_eval][col] in self.valid_play_contents:
                        self.required_play_locations[(row_eval,col)] = True
                else:
                    row_eval = row+num_squares
                    if row_eval > 14:
                        continue
                    elif self.board[row_eval][row_eval] in self.valid_play_contents:
                        self.required_play_locations[(row_eval,col)] = True
            else:
                raise ValueError("Direction must be 'across' or 'down'.")


    def game_over(self):
        """This function will be called when the game is complete
        """        
        self.is_game_over = True
        self.display_board()
        print("Final Score: ")
        for player in range(self.number_of_players):
            print("Player " + str(player+1) + ": " + str(self.player_scores[player]))
        print("Total Points: " + str(sum(self.player_scores)))
        print("GAME OVER!!!!!!!!!!!!!!\
            \nPlayer "\
            + str(self.player_scores.index(max(self.player_scores))+1)\
            + " is the Winner!")
        # TODO: maybe add a highest scoring word
        # TODO: largest single turn differential
        # TODO: average letters placed per turn
        # TODO: number of points in hand total
        # TODO: other metrics


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


    def get_board(self):
        """outputs the board

        Returns:
            List[List(str)]: its the board
        """
        return self.board


    def can_play_word(self,
                      row,
                      col,
                      word,
                      direction):
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
            for i in range(len(word)):
                if (row, col+i) in self.required_play_locations:
                    return True
        elif direction == 'down':
            # if the length of the word plus the starting position is out of bounds, return False
            if row + len(word)-1 >= 15:
                return False
            for i in range(len(word)):
                if (row+i, col) in self.required_play_locations:
                    return True
        else:
            raise ValueError("Direction must be 'across' or 'down'.")
        return False

    def calculate_word_score(self,
                             letters,
                             letter_multiplier_list,
                             word_multiplier_list,
                             num_letters_from_hand):
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


    def get_perp_words(self,
                       row,
                       col,
                       word,
                       direction):
        """gets all words formed perpendicular to the direction of play

        Args:
            row (int): row of first letter of word
            col (int): column of first letter of word
            word (str): word to evaluate
            direction (str): direction of play

        Raises:
            ValueError: if direction is not across or down

        Returns:
            tuple (perp_locations, perp_words):
                perp_locations (List[tuple]): list of the
                    location and direction of each word listed
                    in perp_words
                perp_words (List[List]): list of words formed by play
        """        
        # intention for this is to check if any words that the placed word
        # combines with not in the direction of play are invalid
        # check for validity in cross directions
        perp_locations = []
        perp_words = []
        for i, letter in enumerate(word):
            if direction == 'across':
                perp_word, row_out = self.get_branched_word(row, col+i, 'down', letter)
                if len(perp_word) > 1:
                    perp_locations.append((row_out, col + i, 'down'))
                    # wrapping perp_word in a list so enumerate in calculate turn 
                    # score doesn't loop through the letters
                    perp_words.append([perp_word])
            elif direction == 'down':
                perp_word, col_out = self.get_branched_word(row+i, col, 'across', letter)
                if len(perp_word) > 1:
                    perp_locations.append((row + i, col_out, 'across'))
                    # wrapping perp_word in a list so enumerate in calculate turn 
                    # score doesn't loop through the letters
                    perp_words.append([perp_word])
            else:
                raise ValueError("direction must be 'across' or 'down'.")
        return perp_locations, perp_words


    def get_branched_word(self,
                          row,
                          col,
                          direction,
                          letter):
        """Gets the word being formed by the letter placed in the row/col index
        in the direction given

        Args:
            row (int): row of first letter of word
            col (int): column of first letter of word
            direction (str): direction of play
            letter (char): letter played

        Returns:
            tuple (out, start):
                out (str): word formed by letter placement
                start(int): index of the first letter in the word in
                    the direction of play
        """
        # gets the word being formed by the letter placed in the row/col index in direction given
        out = ""
        if direction == 'down':
            start = row
            i = 1
            # get the first index of the branched word
            while row-i >= 0:
                if self.board[row-i][col] not in self.valid_play_contents:
                    start = row-i
                    i += 1
                else:
                    break
            ind = start
            # get the fully formed word
            while ind < 15 and (self.board[ind][col] not in self.valid_play_contents or ind == row):
                if ind == row:
                    out += letter[0]
                else:
                    out += self.board[ind][col][0]
                ind += 1
        elif direction == 'across':
            start = col
            i = 1
            # get the first index of the branched word
            while col-i >= 0:
                if self.board[row][col-i] not in self.valid_play_contents:
                    start = col-i
                    i += 1
                else:
                    break
            ind = start
            # get the fully formed word
            while ind < 15 and (self.board[row][ind] not in self.valid_play_contents or ind == col):
                if ind == col:
                    out += letter[0]
                else:
                    out += self.board[row][ind][0]
                ind += 1
        return out, start


    def check_validity(self,
                       words):
        """This checks whether a given word is in the dictionary, and hence valid

        Args:
            words (list): word contained in a list (ie. ['word'])

        Returns:
            bool: Whether or not the given word is valid
        """        
        for word in words:
            valid_word = self.dictionary.search(word[0])
            if not valid_word[0]:
                return False
        return True
    
    
    def calculate_turn_score(self,
                             row,
                             col,
                             word,
                             hand,
                             direction):
        """Calculates the full score from the turn for the word being played

        Args:
            row (int): row of first letter of word
            col (int): column of first letter of word
            word (str): word to play
            hand (List): letters in hand
            direction (str): direction of play

        Returns:
            tuple (score, word, letters_from_hand):
                score (int): score of play
                word (List[char]): word played in the primary direction of play
                    formatted as a list of characters
                letters_from_hand(List[char]): letters in the played word that
                    come from the player's hand
        """
        score = 0
        # this checks the validity of all the perpendicular words and adds them to a list of tuples
        # in order to calculate their contribution to the score
        perp_locations, perp_words = self.get_perp_words(row, col, word, direction)
        valid = self.check_validity(perp_words)
        if not valid:
            return 0, None, None
        else:
            for i, perp_word in enumerate(perp_words):
                perp_row = perp_locations[i][0]
                perp_col = perp_locations[i][1]
                perp_dir = perp_locations[i][2]
                perp_word = perp_word[0]
                letter_multipliers, word_multipliers = self.get_multipliers(perp_row,\
                                                                            perp_col,\
                                                                            perp_word,\
                                                                            perp_dir)
                perp_word, letters_from_hand = self.get_score_input(perp_row,\
                                                                    perp_col,\
                                                                    perp_dir,\
                                                                    perp_word,\
                                                                    hand)
                score += self.calculate_word_score(perp_word,\
                                                    letter_multipliers,\
                                                    word_multipliers,\
                                                    len(letters_from_hand))

        letter_multipliers, word_multipliers = self.get_multipliers(row, col, word, direction)
        word, letters_from_hand = self.get_score_input(row, col, direction, word, hand)
        score += self.calculate_word_score(word,\
                                            letter_multipliers,\
                                            word_multipliers,\
                                            len(letters_from_hand))
        return score, word, letters_from_hand

    def get_score_input(self, row, col, direction, word, hand):
        """Gets the word formatted as a list to handle blanks

        Args:
            row (int): row of first letter of word
            col (int): column of first letter of word
            word (str): word to play
            direction (str): direction of play
            hand (List): letters in hand

        Raises:
            ValueError: if direction is not across or down

        Returns:
            tuple (word, letters_from_hand):
                word (List[char]): word played in the primary direction of play
                    formatted as a list of characters
                letters_from_hand(List[char]): letters in the played word that
                    come from the player's hand
        """
        # this function should score calculate for a word placement
        word = list(word)
        letters_from_hand = []
        for ind, letter in enumerate(word):
            if direction == 'across':
                if self.board[row][col+ind] not in self.valid_play_contents:
                    word[ind] = self.board[row][col+ind]
                else:
                    # adding in length check to prevent constant appending of '-'
                    if letter not in hand:
                        word[ind] = letter + '-'
                    else:
                        instances_in_hand = len([x for x in range(len(hand)) if hand[x] == letter])
                        instances_in_lfh = len([x for x in range(len(letters_from_hand))\
                            if letters_from_hand[x] == letter])
                        if instances_in_hand == instances_in_lfh:
                            word[ind] = letter + '-'
                    letters_from_hand.append(word[ind])
            elif direction == 'down':
                if self.board[row+ind][col] not in self.valid_play_contents:
                    word[ind] = self.board[row+ind][col]
                else:
                    # adding in length check to prevent constant appending of '-'
                    if letter not in hand:
                        word[ind] = letter + '-'
                    else:
                        instances_in_hand = len([x for x in range(len(hand)) if hand[x] == letter])
                        instances_in_lfh = len([x for x in range(len(letters_from_hand))\
                            if letters_from_hand[x] == letter])
                        if instances_in_hand == instances_in_lfh:
                            word[ind] = letter + '-'
                    letters_from_hand.append(word[ind])
            else:
                raise ValueError("direction must be 'across' or 'down'")
        return word, letters_from_hand
