from copy import deepcopy
import string
from ScrabbleBoard import ScrabbleBoard

class Brute:
    """
    game player that uses a brute force method
    """
    def __init__(self, game, number, hand=None):
        self.game = game
        self.number = number
        # TODO: remove this once debugged
        if not hand:
            self.hand = self.game.draw_letters(7)
        else:
            self.hand = hand
            self.hand += self.game.draw_letters(7-len(hand))


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
            prefix += fixed_letters[fixed_letter_indices.index(len(prefix))][0]

        if prefix:
            valid_word, valid_prefix = self.game.dictionary.search(prefix)
            if valid_word:
                if len(fixed_letter_indices) == 0:
                    if prefix not in words:
                        words.add(prefix)
                elif len(prefix) >= fixed_letter_indices[0] and prefix not in words:
                    # this line is here to make sure at least one fixed letter is contained in the word
                    words.add(prefix)
            if not valid_prefix:
                return words

        for i, letter in enumerate(letters):
            new_letters = list(letters)
            new_letters.pop(i)
            if letter == ' ':
                for wildcard in string.ascii_uppercase:
                    self.get_words(new_letters, prefix + wildcard, words, fixed_letter_indices=fixed_letter_indices, fixed_letters=fixed_letters)
            else:
                self.get_words(new_letters, prefix + letter, words, fixed_letter_indices=fixed_letter_indices, fixed_letters=fixed_letters)
        return words

    def get_prefixes(self, letters, prefix='', prefixes = None):
        if prefixes is None:
            prefixes = set()

        if prefix:
            valid_word, valid_prefix = self.game.dictionary.search(prefix)
            if not valid_prefix:
                return prefixes
            else:
                prefixes.add(prefix)

        for i, letter in enumerate(letters):
            new_letters = list(letters)
            new_letters.pop(i)
            if letter == ' ':
                for wildcard in string.ascii_uppercase:
                    self.get_prefixes(new_letters, prefix + wildcard, prefixes)
            else:
                self.get_prefixes(new_letters, prefix + letter, prefixes)
        return prefixes


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
            # sorting first by alphabetical order and then by length in order
            # to consistently order words
            valid_words = sorted(valid_words)
            valid_words = sorted(valid_words, key=len)[::-1]
            for word in valid_words:
                # simplifying by placing the first word horizontally always
                row = 7
                for col in range(7 - (len(word)-1), 8):
                    letter_multipliers, word_multipliers = self.game.get_multipliers(row, col, word, 'across')
                    word, letters_from_hand = self.game.get_score_input(word, self.hand)
                    score = self.game.calculate_word_score(word, letter_multipliers, word_multipliers, len(letters_from_hand))
                    if score > best_score:
                        best_word = word
                        best_letters_from_hand = best_word
                        best_score = score
                        best_position = (row, col)
                        best_direction = 'across'
                        best_fl_ind = []
                        best_fl_let = []
        else:
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
            searched_rows = []
            searched_cols = []
            # TODO: check for overwriting of other words
            for i, item in enumerate(self.game.letter_locations):
                row = item[0]
                col = item[1]
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
                    if start > 0:
                        fl_ind = [x - start for x in fl_ind]
                    for j in range(start, maxl+1):
                        if j > start:
                            # shift the index down by one because we are moving our start position
                            # shift through continuous blocks of letters
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
                        # adding sorting here to have consistent ordering during search
                        words = sorted(words)
                        words = sorted(words, key=len)[::-1]
                        for word in words:
                            if self.game.can_play_word(row, col, word, direction):
                                score, word, letters_from_hand = self.game.calculate_turn_score(\
                                    row, col, word, self.hand, direction, fl_ind, fl_let)
                                if score > best_score:
                                    best_word = word
                                    best_letters_from_hand = letters_from_hand
                                    best_score = score
                                    best_position = (row, col)
                                    best_direction = direction
                                    best_fl_ind = fl_ind
                                    best_fl_let = fl_let
        
        return best_word, best_position, best_direction, best_letters_from_hand, best_fl_ind, best_fl_let

    def do_turn(self):
        """turn execution
        """
        word, position, direction, letters_from_hand, fl_ind, fl_let = self.find_best_play()
        pre_points = self.game.get_player_scores()[self.number]
        self.game.place_word(position[0], position[1], word, direction, self.number, self.hand, fl_ind, fl_let)
        self.game.display_board()
        points = self.game.get_player_scores()[self.number] - pre_points
        print("hand was: " + str(self.hand) + "\nword: "+ str(word) + "\nnumber of points this turn: " + str(points) + "\nnumber of points: " + str(self.game.get_player_scores()[self.number]))
        
        for letter in letters_from_hand:
            if letter not in self.hand:
                letter = ' '
            index = self.hand.index(letter)
            self.hand = self.hand[0:index] + self.hand[index + 1:]
        self.hand += self.game.draw_letters(len(letters_from_hand))
        print("new hand" + str(self.hand))

# initialize the board
Game = ScrabbleBoard(2, seed=11)
brute_1 = Brute(Game, 0)
brute_2 = Brute(Game, 1)
go_again = 'yep'
i = 0
while go_again != 'stop':
    if i == 0:
        brute_1.do_turn()
        i = 1
    elif i == 1:
        brute_2.do_turn()
        i = 0
    go_again = input("type stop to stop, otherwise it will do another turn: ")
