# core/Trie.py
from dataclasses import dataclass, field


@dataclass
class TrieNode:
    children: dict[str, 'TrieNode'] = field(default_factory=dict)  # New dictionary instance for each node
    is_end_of_word: bool = False


class Trie:
    """Interative implementation of a Trie.
    """
    def __init__(self):
        self._root = TrieNode()

    def insert(self, word: str) -> None:
        """Inserts the given word into the Trie, starting at the root node.

        Args:
            word (str): The word to insert.
        """
        node: TrieNode = self._root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
        node.is_end_of_word = True

    def _get_words_from_node(self, node: TrieNode, prefix: str, words: list[str]) -> None:
        if node.is_end_of_word:
            words.append(prefix)
        for char, child in node.children.items():
            self._get_words_from_node(child, prefix + char, words)

    def get_words_from_prefix(self, prefix: str) -> list[str]:
        """returns all words that start with the given prefix.

        Args:
            prefix (str): The prefix for every word returned.

        Returns:
            list[str]: A list of words that start with the given prefix.
        """
        node: TrieNode = self._root
        words = []
        for char in prefix:
            node = node.children.get(char, None)
            if node is None:
                return words
        self._get_words_from_node(node, prefix, words)
        return words
