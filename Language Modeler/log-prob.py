# Author: Yuhuan Jiang
# Version: 1.0
# Language: Python 2

import argparse
import math

# The following lines parse the command line arguments for you. You may ignore this part.
argument_parser = argparse.ArgumentParser("Log probability script. ")
argument_parser.add_argument('-m', '--model', help='The path to the directory containing the necessary files to recreate the language model.', required=True)
argument_parser.add_argument('-i', '--input', help='The path to the input file containing the n-grams to query. ', required=True)
argument_parser.add_argument('-o', '--output', help='The path to the output file containing the log probabilities for the input n-grams. ', required=True)
args = argument_parser.parse_args()

# The following variables are created for your convenience.
# They are the values from the command line input.
model_dir = args.model
ngram_input_path = args.input
log_prob_output_path = args.output

# Prints out what this script does
print("Computing the log-probabilities of the input n-grams in file: " + ngram_input_path)
print("    using the language model recreated from the directory: " + model_dir)
print("Result will be stored in the file: " + log_prob_output_path)
print("")



# START OF YOUR IMPLEMENTATION

# Recreate the LM
with open(model_dir + "/model_type.txt") as f:
    model_type = f.readline()

with open(model_dir + "/vocab_size.txt") as f:
    vocab_size = float(f.readline())

queried_ngrams = [tuple(line.rstrip('\n').split(' ')) for line in open(ngram_input_path)]
language_model = {}
from decimal import *
with open(model_dir + "/vocab_prob.txt") as f:
    for line in f:
        #print line
        toSplit = line.split(" ")
        #print len(toSplit)
        if len(toSplit) == 4:
            #print Decimal(toSplit[3])
            language_model[toSplit[0] + " " + toSplit[1] + " " + toSplit[2]] = float(Decimal(toSplit[3]))
        else:
            language_model[toSplit[0]] = float(Decimal(toSplit[1]))

if model_type == "dummy":
    # The dummy model always assigns 1/V to any unigram
    log_probs = [-math.log(vocab_size) for ngram in queried_ngrams]
    with open(log_prob_output_path, "w") as f:
        f.write("\n".join([str(x) for x in log_probs]))
#Adds all the log probabilities from unigram together
elif model_type == "1":
    total_log_prob = {}
    count = 0
    for ngram in queried_ngrams:

        total_prob = 0.0

        for w in ngram:
            if w in language_model:
                total_prob += -math.log(language_model[w])
            else:
                total_prob += -math.log(language_model["<unk>"])
        total_log_prob[count] = total_prob
        count = count + 1

    with open(log_prob_output_path, "w") as f:
        for x in total_log_prob:
            f.write("%.20f\n" % (total_log_prob[x]))
#Adds all the log probabilities from trigram togeter

elif model_type == "3":

    total_log_prob = {}
    num_tokens = 0
    count = 0
    for snt in queried_ngrams:
        log_prob = 0
        for w in range(0, len(snt), 1):

            if w < len(snt) - 2:
                themark = (snt[w] + " " + snt[w + 1] + " " + snt[w + 2])
                # print themark

                if themark in language_model:
                    log_prob = -math.log(language_model[themark])
                elif ("<unk>" + " " + snt[w + 1] + " " + snt[w + 2]) in language_model:
                    log_prob = -math.log(language_model["<unk>" + " " + snt[w + 1] + " " + snt[w + 2]])
                elif ("<unk>" + " " + snt[w + 1] + " " + "<unk>") in language_model:
                    log_prob = -math.log(language_model["<unk>" + " " + snt[w + 1] + " " + "<unk>"])
                elif (snt[w] + " " + "<unk>" + " " + snt[w + 2]) in language_model:
                    log_prob = -math.log(language_model[snt[w] + " " + "<unk>" + " " + snt[w + 2]])

                total_log_prob[count] = log_prob
        count = count + 1
    #Writes out to file
    with open(log_prob_output_path, "w") as f:
        for x in total_log_prob:
            f.write("%.20f\n" % (total_log_prob[x]))

#Adds all the log probabilities from smoothed trigram  togeter

elif model_type == "3s":
    total_log_prob = {}
    num_tokens = 0
    count = 0
    for snt in queried_ngrams:
        log_prob = 0

        for w in range(0, len(snt), 1):

            if w < len(snt) - 2:
                themark = (snt[w] + " " + snt[w + 1] + " " + snt[w + 2])
                # print themark

                if themark in language_model:
                    log_prob = -math.log(language_model[themark])
                elif ("<unk>" + " " + snt[w + 1] + " " + snt[w + 2]) in language_model:
                    log_prob = -math.log(language_model["<unk>" + " " + snt[w + 1] + " " + snt[w + 2]])
                elif ("<unk>" + " " + snt[w + 1] + " " + "<unk>") in language_model:
                    log_prob = -math.log(language_model["<unk>" + " " + snt[w + 1] + " " + "<unk>"])
                elif (snt[w] + " " + "<unk>" + " " + snt[w + 2]) in language_model:
                    log_prob = -math.log(language_model[snt[w] + " " + "<unk>" + " " + snt[w + 2]])
                else:
                    log_prob = -math.log(1 / vocab_size) #once again, this is the part of the dynamic smoothing.

                total_log_prob[count] = log_prob
        count = count + 1
    #Writes out to file
    with open(log_prob_output_path, "w") as f:
        for x in total_log_prob:
            f.write("%.20f\n" % (total_log_prob[x]))



#elif model_type == "3":

#elif model_type == "3s":


else:
    print("Not implemented!! ")
