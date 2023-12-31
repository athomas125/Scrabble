import string
from ScrabbleBoard import ScrabbleBoard

class Brute:
    """
    game player that uses a brute force method
    """
    def __init__(self,
                 game,
                 number,
                 hand=None):
        self.game = game
        self.number = number
        self.playing = True
        if not hand:
            self.hand = self.game.draw_letters(7)
        else:
            self.hand = hand
        self.state = {'board': [], 'letters_left': [], 'letters_in_hand': [], 'reward': 0}


    def update_state(self):
        self.state['board'] = self.game.board_state
        self.state['letters_left'] = self.game.letters_not_on_board
        self.state['letters_in_hand'] = [0]*27

        for letter in self.hand:
            if letter != ' ':
                self.state['letters_left'][ord(letter)-64] -= 1
                self.state['letters_in_hand'][ord(letter)-64] += 1
            else:
                self.state['letters_left'][0] -= 1
                self.state['letters_in_hand'][0] += 1
                
    
    def get_state(self):
        return self.state
    
    
    def update_game(self, game):
        self.game = game


    def get_words(self,
                  letters,
                  prefix='',
                  words=None,
                  fixed_letter_indices=None,
                  fixed_letters=None):
        """gets all words given set of letters, prefixes and fixed letters

        Args:
            letters (List): list of letters to spell words with
            prefix (str, optional): fixed prefix of word. Defaults to ''.
            words (List[str], optional): list of valid words. Defaults to None.
            fixed_letter_indices (list[int], optional): list of indices of fixed letters. Defaults to None.
            fixed_letters (List[char], optional): list of fixed letters. Defaults to None.

        Raises:
            ValueError: if fixed letters indices and fixed letters aren't both populated
            ValueError: if fixed letters indices and fixed letters aren't the same length

        Returns:
            List[str]: list of valid words
        """        
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
            valid_word, valid_prefix = self.game._dictionary.search(prefix)
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
                    self.get_words(new_letters,
                                   prefix + wildcard, words,
                                   fixed_letter_indices=fixed_letter_indices,
                                   fixed_letters=fixed_letters)
            else:
                self.get_words(new_letters,
                               prefix + letter,
                               words,
                               fixed_letter_indices=fixed_letter_indices,
                               fixed_letters=fixed_letters)
        return words

    def get_prefixes(self,
                     letters,
                     prefix='',
                     prefixes = None):
        """gets all valid prefixes given set of letters

        Args:
            letters (List[char]): letters to form prefixes with
            prefix (str, optional): fixed prefix to use. Defaults to ''.
            prefixes (List[str], optional): list of valid prefixes. Defaults to None.

        Returns:
            List[str]: list of valid prefixes
        """
        if prefixes is None:
            prefixes = set()

        if prefix:
            valid_word, valid_prefix = self.game._dictionary.search(prefix)
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
            tuple: A tuple containing the best word to play, its score, 
                starting position (row, col), and direction.
        """
        best_word = None
        best_score = 0
        best_position = None
        best_direction = None
        best_letters_from_hand = None

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
        searched_rows = set()
        searched_cols = set()
        
        for location in self.game.required_play_locations:
            row = location[0]
            col = location[1]
            for direction in ['across', 'down']:
                fl_ind = []
                fl_let = []
                minl = 15
                maxl = -1
                # using prev_blank sets maxl to be the first letter in of the final string
                # of connected letters in desired direction
                # want to check to see if there are any intersecting letters in the play direction
                
                # TODO: want to add some way to check the cross direction and narrow down the
                # letters that can be played there, this should interface with fl_ind, want to
                # loop through all of the combinations of letters in hand that can be played
                prev_blank = -1
                if direction == 'across':
                    if row not in searched_rows:
                        searched_rows.add(row)
                        for j in range(15):
                            if (row, j) in self.game.required_play_locations:
                                if minl == 15:
                                    minl = j
                                maxl = j
                                prev_blank = j
                            elif self.game.board[row][j] not in self.game.valid_play_contents:
                                fl_ind.append(j)
                                fl_let.append(self.game.board[row][j])
                                if minl == 15:
                                    minl = j
                                if j - prev_blank == 1:
                                    maxl = j
                            else:
                                prev_blank = j
                elif direction == 'down':
                    if col not in searched_cols:
                        searched_cols.add(col)
                        for j in range(15):
                            if (j, col) in self.game.required_play_locations:
                                if minl == 15:
                                    minl = j
                                maxl = j
                                prev_blank = j
                            elif self.game.board[j][col] not in self.game.valid_play_contents:
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
                # if no min is set, then you can't play in this space or
                # the row/col has already been searched
                if minl == 15:
                    continue
                
                if self.game.get_is_first_turn():
                    start = max(minl-6, 0)
                else:
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
                    if len(fl_ind) > 0 and fl_ind[0] in sorted_prefixes:
                        for p in sorted_prefixes[fl_ind[0]]:
                            letters_left = self.hand
                            for char in p:
                                if char in letters_left:
                                    ll_ind = letters_left.index(char)
                                else:
                                    ll_ind = letters_left.index(' ')
                                letters_left = letters_left[:ll_ind] + letters_left[ll_ind+1:]
                            words += self.get_words(letters_left, prefix=p, fixed_letter_indices=fl_ind, fixed_letters=fl_let)
                    elif len(fl_ind) > 0 and fl_ind[0] == 0:
                        words += self.get_words(self.hand, fixed_letter_indices=fl_ind, fixed_letters=fl_let)
                    else:
                        words += self.get_words(self.hand)
                    # adding sorting here to have consistent ordering during search
                    words = sorted(words)
                    words = sorted(words, key=len)[::-1]
                    for word in words:
                        if self.game.can_play_word(row, col, word, direction):
                            score, score_word, letters_from_hand = self.game.calculate_turn_score(\
                                row, col, word, self.hand, direction)
                            if score > best_score:
                                best_word = word
                                best_letters_from_hand = letters_from_hand
                                best_score = score
                                best_position = (row, col)
                                best_direction = direction

        return best_word, best_position, best_direction, best_letters_from_hand


    def find_best_play_no_parallel(self):
        """
        Finds the best place to play a word from the given list of words.
        will only find words that intersect at least one already placed
        letter on the board

        Returns:
            tuple: A tuple containing the best word to play, its score,
                starting position (row, col), and direction.
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
                word = list(word)
                row = 7
                for col in range(7 - (len(word)-1), 8):
                    letter_multipliers, word_multipliers = self.game.get_multipliers(row,
                                                                                     col,
                                                                                     word,
                                                                                     'across')
                    score_word, letters_from_hand = self.game.get_score_input(row,
                                                                              col,
                                                                              'across',
                                                                              word,
                                                                              self.hand)
                    score = self.game.calculate_word_score(score_word,
                                                           letter_multipliers,
                                                           word_multipliers,
                                                           len(letters_from_hand))
                    if score > best_score:
                        best_word = word
                        best_letters_from_hand = best_word
                        best_score = score
                        best_position = (row, col)
                        best_direction = 'across'
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

            for i, item in enumerate(self.game.letter_locations):
                row = item[0]
                col = item[1]
                for direction in ['across', 'down']:
                    fl_ind = []
                    fl_let = []
                    minl = 15
                    maxl = -1
                    # using prev_blank sets maxl to be the first letter in of the final string
                    # of connected letters in desired direction
                    prev_blank = -1
                    # check if there are any intersecting letters in the play direction
                    if direction == 'across':
                        if row not in searched_rows:
                            searched_rows.append(row)
                            for j in range(15):
                                if self.game.board[row][j] not in self.game.valid_play_contents:
                                    fl_ind.append(j)
                                    fl_let.append(self.game.board[row][j])
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
                                if self.game.board[j][col] not in self.game.valid_play_contents:
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

                        # TODO: there may be a faster way to form words here where
                        # you also account for the different directions and invalidate
                        # certain letters in certain positions or something
                        # maybe could do something with suffixes
                        # TODO: check that the correct words are gotten

                        # sorted prefix makes it so you don't have to search through all prefixes
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
                                words += self.get_words(letters_left,
                                                        prefix=p,
                                                        fixed_letter_indices=fl_ind,
                                                        fixed_letters=fl_let)
                        elif fl_ind[0] == 0:
                            words += self.get_words(self.hand,
                                                    fixed_letter_indices=fl_ind,
                                                    fixed_letters=fl_let)
                        # adding sorting here to have consistent ordering during search
                        words = sorted(words)
                        words = sorted(words, key=len)[::-1]
                        for word in words:
                            if self.game.can_play_word(row, col, word, direction):
                                score, score_word, letters_from_hand = \
                                    self.game.calculate_turn_score(row,
                                                                   col,
                                                                   word,
                                                                   self.hand,
                                                                   direction)
                                if score > best_score:
                                    best_word = word
                                    best_letters_from_hand = letters_from_hand
                                    best_score = score
                                    best_position = (row, col)
                                    best_direction = direction

        return best_word, best_position, best_direction, best_letters_from_hand

    def find_all_possible_plays(self):
        """
        finds all possible plays

        Returns:
            list[tuple]: A list of tuples containing the word to play, its score,
                starting position (row, col), and direction.
        """
        out_tup = []
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
        searched_rows = set()
        searched_cols = set()
        
        for location in self.game.required_play_locations:
            row = location[0]
            col = location[1]
            for direction in ['across', 'down']:
                fl_ind = []
                fl_let = []
                minl = 15
                maxl = -1
                # using prev_blank sets maxl to be the first letter in of the final string
                # of connected letters in desired direction
                # want to check to see if there are any intersecting letters in the play direction
                
                # TODO: want to add some way to check the cross direction and narrow down the
                # letters that can be played there, this should interface with fl_ind, want to
                # loop through all of the combinations of letters in hand that can be played
                prev_blank = -1
                if direction == 'across':
                    if row not in searched_rows:
                        searched_rows.add(row)
                        for j in range(15):
                            if (row, j) in self.game.required_play_locations:
                                if minl == 15:
                                    minl = j
                                maxl = j
                                prev_blank = j
                            elif self.game.board[row][j] not in self.game.valid_play_contents:
                                fl_ind.append(j)
                                fl_let.append(self.game.board[row][j])
                                if minl == 15:
                                    minl = j
                                if j - prev_blank == 1:
                                    maxl = j
                            else:
                                prev_blank = j
                elif direction == 'down':
                    if col not in searched_cols:
                        searched_cols.add(col)
                        for j in range(15):
                            if (j, col) in self.game.required_play_locations:
                                if minl == 15:
                                    minl = j
                                maxl = j
                                prev_blank = j
                            elif self.game.board[j][col] not in self.game.valid_play_contents:
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
                # if no min is set, then you can't play in this space or
                # the row/col has already been searched
                if minl == 15:
                    continue
                
                if self.game.get_is_first_turn():
                    start = max(minl-6, 0)
                else:
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
                    if len(fl_ind) > 0 and fl_ind[0] in sorted_prefixes:
                        for p in sorted_prefixes[fl_ind[0]]:
                            letters_left = self.hand
                            for char in p:
                                if char in letters_left:
                                    ll_ind = letters_left.index(char)
                                else:
                                    ll_ind = letters_left.index(' ')
                                letters_left = letters_left[:ll_ind] + letters_left[ll_ind+1:]
                            words += self.get_words(letters_left, prefix=p, fixed_letter_indices=fl_ind, fixed_letters=fl_let)
                    elif len(fl_ind) > 0 and fl_ind[0] == 0:
                        words += self.get_words(self.hand, fixed_letter_indices=fl_ind, fixed_letters=fl_let)
                    else:
                        words += self.get_words(self.hand)
                    # adding sorting here to have consistent ordering during search
                    words = sorted(words)
                    words = sorted(words, key=len)[::-1]
                    for word in words:
                        if self.game.can_play_word(row, col, word, direction):
                            score, score_word, letters_from_hand = self.game.calculate_turn_score(\
                                row, col, word, self.hand, direction)
                            if score > 0:
                                out_tup.append((score, word, (row, col), direction, letters_from_hand))

        return out_tup


    def get_play(self, method):
        """turn execution
        """
        if not self.game.is_game_over:
            options = []
            match method:
                case 0:
                    options.append(self.find_best_play_no_parallel())
                case 1:
                    options.append(self.find_best_play())
                case 2:
                    options = self.find_all_possible_plays()
                    options = sorted(options, key=lambda tup: tup[0], reverse=True)
        else:
            return ValueError("GAME IS OVER, YOU CAN'T KEEP PLAYING")

        self.update_state()
        return options

    def do_turn(self, word, position, direction, letters_from_hand):
            if word is not None:
                self.game.place_word(position[0],
                                     position[1],
                                     word,
                                     direction,
                                     self.number,
                                     self.hand)
                if not self.game.is_game_over:
                    # self.game.display_board()
                    for letter in letters_from_hand:
                        if letter not in self.hand:
                            letter = ' '
                        index = self.hand.index(letter)
                        self.hand = self.hand[0:index] + self.hand[index + 1:]
                    self.hand += self.game.draw_letters(len(letters_from_hand))

    def recycle_hand(self):
        self.game.put_letters_back(self.hand)
        self.hand = []
        self.hand += self.game.draw_letters(7)