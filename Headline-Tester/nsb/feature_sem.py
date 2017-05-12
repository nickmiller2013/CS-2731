from collections import Counter
from collections import defaultdict
from nltk.corpus import framenet
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.parse import DependencyGraph
#import malt
from nltk.stem import porter
import csv
import json
import math
import nltk.data # for punkt sentence splitter
import nltk.tag
import operator
import os
import pickle
import re
import socket
import sys
import warnings 

class Headline:
    def __init__(self, headline, bodyid, stance):
        self.text = headline
        self.bodyid = bodyid
        self.stance = stance
        self.features = []

    def __hash__(self):
        return hash(str(self.text) + '\n' + str(self.bodyid) + '\n' + str(stance))

    def __eq__(self, other):
        return str(self.text) == str(other.text) and self.bodyid == other.bodyid and self.stance == other.stance

    def __str__(self):
        return str(self.text) + " => " + str(self.bodyid)

def clean_headlines(headlines):
    for h in headlines:
        # Remove 1-3 word leaders such as "Breaking News:", "Report:", etc.
        h.text = re.sub(r"^\S+?(\s\S+?){0,3}:\s*", r"", h.text)
        # Remove leading quotes such as "'I couldn't believe my eyes': ..."
        h.text = re.sub(r"^['‘].+?':\s*", r"", h.text)
        # Remove twitter hashtags such as "#ISIS"
        h.text = re.sub(r"#(\w+(\W|$))", r"\1", h.text)
        # Remove details in brackets such as "[Updated]", "[AUDIO]", etc.
        h.text = re.sub(r"\[[^\]]+?\]", r"", h.text)
        h.text = re.sub(r"\([^\)]+?\)", r"", h.text)
        # lowercase verbs in infinitive form ('[purports ]to do') and following obvious adjectives ('-ly do')
        h.text = re.sub(r"(\w+s to |to |ly )([A-Z])",
                lambda match: (match.group(1)+match.group(2)).lower(), 
                h.text, flags=re.IGNORECASE)
        # remove adverbs entirely
        h.text = re.sub(r"\w+?ly ", r"", h.text)
        # remove 'No, ' from 'No, ____ didn't happen' clickbait to help Semafor
        h.text = re.sub(r"^[Nn]o, ", r"", h.text)
        # remove appositives such as "filled from lunch" in "Jim, filled from lunch, said ..." to help Semafor
        h.text = re.sub(r",( [^,]+){1,6},", r"", h.text)
        # lowercase verbs ending in -s, -ed, -ing (exclude starting J since... 'James') 
        h.text = re.sub(r"([A-IK-Z]\w+(s|ed|ing))", lambda match: match.group(1).lower(), h.text)
        # get rid of ending explainers such as "president mauled by bear: report"
        h.text = re.sub(r":( \S+){1,4}$", r"", h.text)

    return headlines

def load_headlines(headlines_file):
    '''
    Loads a list of Headline objects from the input file.
    Ignores the stance column of the input file (unrelated to this feature.)
    '''
    headlines = []
    with open(headlines_file, 'r') as hfile:
        reader = csv.DictReader(hfile, delimiter=',', quotechar='"')
        if 'Stance' in reader.fieldnames:
            for line in reader:
                headlines.append(Headline(line['Headline'], line['Body ID'], line['Stance']))
        else:
            for line in reader:
                headlines.append(Headline(line['Headline'], line['Body ID'], None))
    return headlines

def load_bodies(bodies_file):
    '''
    Loads a dictionary of (body id, body text) mappings from the input file.
    '''
    bodies = dict() # body id => body text
    with open(bodies_file, 'r') as bfile:
        reader = csv.DictReader(bfile, delimiter=',', quotechar='"')
        for line in reader:
            bodies[line['Body ID']] = line['articleBody']
    return bodies

def split_sentences(bodies):
    '''
    Assumes bodies is a dict mapping body_id => body_text
    '''
    splitter = nltk.data.load('tokenizers/punkt/english.pickle')
    for body_id in bodies:
        newbody = "\n".join(splitter.tokenize(bodies[body_id])) # one sentence per line
        newbody = re.sub(r"[^A-Za-z]+$", r"", newbody) # remove blankspace/symbol-only lines such as ' * * * '
        newbody = re.sub(r"\n\n", r"\n", newbody, re.MULTILINE) # remove blank lines
        bodies[body_id] = newbody.split('\n')
    return bodies

CACHED_TOK_TAGGED = dict() # sent => list of (token, POS tag) tuples
def tok_and_tag(sents):
    processed = dict()
    for s in sents:
        if s not in CACHED_TOK_TAGGED:
            CACHED_TOK_TAGGED[s] = nltk.pos_tag(nltk.word_tokenize(s))
        processed[s] = CACHED_TOK_TAGGED[s]

    return processed

def dep_parse_sents(sents):
    '''
    Parses sentences using Malt dependency parser, storing the results in a dict
    mapping (headine_text => DependencyGraph)
    '''
    processed = tok_and_tag(sents)
    uniq_sents = sorted([sent for sent in processed])

    parses = maltparser.parse_tagged_sents([processed[sent] for sent in uniq_sents], verbose=True)
    depgraphs = [graph for p in parses for graph in p]
    return dict(zip(uniq_sents, depgraphs))

def semafor_parse(dep_parses):
    '''
    Connects to listening SemaforSocketServer and gets semantic frame labels for input headlines.

    headline_parses: dict mapping sentence_text => DependencyGraph parse
    returns: dict mapping sentence_text => SFO triplet
    '''
    # connect to the SemaforSocketServer and send over the dependency parses
    HOSTNAME = 'localhost'
    PORT = 1234
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOSTNAME, PORT))

    semparses = dict()
    for sent in dep_parses:
        s.sendall((dep_parses[sent].to_conll(10) + "\n").encode('UTF-8')) # newline separates inputs to Semafor
        jsonstr = s.recv(8192).decode('UTF-8') # NOTE: this buffer _could_ be too small...
        semparses[sent] = json.loads(jsonstr)
    s.close()

    return semparses

SFO_KEYS = ['frame_text', 'frame_name', 'subj_text', 'subj_name', 'obj_text', 'obj_name']
def extract_sfo_triples(semparses):
    '''
    Assumes semparses maps sentences => semafor parse output
    '''
    sfo_triples = dict() # sentence => SFO triple dict()
    for s in semparses:
        sfo_triples[s] = defaultdict(str)
        if len(semparses[s]['frames']) > 0:
            sfo_triples[s]['frame_text'] = semparses[s]['frames'][0]['target']['spans'][0]['text']
            sfo_triples[s]['frame_name'] = semparses[s]['frames'][0]['target']['name']
            if len(semparses[s]['frames'][0]['annotationSets']) > 0:
                if len(semparses[s]['frames'][0]['annotationSets'][0]['frameElements']) > 0:
                    sfo_triples[s]['subj_text'] = semparses[s]['frames'][0]['annotationSets'][0]['frameElements'][0]['spans'][0]['text']
                    sfo_triples[s]['subj_name'] = semparses[s]['frames'][0]['annotationSets'][0]['frameElements'][0]['name']
                if len(semparses[s]['frames'][0]['annotationSets'][0]['frameElements']) > 1:
                    sfo_triples[s]['obj_text'] = semparses[s]['frames'][0]['annotationSets'][0]['frameElements'][1]['spans'][0]['text']
                    sfo_triples[s]['obj_name'] = semparses[s]['frames'][0]['annotationSets'][0]['frameElements'][1]['name']
    return sfo_triples

def get_cosine(vec1, vec2):
    '''
    From http://stackoverflow.com/questions/15173225/how-to-calculate-cosine-similarity-given-2-sentence-strings-python#15174569
    To test for now...
    '''
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def pos_tags_to_wordnet_form(tagged_sent):
    '''
    takes a list of (token, tag) tuples and converts the tag to
    a wordnet friendly form

    Verb -> v, noun -> n, adverb -> r, adj -> a
    '''
    newtags = dict()
    for token in tagged_sent:
        tok = token[0]
        tag = token[1]
        if tag.startswith('V'):
            newtags[tok] = 'v'
        elif tag.startswith('N'):
            newtags[tok] = 'n'
        elif tag.startswith('J'):
            newtags[tok] = 'a'
        elif tag.startswith('RB'):
            newtags[tok] = 'r'
    return newtags

def hypernyms_in_sent(sent):
    '''
    returns a list of synset hypernyms of non-stop-words in the sentence
    '''
    tagged = tok_and_tag([sent])[sent] # tok_and_tag expects list, returns dict mapping sent => tagged
    tagged = pos_tags_to_wordnet_form(tagged)
    hypernyms = []
    for tok in tagged:
        synset = wordnet.synsets(tok, pos=tagged[tok])
        if len(synset) > 0 and len(synset[0].hypernyms()) > 0:
            hypernyms.append(synset[0].hypernyms()[0].name())
    return hypernyms

# huge performance boost...
CACHED_HEADLINE_VECS = dict()
CACHED_SENT_VECS = dict()
def most_sim_sents(headline, body_sents, top_n=3):
    '''
    Assumes headline is str, body is list of sentence strings
    returns a list of top_n body sentences most similar to the headline
    in (sent, similarity) tuples

    includes hypernyms, unigram stems, and bigram stems as sentence similarity features
    '''
    stemmer = porter.PorterStemmer()

    # calculate vector of headline
    if headline in CACHED_HEADLINE_VECS:
        headline_vec = CACHED_HEADLINE_VECS[headline]
    else:
        # lowercase, tokenize, remove punctuation, stem
        headline_uni_stems = [stemmer.stem(t) for t in nltk.word_tokenize(headline.lower()) if t not in stopwords.words('english') and re.match(r"\W+", t) is None]
        headline_bi_stems = []
        for i in range(len(headline_uni_stems)-1):
            headline_bi_stems.append((headline_uni_stems[i], headline_uni_stems[i+1]))

        headline_hypernyms = hypernyms_in_sent(headline)

        headline_vec = Counter(headline_uni_stems + headline_bi_stems + headline_hypernyms)
        CACHED_HEADLINE_VECS[headline] = headline_vec

    # calculate vector of each body sentence & compare similarity to the headline
    sent_score = dict()
    for sent in body_sents:
        if sent in CACHED_SENT_VECS:
            body_vec = CACHED_SENT_VECS[sent]
        else:
            body_uni_stems = [stemmer.stem(t) for t in nltk.word_tokenize(sent.lower()) if t not in stopwords.words('english') and re.match(r"\W+", t) is None]
            body_bi_stems = []
            for i in range(len(body_uni_stems)-1):
                body_bi_stems.append((body_uni_stems[i], body_uni_stems[i+1]))

            body_hypernyms = hypernyms_in_sent(sent)

            body_vec = Counter(body_uni_stems + body_bi_stems + body_hypernyms)
            CACHED_SENT_VECS[sent] = body_vec
        sent_score[sent] = get_cosine(headline_vec, body_vec)
    sorted_by_score = sorted(sent_score.items(), reverse=True, key=operator.itemgetter(1))
    if top_n == -1: # return all similar sentences
        return [sent for sent in sorted_by_score if sent[1] > 0.0]
    else:
        return [sent for sent in sorted_by_score[:top_n] if sent[1] > 0.0]

def has_negation(sent):
    return re.match("(no|n't|not)\b", sent, flags=re.IGNORECASE) is not None

def sim_neg_features(headlines_file, bodies_file):
    '''
    Calculates various potentially useful features...
    '''
    # load input data
    headlines = load_headlines(headlines_file)
    bodies = load_bodies(bodies_file)
    bodies_sents = split_sentences(bodies)

    print('processing', len(headlines), 'headlines from', headlines_file, '...')
    count = 0
    for headline in headlines:
        # body sentences linked to this headline
        body_sents = bodies_sents[headline.bodyid]
        # most similar sentences from body for this headline
        top_sents = most_sim_sents(headline.text, body_sents, top_n=-1)

        # feature calculation =========
        # - sentence similarity
        headline.features.append(len(top_sents) / len(body_sents)) # proportion of body related to headline

        if len(top_sents) > 0:
            headline.features.append(top_sents[0][1]) # max similarity of any one sentence
            headline.features.append(sum([s[1] for s in top_sents])/len(body_sents)) # average similarity of all sentences
            # compare negation in headline and most similar sentence
            if has_negation(headline.text) == has_negation(top_sents[0][0]):
                headline.features.append(1)
            else:
                headline.features.append(0)
        else:
            headline.features.append(0) # max similarity = 0
            headline.features.append(0) # avg similarity = 0
            headline.features.append(-1) # no match in negation

        # headline-to-first-sentence similarity metrics
        first_sent = body_sents[0]
        first_sent_sim = get_cosine(CACHED_HEADLINE_VECS[headline.text], CACHED_SENT_VECS[first_sent])
        headline.features.append(first_sent_sim)
        # compare negation in headline and first sentence
        if has_negation(headline.text) == has_negation(first_sent):
            headline.features.append(1)
        else:
            headline.features.append(0)

        count += 1
        if (count % 1000 == 0):
            print(count)

    return headlines

def calc_sfo_sim(h_sfo_triple, b_sfo_triple):
    '''
    Calculates the actual feature list for a headline-body pairing.

    h_sfo_triple: headline SFO triples
    b_sfo_triple: body sentence SFO triples

    The features roughly follow [Hasan and Ng 2013, Sec. 4.1.2] except for sentiment labels.
    We also add a feature corresponding to matching frames with Don't Care (DC) for subj and obj,
    and we extract negation into its own feature: 1 if both negated or both positive, 0 if they disagree
    For all below: 1 if match, 0 if mismatch
    <subj_text:frame_name:obj_text>
    <subj_name:frame_name:obj_text>
    <subj_text:frame_name:obj_name>
    <subj_name:frame_name:obj_name>
    <DC:frame_name:obj_name>
    <subj_name:frame_name:DC>
    <DC:frame_name:DC>
    '''
    if b_sfo_triple is None: # no sentence is similar enough to even bother Semafor parsing
        return [0, 0, 0, 0, 0, 0, 0]

    subj_text_agrees = h_sfo_triple['subj_text'] == b_sfo_triple['subj_text'] != ''
    subj_name_agrees = h_sfo_triple['subj_name'] == b_sfo_triple['subj_name'] != ''
    obj_text_agrees = h_sfo_triple['obj_text'] == b_sfo_triple['obj_text'] != ''
    obj_name_agrees = h_sfo_triple['obj_name'] == b_sfo_triple['obj_name'] != ''
    frame_name_agrees = h_sfo_triple['frame_name'] == b_sfo_triple['frame_name'] != ''

    # <subj_text:frame_name:obj_text>
    features = []
    if subj_text_agrees and frame_name_agrees and obj_text_agrees:
        features.append(1)
    else:
        features.append(0)
    # <subj_name:frame_name:obj_text>
    if subj_name_agrees and frame_name_agrees and obj_text_agrees:
        features.append(1)
    else:
        features.append(0)
    # <subj_text:frame_name:obj_name>
    if subj_text_agrees and frame_name_agrees and obj_name_agrees:
        features.append(1)
    else:
        features.append(0)
    # <subj_name:frame_name:obj_name>
    if subj_name_agrees and frame_name_agrees and obj_name_agrees:
        features.append(1)
    else:
        features.append(0)
    # <DC:frame_name:obj_name>
    if subj_name_agrees and frame_name_agrees:
        features.append(1)
    else:
        features.append(0)
    # <subj_name:frame_name:DC>
    if subj_name_agrees and obj_name_agrees:
        features.append(1)
    else:
        features.append(0)
    # <DC:frame_name:DC>
    if frame_name_agrees and obj_name_agrees:
        features.append(1)
    else:
        features.append(0)

    return features

def sfo_feature(headlines_file, bodies_file):
    '''
    Requires Semafor to be running as a socket server. Use following command:
    java -Xms4g -Xmx4g -cp target/Semafor-3.0-alpha-04.jar edu.cmu.cs.lti.ark.fn.SemaforSocketServer model-dir:models/semafor_malt_model_20121129 port:1234
    '''
    # load input data
    raw_headlines = load_headlines(headlines_file)
    cleaned_headlines = clean_headlines(raw_headlines)
    raw_to_clean = dict(zip(raw_headlines, cleaned_headlines))
    bodies = load_bodies(bodies_file)
    bodies_sents = split_sentences(bodies)

    # work with headlines
    depparses = dep_parse_sents([h.text for h in cleaned_headlines])
    semparses = semafor_parse(depparses)
    h_sfo_trips = extract_sfo_triples(semparses)

    # find most relevant sentences in bodies for every headline
    print("calculating most related sentence(s) for each headline...")
    top_sents = dict() # maps headline => list of top sentences
    to_be_parsed = set()
    for headline in raw_headlines:
        top_sents[headline] = most_sim_sents(headline.text, bodies_sents[headline.bodyid], top_n=1)
        to_be_parsed |= set(top_sents[headline])

    # parse related body sentences and extract their SFO triples to compare with those of headlines
    print("calculating dependency parses for sentences...")
    b_dep_parses = dep_parse_sents(to_be_parsed) # maps sentence => dep parse
    print("calculating semafor parses for sentences...")
    b_sem_parses = semafor_parse(b_dep_parses) # maps sentence => sem parse
    print("calculating SFO triples for sentences...")
    b_sfo_trips = extract_sfo_triples(b_sem_parses) # maps sentence => top-confidence SFO triple

    # calculate the actual features
    features = dict()
    for headline in raw_headlines:
        cleaned = raw_to_clean[headline]
        # get headline sfo
        h_sfo_triple = h_sfo_trips[cleaned.text]
        # get body sfo
        if len(top_sents[headline]) > 0: # get the top sentence's SFO triple
            b_sfo_triple = b_sfo_trips[top_sents[headline][0]]
        else:
            b_sfo_triple = None
        features[headline] = calc_sfo_sim(h_sfo_triple, b_sfo_triple)

    return features

if __name__ == "__main__":
    MALT_PATH = os.path.abspath("./maltparser-1.9.0/")
    MALT_MODEL = os.path.abspath("./maltparser-1.9.0/engmalt.linear-1.7.mco")
    maltparser = malt.MaltParser(MALT_PATH, MALT_MODEL)

    SAVED_DEP_PARSES='headlines.conll'

    raw_headlines = load_headlines(sys.argv[1])
    cleaned_headlines = clean_headlines(raw_headlines)
    raw_to_clean = dict(zip(raw_headlines, cleaned_headlines))
    bodies = load_bodies(sys.argv[2])
    bodies_sents = split_sentences(bodies)

    # load saved dep parses if available to save runtime/repeated work
    if os.path.isfile(SAVED_DEP_PARSES):
        depgraphs = DependencyGraph.load(SAVED_DEP_PARSES, top_relation_label='null')
        depparses = dict(zip(uniq_headlines, depgraphs))
        print("loaded cached headline dep parses")
    else:
        depparses = dep_parse_sents([h.text for h in cleaned_headlines])
        with open(SAVED_DEP_PARSES, 'w') as p_out:
            for headline in depparses:
                p_out.write(depparses[headline].to_conll(10) + '\n')

    # find most relevant sentences in bodies for every headline
    print("calculating most related sentence(s) for each headline...")
    top_sents = dict() # maps headline => list of top sentences
    to_be_parsed = set()
    for headline in raw_headlines:
        top_sents[headline] = most_sim_sents(headline.text, bodies_sents[headline.bodyid], top_n=10)
        to_be_parsed |= set(top_sents[headline])

    # parse related body sentences and extract their SFO triples to compare with those of headlines
    print("calculating dependency parses for sentences...")
    b_dep_parses = dep_parse_sents(to_be_parsed) # maps sentence => dep parse
