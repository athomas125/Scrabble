from  Trie import Trie
import pickle
import time

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

# load the words from the dictionary file into trie
start = time.time()
loaded_trie = load_words_into_trie('Collins Scrabble Words (2019).txt')

# Save trie_instance to a file
with open('trie.pkl', 'wb') as file:
    pickle.dump(loaded_trie, file)

end = time.time()
print("time to load trie: " + str(end-start))