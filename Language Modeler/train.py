# Author: Nick Miller
# Version: 1.0
# Language: Python 2

import argparse
import os
from decimal import *


getcontext().prec = 28
# The following lines parse the command line arguments for you. You may ignore this part.
argument_parser = argparse.ArgumentParser("Language model trainer. ")
argument_parser.add_argument('-t', '--type', help='The type of the model. Possible values: 1, 3, 3s, dummy', required=True)
argument_parser.add_argument('-i', '--input', help='The path to the input file containing the training sentences. ', required=True)
argument_parser.add_argument('-m', '--model', help='The path to the directory of the model files.', required=True)
args = argument_parser.parse_args()

# The following variables are created for your convenience.
# They are the values from the command line input.
model_type = args.type
training_data_path = args.input
model_dir = args.model

# Doing some sanity check for you
if model_type not in ['1', '3', '3s', 'dummy']:
    print("The model type " + model_type + " is not supported.")
    exit(1)

# Prints out what this script does
print("Training a " + model_type + " model")
print("    using training data found at " + training_data_path)
print("After training, the model files will be stored at this directory: " + model_dir)
print("")


# START OF YOUR IMPLEMENTATION

#The oovHandler handles the out of class words to create a list of words to compare frequencies against when they occur
def oovHandler(myList, case):
    words = [w for snt in myList for w in snt]
    tempCount = {}
    wc = {}
    for w in words:
        if w not in wc:
            wc[w] = 1
            tempCount[w] = 1
        else:
            if(w in tempCount):
                tempCount.pop(w, None)
            wc[w] += 1
    if case == 1:
        with open(model_dir + "/oov_handler.txt", "w") as f:
            for k, v in tempCount.items():
                f.writelines("%s\n" % (k))
        return tempCount
    else:
        return wc

# Create the folder that holds the necessary files for fast re-building this LM later (i.e., a dump of the trained LM)
# Notice: this will create whatever user specifies as model_dir.
#         Always use the variable model_dir, and never hard code any absolute paths.
if not os.path.exists(model_dir):
    os.makedirs(model_dir)
else:
    exit(1)

# This variable holds the training sentences. Example content::
#
# train_snts = [
#     ["john", "has", "a",  "cat", "."],
#     ["mary", "has", "a",  "dog", "."],
#     ["john", "'s", "cat",  "is", "not", "a", "dog" "."],
#     ["mary", "'s", "dog",  "is", "not", "a", "cat" "."]"
# ]
#
training_sentences = [line.rstrip('\n').split(' ') for line in open(training_data_path)]

if os.path.isfile(model_dir + "/oov_handler.txt"):
    print("Found the path")
    toRemove = [line.rstrip('\n') for line in open(model_dir + "/oov_handler.txt")]
else:
    toRemove = oovHandler(training_sentences,1)

if model_type == "dummy":
    # The dummy model is a very naive unigram model.
    # It assigns 1/V as the probability for every unigram.
    #   where V is the vocabulary size

    words = [w for snt in training_sentences for w in snt]
    vocab = set()
    for w in words:
        #print(w)
        vocab.add(w)

    vocab_size = len(vocab)

    # When we re-create the LM later, we will need the model type and the vocabulary size.
    # We don't save the probabilities here, because we will be computing the probabilities only the fly later in other scripts.
    with open(model_dir + "/model_type.txt", "w") as f:
        f.writelines([model_type])

    with open(model_dir + "/vocab_size.txt", "w") as f:
        f.writelines([str(vocab_size)])
elif model_type == "1":
    # The dummy model is a very naive unigram model.
    # It assigns 1/V as the probability for every unigram.
    #   where V is the vocabulary size

    print("In the unigram.")

    wordcount = {}
    #A loop to go through and check whether the word is in the words that have freq of 1. If so change it to 1.
    #then add it to the wordcount list appropriately
    words = [w for snt in training_sentences for w in snt]
    totalCount = 0
    for w in words:
        if w in toRemove:
            w = "<unk>"
        totalCount += 1
        if w not in wordcount:
            wordcount[w] = 1
        else:
            wordcount[w] += 1

    #Output files, the conversion to assign probability is done in the actual file output.
    with open(model_dir + "/model_type.txt", "w") as f:
        f.writelines([model_type])
    with open(model_dir + "/vocab_prob.txt", "w") as f:
        for k, v in wordcount.items():
            f.writelines("%s %.20f\n" % (k, Decimal(Decimal(v)/Decimal(totalCount))))
    with open(model_dir + "/vocab_size.txt", "w") as f:
        f.writelines([str(len(wordcount))])
        f.writelines("\n%s" % str(totalCount))
    with open(model_dir + "/model_properties.txt", "w") as f:
        f.writelines("unsmoothed unigram")
    print("Looking for a unigram model type")
elif model_type == "3":
    print("In the trigram.")

    words = [w for snt in training_sentences for w in snt]
    wordcount = {}
    wordcount2 = {}

    totalCount = 0

    #Removes the words with frequency of 1 by changing them and creating a toInsert string, does this for both a
    #count of 2 and count of 3 word groups. Then d
    for snt in training_sentences:
        snt.insert(0, "[s]")
        snt.insert(0, "[s]")
        snt.insert(len(snt), "[s/]")

        for w in range(0, len(snt), 1):

            #Gets the (Wn-2, Wn-1, Wn)

            if w < len(snt) - 2:
                if snt[w] in toRemove:
                    #print(snt[w])
                    snt[w] = "<unk>"
                if snt[w + 1] in toRemove:
                    #print(snt[w])
                    snt[w+1] = "<unk>"
                if snt[w + 2] in toRemove:
                    #print(snt[w])
                    snt[w+2] = "<unk>"
                toInsert = (snt[w] + " " + snt[w+1] + " " + snt[w+2])

                totalCount += 1
                if toInsert not in wordcount:
                    wordcount[toInsert] = 1
                else:
                    wordcount[toInsert] += 1
            #Gets the (Wn-2, Wn-1)
            if w < len(snt) - 1:
                if snt[w] in toRemove:
                    #print(snt[w])
                    snt[w] = "<unk>"
                if snt[w + 1] in toRemove:
                    #print(snt[w])
                    snt[w+1] = "<unk>"

                toInsert = (snt[w] + " " + snt[w+1])

                totalCount += 1
                if toInsert not in wordcount2:
                    wordcount2[toInsert] = 1
                else:
                    wordcount2[toInsert] += 1

    i = 0

    trigram_calc = {}
    for key in wordcount:
        new_key = key.split(" ")
        trigram_calc[key] = float(wordcount[key])/wordcount2[new_key[0] + " " + new_key[1]]

    with open(model_dir + "/model_type.txt", "w") as f:
        f.writelines([model_type])

    with open(model_dir + "/vocab_prob.txt", "w") as f:
        for k, v in trigram_calc.items():
            f.writelines("%s %.20f\n" % (k, Decimal(v)))

    with open(model_dir + "/tri_count.txt", "w") as f:
        for k, v in wordcount.items():
            f.writelines("%s %f\n" % (k, float(v)))
    with open(model_dir + "/di_count.txt", "w") as f:
        for k, v in wordcount2.items():
            f.writelines("%s %f\n" % (k, float(v)))
    with open(model_dir + "/vocab_size.txt", "w") as f:
        f.writelines([str(len(trigram_calc))])


    print("Looking for a unsmoothed trigram model type")
elif model_type == "3s":

    print("In the trigram.")

    #Difference here is in the division
    words = [w for snt in training_sentences for w in snt]
    wordcount = {}
    wordcount2 = {}

    totalCount = 0

    for snt in training_sentences:
        snt.insert(0,"[s]")
        snt.insert(0,"[s]")
        snt.insert(len(snt),"[/s]")
        for w in range(0, len(snt), 1):

            if w < len(snt) - 2:
                if snt[w] in toRemove:
                    #print(snt[w])
                    snt[w] = "<unk>"
                if snt[w + 1] in toRemove:
                    #print(snt[w])
                    snt[w+1] = "<unk>"
                if snt[w + 2] in toRemove:
                    #print(snt[w])
                    snt[w+2] = "<unk>"
                toInsert = (snt[w] + " " + snt[w+1] + " " + snt[w+2])

                totalCount += 1
                if toInsert not in wordcount:
                    wordcount[toInsert] = 1
                else:
                    wordcount[toInsert] += 1
            if w < len(snt) - 1:
                if snt[w] in toRemove:
                    #print(snt[w])
                    snt[w] = "<unk>"
                if snt[w + 1] in toRemove:
                    #print(snt[w])
                    snt[w+1] = "<unk>"

                toInsert = (snt[w] + " " + snt[w+1])

                totalCount += 1
                if toInsert not in wordcount2:
                    wordcount2[toInsert] = 1
                else:
                    wordcount2[toInsert] += 1

    i = 0

    trigram_calc = {}
    #Calculates with the appropriate additions to smooth it.
    for key in wordcount:
        new_key = key.split(" ")
        trigram_calc[key] = (float(wordcount[key]) + 1)/((wordcount2[new_key[0] + " " + new_key[1]]) + len(wordcount2))

    with open(model_dir + "/model_type.txt", "w") as f:
        f.writelines([model_type])

    with open(model_dir + "/vocab_prob.txt", "w") as f:
        for k, v in trigram_calc.items():
            f.writelines("%s %.20f\n" % (k, Decimal(v)))

    with open(model_dir + "/tri_count.txt", "w") as f:
        for k, v in wordcount.items():
            f.writelines("%s %f\n" % (k, float(v)))
    with open(model_dir + "/di_count.txt", "w") as f:
        for k, v in wordcount2.items():
            f.writelines("%s %f\n" % (k, float(v)))
    with open(model_dir + "/vocab_size.txt", "w") as f:
        f.writelines([str(len(trigram_calc))])

    print("Looking for a smoothed trigram model type")
else:
    print("Not implemented yet.")

