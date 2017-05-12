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
import swoogle_similarity as ss
import nsb.feature_sem as nsb

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
    with open(bodies_file, 'r', encoding='utf-8') as body_csv:
        bodies_data_csv = csv.DictReader(body_csv, delimiter=',', quotechar='"')
        body_dict = {}
        for row in bodies_data_csv:
            body_dict[int(row['Body ID'])] = row['articleBody']
    
    #Get training data.
    with open(train_file, 'r', encoding='utf-8') as train_csv:
        train_data_csv = csv.DictReader(train_csv, delimiter=',', quotechar='"')
        train_data = []
        for row in train_data_csv:
            train_data.append(row)

    # calc nathaniel's features...
    nsbfeatures = nsb.sim_neg_features(train_file, bodies_file)
            
    stances = [] #add the stance of the training example in order
    featureVectors = [] #add the completed feature lists to this after all training
    count = 0 #literally just for keeping track of how fast the training goes
    for train_ex in train_data:
        headline = train_ex['Headline']
        body = body_dict[int(train_ex['Body ID'])]

        
        #potentially or definately reused bits
        featureVector = []
        head_tokens = word_tokenize(headline) #tokenized headline
        head_set = set(head_tokens) #set of words in headline
        bow = head_set - set(nltk.corpus.stopwords.words('english')) #bog of words = head_set - stop_words
        body_tokens = word_tokenize(body)
        (swoogle_average, swoogle_max, sm_accr) = ss.average_svo(headline, body)

        #bow specific declarations
        bow_seen = set()
        
        bowFeatEx = 0
        for word in word_tokenize(body):
            if word in bow:
                if word not in bow_seen:
                    bowFeatEx =  bowFeatEx + 1
                    bow_seen.add(word)
                
        #handle features and stance lists        
        stances.append(train_ex['Stance'])
        featureVector.append(bowFeatEx)
        featureVector.append(len(head_tokens))
        featureVector.append(swoogle_average)
        featureVector.append(swoogle_max)
        featureVector.append(sm_accr)
        featureVector += nsbfeatures[count].features

        count = count+1
        if count%1000 is 0:
            print(count)
        featureVectors.append(featureVector)
        
    #now define and fit the svm classifier
    clf = svm.SVC(decision_function_shape='ovo')
    clf.fit(featureVectors, stances) 
    
    # calc nathaniel's features...
    nsbfeatures = nsb.sim_neg_features(test_file, bodies_file)

    with open(test_file, 'r', encoding='utf-8') as test_csv, open(outfile, 'w', encoding='utf-8') as out_csv:
        test_data = csv.DictReader(test_csv, delimiter=',', quotechar='"')
        out = csv.DictWriter(out_csv, delimiter=',', quotechar='"', fieldnames=FIELDNAMES)
        out.writeheader()
        row_num = 0
        for row in test_data:
            #get decoded headline and body
            headline = row['Headline']
            body = body_dict[int(row['Body ID'])]
            
            #features list
            features = []
            
            #potentially reused things go here
            head_tokens = word_tokenize(headline) #tokenized headline
            head_set = set(head_tokens) #set of words in headline
            bow = head_set - set(nltk.corpus.stopwords.words('english')) #bog of words = head_set - stop_words
            body_tokens = word_tokenize(body) #tokenized body
            (swoogle_average, swoogle_max, sm_accr) = ss.average_svo(headline, body)

            #sepecific to bow things here
            bow_seen = set()
            
            bowFeatEx = 0
            for word in body_tokens:
                if word in bow:
                    if word not in bow_seen:
                        bowFeatEx =  bowFeatEx + 1
                        bow_seen.add(word)
            
            #add up all features to list in same order as in training
            features.append(bowFeatEx)
            features.append(len(head_tokens))
            features.append(swoogle_average)
            features.append(swoogle_max)
            features.append(sm_accr)
            features += nsbfeatures[row_num].features
            result = clf.predict(np.array(features).reshape(1, -1)) # reshape since it's a single sample
            
            out.writerow({
                FIELDNAMES[0]: row[FIELDNAMES[0]],
                FIELDNAMES[1]: row[FIELDNAMES[1]],
                FIELDNAMES[2]: result[0]}) # assume unrelated for every entry

            row_num += 1
