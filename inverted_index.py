class InvertedIndex:
    def __init__(self):
        self.posting_lists = {}
        
    def __len__(self):
        return len(self.posting_lists)
    
    def has_term(self, term):
        return term in list(self.posting_lists.keys())

    def add(self, term, doc_id, position):
        self.posting_lists.setdefault(term, {}).setdefault(
            doc_id, []).append(position)

    def get_docs(self, term):
        return list(self.posting_lists[term].keys())

    def doc_frequency(self, term):
        return len(self.postings_lists[term])

    def term_frequency(self, term, doc_id):
        return len(self.postings_lists[term][doc_id])
