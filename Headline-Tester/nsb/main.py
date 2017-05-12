#!/usr/bin/env python3
# Matthew O'Brien, Nathaniel Blake, Nick Miller
import csv
import sys
from sklearn import svm
import numpy as np
import nltk
import random
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize, word_tokenize
import nltk.data
from nltk.corpus import stopwords
import feature_sem as nsb

USAGE = 'Usage: python3 main.py bodies.csv train.csv test.csv answers.csv'
FIELDNAMES = ['Headline', 'Body ID', 'Stance']
LABELS = ['agree', 'disagree', 'discuss', 'unrelated']
RELATED = LABELS[0:3]

if __name__ == '__main__':
    args = sys.argv
    if len(args) < 5:
        print(USAGE)
        sys.exit(0);

    bodies_file = args[1]; # bodies for both train & test data
    train_file = args[2]; # training data = list of (title, ID, stance) triplets
    test_file = args[3]; # test file = list of (title, ID) pairs
    outfile = args[4]; # output is in (title, ID, stance) format of train data

    processed_headlines = nsb.sim_neg_features(train_file, bodies_file)

    print('fitting SVM...')
    clf = svm.SVC(decision_function_shape='ovo')
    clf.fit([h.features for h in processed_headlines], [h.stance for h in processed_headlines]) 

    processed_headlines = nsb.sim_neg_features(test_file, bodies_file)
    print('making predictions of SVM...')
    predictions = clf.predict(np.array([h.features for h in processed_headlines]))
    with open(outfile, 'w', encoding='utf-8') as out_csv:
        out = csv.DictWriter(out_csv, delimiter=',', quotechar='"', fieldnames=FIELDNAMES)
        out.writeheader()

        for i in range(len(processed_headlines)):
            out.writerow({
                FIELDNAMES[0]: processed_headlines[i].text,
                FIELDNAMES[1]: processed_headlines[i].bodyid,
                FIELDNAMES[2]: predictions[i]})
                
                
                
                
