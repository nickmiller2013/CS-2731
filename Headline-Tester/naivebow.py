#!/usr/bin/env python3
# Matthew O'Brien, Nathaniel Blake, Nick Miller
# Tuesday, March 28 2017
import csv
import sys
import nltk
import random
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize, word_tokenize
import nltk.data

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
	
    #Get body data.
    with open(bodies_file, 'r') as body_csv:
        bodies_data_csv = csv.DictReader(body_csv, delimiter=',', quotechar='"')
        body_dict = {}
        for row in bodies_data_csv:
            body_dict[int(row['Body ID'])] = row['articleBody']
    
    #Get training data.
    with open(train_file, 'r') as train_csv:
        train_data_csv = csv.DictReader(train_csv, delimiter=',', quotechar='"')
        train_data = []
        for row in train_data_csv:
            train_data.append(row)
    
    
    #traing the classifier
    rel_av = 0
    unrel_av = 0
    rel_count = 0
    unrel_count = 0
    for train_ex in train_data:
        headline = train_ex['Headline']
        headline = headline.decode("utf-8")
        body = body_dict[int(train_ex['Body ID'])]
        body = body.decode("utf-8")
        bow1 = set()
        bow2 = set()
        for word in word_tokenize(headline):
            bow1.add(word)
        for word in word_tokenize(body):
            bow2.add(word)
        intersect = set(bow1).intersection(bow2)
        if train_ex['Stance'] == 'unrelated':
            unrel_av = unrel_av + len(intersect)
            unrel_count = unrel_count + 1
        else:
            rel_av = rel_av + len(intersect)
            rel_count = rel_count + 1
            
    rel_av = rel_av/rel_count
    unrel_av = unrel_av/unrel_count
        
    print rel_av
    print unrel_av
    
    with open(test_file, 'r') as test_csv, open(outfile, 'w') as out_csv:
        test_data = csv.DictReader(test_csv, delimiter=',', quotechar='"')
        out = csv.DictWriter(out_csv, delimiter=',', quotechar='"', fieldnames=FIELDNAMES)
        out.writeheader()
        for row in test_data:
            headline = row['Headline'].decode("utf-8")
            body = body_dict[int(row['Body ID'])].decode("utf-8")
            bow1 = set()
            bow2 = set()
            for word in word_tokenize(headline):
                bow1.add(word)
            for word in word_tokenize(body):
                bow2.add(word)
            intersect = set(bow1).intersection(bow2)
            count = len(intersect)
            if(abs(count-rel_av) > abs(count-unrel_av)):
                out.writerow({
                    FIELDNAMES[0]: row[FIELDNAMES[0]],
                    FIELDNAMES[1]: row[FIELDNAMES[1]],
                    FIELDNAMES[2]: LABELS[3]})
            else:
                out.writerow({
                    FIELDNAMES[0]: row[FIELDNAMES[0]],
                    FIELDNAMES[1]: row[FIELDNAMES[1]],
                    FIELDNAMES[2]: LABELS[random.randint(0,2)]})


