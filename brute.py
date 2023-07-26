from copy import deepcopy
import string
from Trie import Trie
from ScrabbleBoard import ScrabbleBoard

class Brute:
    """
    game player that uses a brute force method
    """
    def __init__(self, game, number):
        # load the words from the dictionary file into the brute's brain
        self.brain = self.load_words_into_trie('Collins Scrabble Words (2019).txt')
        self.game = game
        self.hand = self.game.draw_letters(7)
        self.number = number


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


    def get_words(self, letters, prefix='', words=None, fixed_letter_indices=None, fixed_letters=None):
        if bool(fixed_letter_indices) != bool(fixed_letters):
            raise ValueError("Both fixed_letter_indices and fixed_letters should be populated if populating one")
        if fixed_letter_indices and fixed_letters:
            if len(fixed_letter_indices) != len(fixed_letters):
                raise ValueError("Mismatching size of fixed letter lists")
        if words is None:
            words = set()
        if fixed_letters is None:
            fixed_letters = []
            fixed_letter_indices = []

        while len(prefix) in fixed_letter_indices:
            prefix += fixed_letters[fixed_letter_indices.index(len(prefix))]

        if prefix:
            valid_word, valid_prefix = self.brain.search(prefix)
            if valid_word:
                if len(fixed_letter_indices) == 0:
                    words.add(prefix)
                else:
                    if len(prefix) >= fixed_letter_indices[0]:
                        words.add(prefix)
            if not valid_prefix:
                return words

        for i, letter in enumerate(letters):
            new_letters = list(letters)
            new_letters.pop(i)
            if letter == ' ':
                for wildcard in string.ascii_uppercase:
                    self.get_words(new_letters, prefix + wildcard, words)
            else:
                self.get_words(new_letters, prefix + letter, words)
        return words

    def get_prefixes(self, letters, prefix='', prefixes = None):
        if prefixes is None:
            prefixes = set()

        if prefix:
            valid_word, valid_prefix = self.brain.search(prefix)
            if not valid_prefix:
                return prefixes

        for i, letter in enumerate(letters):
            new_letters = list(letters)
            new_letters.pop(i)
            if letter == ' ':
                for wildcard in string.ascii_uppercase:
                    self.get_words(new_letters, prefix + wildcard, prefixes)
            else:
                self.get_words(new_letters, prefix + letter, prefixes)
        return prefixes

    def check_validity(self, row, col, word, direction):
        # intention for this is to check if any words that the placed word 
        # combines with not in the direction of play are invalid
        # check for validity in cross directions
        for i, letter in enumerate(word):
            if direction == 'across':
                combined_word = self.get_branched_word(row, col+i, 'down', letter)
            elif direction == 'down':
                combined_word = self.get_branched_word(row+i, col, 'across', letter)
            else:
                raise ValueError("direction must be 'across' or 'down'.")
            # check if combined_word exists and is valid
            if len(combined_word) <= 1:
                continue
            else:
                valid_word = self.brain.search(combined_word)
                if not valid_word[0]:
                    return False
        # check for validity in the placement direction
        self.get_branched_word(row, col, direction, word)
        return True

    def get_branched_word(self, row, col, direction, letter):
        # gets the word being formed by the letter placed in the row/col index in direction given
        # TODO: test that this works properly
        out = ""
        if direction == 'down':
            start = row
            i = 1
            # get the first index of the branched word
            while row-i >= 0:
                if self.game.board[row-i][col] not in self.game.valid_play_squares:
                    start = row-i
                    i += 1
                else:
                    break
            ind = start
            # get the fully formed word
            while ind < 15 and (self.game.board[ind][col] not in self.game.valid_play_squares or ind == row):
                if ind == row:
                    out += letter
                else:
                    out += self.game.board[ind][col]
                ind += 1
        elif direction == 'across':
            start = col
            i = 1
            # get the first index of the branched word
            while col-i >= 0:
                if self.game.board[row][col-i] not in self.game.valid_play_squares:
                    start = col-i
                    i += 1
                else:
                    break
            ind = start
            # get the fully formed word
            while ind < 15 and (self.game.board[row][ind] not in self.game.valid_play_squares or ind == col):
                if ind == col:
                    out += letter
                else:
                    out += self.game.board[row][ind]
                ind += 1
        return out

    def find_best_play(self):
        """
        Finds the best place to play a word from the given list of words.

        Returns:
            tuple: A tuple containing the best word to play, its score, starting position (row, col), and direction.
        """
        best_word = None
        best_score = 0
        best_position = None
        best_direction = None
        best_letters_from_hand = None

        if self.game.get_is_first_turn():
            # just want to calculate the highest score word in our hand
            valid_words = self.get_words(self.hand)
            valid_words = sorted(valid_words, key=len)[::-1]
            for word in valid_words:
                # simplifying by placing the first word horizontally always
                row = 7
                letters_from_hand = word
                for col in range(7 - (len(word)-1), 8):
                    letter_multipliers, word_multipliers = self.game.get_multipliers(row, col, word, 'across')
                    score = self.game.calculate_score(word, letter_multipliers, word_multipliers, len(letters_from_hand))
                    if score > best_score:
                        best_word = word
                        best_letters_from_hand = best_word
                        best_score = score
                        best_position = (row, col)
                        best_direction = 'across'
        else:
            # TODO: Implement this
            # compute all words that are made out of our letters so that 
            # we have a set of prefixes to use to check for more words
            prefixes = self.get_prefixes(self.hand)
            sorted_prefixes = {}
            for prefix in prefixes:
                length = len(prefix)
                if length not in sorted_prefixes:
                    sorted_prefixes[length] = []
                sorted_prefixes[length].append(prefix)

            # here you want to check both directions and all possible play locations
            # TODO: update full board search to just search to play off where there are letters
            searched_rows = []
            searched_cols = []
            # TODO: fix overwriting of other words
            for i, item in enumerate(self.game.letter_locations):
                row = item[0]
                col = item[1]
                letter = self.game.board[row][col]
                for direction in ['across', 'down']:
                    # TODO: update this so that it accounts for other words on the board
                    fl_ind = []
                    fl_let = []
                    ind = 0
                    minl = 15
                    maxl = -1
                    # using prev_blank sets maxl to be the first letter in of the final string
                    # of connected letters in desired direction
                    prev_blank = -1
                    # want to check to see if there are any intersecting letters in the play direction
                    if direction == 'across':
                        if row not in searched_rows:
                            searched_rows.append(row)
                            for j in range(15):
                                if self.game.board[row][j] not in self.game.valid_play_squares:
                                    fl_ind.append(j)
                                    fl_let.append(self.game.board[row][j])
                                    ind += 1
                                    if minl == 15:
                                        minl = j
                                    if j - prev_blank == 1:
                                        maxl = j
                                else:
                                    prev_blank = j
                    elif direction == 'down':
                        if col not in searched_cols:
                            searched_cols.append(col)
                            for j in range(15):
                                if self.game.board[j][col] not in self.game.valid_play_squares:
                                    fl_ind.append(j)
                                    fl_let.append(self.game.board[j][col])
                                    if minl == 15:
                                        minl = j
                                    if j - prev_blank == 1:
                                        maxl = j
                                else:
                                    prev_blank = j
                    else:
                        continue
                    # if no min is set, then there are no letters in this search space
                    if minl == 15:
                        continue
                    
                    start = max(minl-7, 0)
                    for j in range(start, maxl+1):
                        if j > start:
                            # shift the index down by one because we are moving our start position
                            # TODO: check this
                            fl_ind = [x - 1 for x in fl_ind]
                            if len(fl_ind) > 0 and fl_ind[0] < 0:
                                del fl_ind[0]
                                del fl_let[0]
                                continue
                        # Check if word can be played in this position
                        if direction == 'across':
                            col = j
                        else:
                            row = j
                        
                        # TODO: there may be a faster way to form words here where you also account for the 
                        # different directions and invalidate certain letters in certain positions or something
                        # maybe could do something with suffixes
                        # TODO: check that the correct words are gotten
                        
                        # sorted prefix stuff makes it so you don't have to search through all prefixes
                        words = []
                        if fl_ind[0] in sorted_prefixes:
                            for p in sorted_prefixes[fl_ind[0]]:
                                # TODO: self.hand needs to change to letters
                                letters_left = self.hand
                                for char in p:
                                    if char in letters_left:
                                        ll_ind = letters_left.index(char)
                                    else:
                                        ll_ind = letters_left.index(' ')
                                    letters_left = letters_left[:ll_ind] + letters_left[ll_ind+1:]
                                words += self.get_words(letters_left, prefix=p, fixed_letter_indices=fl_ind, fixed_letters=fl_let)
                        elif fl_ind[0] == 0:
                            words += self.get_words(self.hand, fixed_letter_indices=fl_ind, fixed_letters=fl_let)
                        for word in words:
                            if self.game.can_play_word(row, col, word, direction) and self.check_validity(row, col, word, direction):
                                letter_multipliers, word_multipliers = self.game.get_multipliers(row, col, word, direction)
                                # Calculate score
                                # use the fixed letters to determine the letters from hand
                                letters_from_hand = word
                                for k in reversed(fl_ind):
                                    if k < len(word):
                                        letters_from_hand = letters_from_hand[:k] + letters_from_hand[k+1:]
                                # TODO: somehow update the calculate score call to handle putting down blanks
                                score = self.game.calculate_score(word, letter_multipliers, word_multipliers, len(letters_from_hand))
                                if score > best_score:
                                    best_word = word
                                    best_letters_from_hand = letters_from_hand
                                    best_score = score
                                    best_position = (row, col)
                                    best_direction = direction
        
        return best_word, best_position, best_direction, best_letters_from_hand

    def do_turn(self):
        """turn execution
        """
        word, position, direction, letters_from_hand = self.find_best_play()
        self.game.place_word(position[0], position[1], word, direction, self.number, len(letters_from_hand))
        temp_hand = deepcopy(self.hand)
        for letter in letters_from_hand:
            if letter not in self.hand:
                letter = ' '
            index = self.hand.index(letter)
            self.hand = self.hand[0:index] + self.hand[index + 1:]
        self.game.display_board()
        print("hand was: " + str(temp_hand) + "\nword: "+ word + "\nnumber of points: " + str(self.game.get_player_scores()[self.number]))
        self.hand += self.game.draw_letters(len(letters_from_hand))
        print("new hand" + str(self.hand))

# initialize the board
Game = ScrabbleBoard(1)
brute_1 = Brute(Game, 1)
brute_2 = Brute(Game, 2)
go_again = 'yep'
while go_again != 'stop':
    brute_1.do_turn()
    brute_2.do_turn()
    go_again = input("type stop to stop, otherwise it will do another turn: ")
