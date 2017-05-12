#!/usr/bin/env python3
# Matthew O'Brien, Nathaniel Blake, Nick Miller
# Tuesday, March 28 2017

#Gets the similarity using the swoogle tool. The swoogle tool seems to be temporarily down but temp_accuracy (which isn't good)
#just checks the synonyms between the words.
import csv
import string
import sys
import re
from difflib import SequenceMatcher as SM
from collections import OrderedDict
import re, math
from collections import Counter
from nltk.corpus import wordnet
import nltk.data
from difflib import SequenceMatcher as SM
from nltk import word_tokenize
from nltk.corpus import stopwords


import math
import nltk
from requests import get



WORD = re.compile(r'\w+')
stop = stopwords.words('english') + list(string.punctuation)


def get_cosine(vec1, vec2):
     intersection = set(vec1.keys()) & set(vec2.keys())
     numerator = sum([vec1[x] * vec2[x] for x in intersection])

     sum1 = sum([vec1[x]**2 for x in vec1.keys()])
     sum2 = sum([vec2[x]**2 for x in vec2.keys()])
     denominator = math.sqrt(sum1) * math.sqrt(sum2)

     if not denominator:
        return 0.0
     else:
        return float(numerator) / denominator

def text_to_vector(text):
     words = WORD.findall(text)
     return Counter(words)

def tempAccuracy(s1, s2):
    vector1 = text_to_vector(s1)
    vector2 = text_to_vector(s2)

    return get_cosine(vector1, vector2)

def stripSentence(s1):

    return (" ").join([i for i in word_tokenize(s1.lower()) if i not in stop])


def average_svo(headline, body):

    avg = 0.0
    count = 0.0
    max = 0.0
    max2 = 0.0
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    headline = stripSentence(headline)

    for d in sent_detector.tokenize(body.strip()):
        ##print d
        ##print "The similarity measurement is below: "

        d = stripSentence(d)


        #similarity_measurement = sss(headline, body_sentence, 'Relation Similarity', 'Refined Stanford WebBase corpus')

        similarity_measurement = tempAccuracy(headline,d)

        if similarity_measurement > max:
            max = similarity_measurement

        sm_accr = SM(None, headline, d).ratio()

        if sm_accr > max2:
            max2 = sm_accr
        avg = avg + similarity_measurement
        count = count + 1

    return (avg/count, max, max2)




            #text_file.write("The similarity for headline %s, with body id %s and a stance of %s, is: %.8f\n" % (train_data[k]['Headline'],k,train_data[k]['Stance'],(avg/count)))

#for k in body_data:
#    #print k
#    for d in body_data[k]['articleBody'].split ("\n"):
#        #print "Beep"
#        #print d

