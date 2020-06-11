from typing import List


class InvertedIndex:
    """
    This class represents an inverted index object.
    """

    def __init__(self) -> None:
        self.posting_lists = {}

    def __len__(self) -> int:
        return len(self.posting_lists)

    def has_term(self, term: str) -> bool:
        """
        Tells if a word is present in the entire indexing list or not.
        """

        return term in list(self.posting_lists.keys())

    def add(self, term: str, doc_id: int, position: int) -> None:
        """
        Adds a term to indexing list. It also saves the positions, so we can have a positional index.
        """

        self.posting_lists.setdefault(term, {}).setdefault(
            doc_id, []).append(position)

    def get_docs(self, term: str) -> List[int]:
        """
        Returns a list consisting of ids of document that contain a particular word.
        """

        return list(self.posting_lists[term].keys())

    def doc_frequency(self, term: str) -> int:
        """
        Returns the number of documents that contain a particular word.
        """

        return len(self.posting_lists[term])

    def term_frequency(self, term: str, doc_id: int) -> int:
        """
        Returns the number of a word occurrences in a document.
        """

        return len(self.posting_lists[term][doc_id])
