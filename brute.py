import re
from itertools import combinations
from Trie import Trie
from ScrabbleBoard import ScrabbleBoard
import time
import numpy as np
import string


def load_words_into_trie(file_name):
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


def get_words(trie, letters, prefix='', words=None):
    if words is None:
        words = set()
    if prefix:
        valid_word, valid_prefix = trie.search(prefix)
        if valid_word:
            words.add(prefix)
        if not valid_prefix:
            return words
    for i, letter in enumerate(letters):
        new_letters = list(letters)
        new_letters.pop(i)
        if letter == ' ':
            for wildcard in string.ascii_uppercase:
                get_words(trie, new_letters, prefix + wildcard, words)
        else:
            get_words(trie, new_letters, prefix + letter, words)
    return words


# Load the words from the dictionary file into the Trie
trie = load_words_into_trie('Collins Scrabble Words (2019).txt')

# initialize the board
board = ScrabbleBoard(1)

hand = board.draw_letters(7)
for _ in range(1):
    drawn_letters = board.draw_letters(7 -len(hand))
    
    # hand = ['U', 'Q', 'E', 'A', 'I', 'A', 'K']
    # hand = input('enter your letters: ').upper()
    print(hand)
    valid_words = get_words(trie, hand)
    print(valid_words)

valid_words = sorted(valid_words, key=len)[::-1]


# # need to update this
# board.display_board()

print(valid_words)

# # saving words to ouput file
# with open(letters + '.txt', 'w') as handle:
#     valid_words = "\n".join(valid_words)
#     handle.write(valid_words)