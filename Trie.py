class TrieNode:
    """
    Represents a single node in the Trie.
    """
    def __init__(self):
        """
        Initializes the TrieNode with an empty dictionary for the children nodes and 
        a boolean indicating whether this node is the end of a word.
        """
        self.children = {}
        self.is_end_of_word = False

class Trie:
    """
    Represents a Trie (or Prefix Tree) data structure.
    """
    def __init__(self):
        """
        Initializes the Trie with a root TrieNode.
        """
        self.root = TrieNode()

    def insert(self, word):
        """
        Inserts a word into the Trie.

        Args:
            word (str): The word to be inserted.
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        """
        Searches for a word in the Trie.

        Args:
            word (str): The word to be searched for.

        Returns:
            bool: True if the word is found, False otherwise.
            bool: True if word is valid prefix, False otherwise.
        """
        node = self.root
        for char in word:
            if char not in node.children:
                return False, False
            node = node.children[char]
        return node.is_end_of_word, True

