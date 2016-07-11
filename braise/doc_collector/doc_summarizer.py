import nltk
import utils
import numpy as np

# Noun Part of Speech Tags used by NLTK
# More can be found here
# http://www.winwaed.com/blog/2011/11/08/part-of-speech-tags/
NOUNS = ['NN', 'NNS', 'NNP', 'NNPS']

def summarize(title, doc, cleaned_document, doc_vector, feature_names):
    top_sents = rank_sentences(title, doc, doc_vector, feature_names)
    summary = '.'.join([cleaned_document.split('.')[i]
                        for i in [pair[0] for pair in top_sents]])
    summary = ' '.join(summary.split())
    return summary

def similarity_score(t, s):
    """Returns a similarity score for a given sentence.

    similarity score = the total number of tokens in a sentence that exits
                        within the title / total words in title

    """
    t = utils.remove_stop_words(t.lower())
    s = utils.remove_stop_words(s.lower())
    t_tokens, s_tokens = t.split(), s.split()
    similar = [w for w in s_tokens if w in t_tokens]
    if len(t_tokens) == 0:
        return 0
    score = (len(similar) * 0.1 ) / float(len(t_tokens))
    return score

def rank_sentences(title, doc, doc_vector, feature_names, top_n=3):
    """Returns top_n sentences. Theses sentences are then used as summary
    of document.

    input
    ------------
    doc : a document as type str
    doc_vector : a dense tf-idf vector calculated with Scikits TfidfTransformer
    feature_names : a list of all features, the index is used to look up
                    tf-idf scores in the doc_vector
    top_n : number of sentences to return

    """
    sents = nltk.sent_tokenize(doc)
    sentences = [nltk.word_tokenize(sent) for sent in sents]
    sentences = [[w for w in sent if nltk.pos_tag([w])[0][1] in NOUNS]
                  for sent in sentences]
    tfidf_sent = [[doc_vector[feature_names.index(w.lower())]
                   for w in sent if w.lower() in feature_names]
                   for sent in sentences]

    # Calculate Sentence Values
    doc_val = sum(doc_vector)
    sent_values = [sum(sent) / doc_val for sent in tfidf_sent]

    # Apply Similariy Score Weightings
    similarity_scores = [similarity_score(title, sent) for sent in sents]
    scored_sents = np.array(sent_values) + np.array(similarity_scores)

    # Apply Position Weights
    ranked_sents = [sent*(i/len(sent_values))
                    for i, sent in enumerate(sent_values)]

    ranked_sents = [pair for pair in zip(range(len(sent_values)), sent_values)]
    ranked_sents = sorted(ranked_sents, key=lambda x: x[1] *-1)

    return ranked_sents[:top_n]
