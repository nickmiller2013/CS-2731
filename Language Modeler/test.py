# Author: Yuhuan Jiang
# Version: 1.0
# Language: Python 2

import argparse
import math

# The following lines parse the command line arguments for you. You may ignore this part.
argument_parser = argparse.ArgumentParser("Intrinsic evaluator of language model. ")
argument_parser.add_argument('-m', '--model', help='The path to the directory containing the necessary files to recreate the language model.', required=True)
argument_parser.add_argument('-i', '--input', help='The path to the input file containing the testing sentences. ', required=True)
argument_parser.add_argument('-o', '--output', help='The path to the output file containing the perplexity score on the testing sentences. ', required=True)
args = argument_parser.parse_args()

# The following variables are created for your convenience.
# They are the values from the command line input.
model_dir = args.model
input_path = args.input
output_path = args.output


# START OF YOUR IMPLEMENTATION

# Utilities
def save_perplexity(perplexity):
    with open(output_path, "w") as f:
        f.write(str(perplexity))


# Prints out what this script does
print("Evaluating the perplexity of the model found at " + model_dir)
print("  on sentences found at " + input_path)
print("The perplexity scores will be saved at " + output_path)
print("")


# This variable holds the training sentences. Example content::
#
# train_snts = [
#     ["john", "has", "a",  "cat", "."],
#     ["mary", "has", "a",  "dog", "."],
#     ["john", "'s", "cat",  "is", "not", "a", "dog" "."],
#     ["mary", "'s", "dog",  "is", "not", "a", "cat" "."]"
# ]
#
testing_sentences = [line.rstrip('\n').split(' ') for line in open(input_path)]

language_model = {}

# Recreate the LM
with open(model_dir + "/model_type.txt") as f:
    model_type = f.readline()

with open(model_dir + "/vocab_size.txt") as f:
    vocab_size = float(f.readline())

with open(model_dir + "/model_type.txt") as f:
    model_type = (f.readline())
#Loading in the LM
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


# This is 1/vocab_size in log domain,
# We use log domain to avoid underflow,
log_prob = -math.log(vocab_size)


if model_type == "dummy":
    # We compute the perplexity by first computing the cross-entropy h, then use exp(h) as entropy.
    
    total_log_prob = 0.0
    num_tokens = 0
    
    for ws in testing_sentences:
        for w in ws:
            total_log_prob += log_prob
            num_tokens += 1
    
    h = -1.0 * total_log_prob / num_tokens
    perplexity = math.exp(h)
        
    # In fact, this uniform unigram LM will have a perplexity which is exactly equals to the vocabulary size.
    
    with open(output_path, "w") as f:
        f.writelines(str(perplexity))

#Gets the perplexity of unigram by getting the log probability, then the cross-entropy h, then use exp(h) as entropy.
elif model_type == "1":
    total_log_prob = 0.0
    num_tokens = 0

    for ws in testing_sentences:
        for w in ws:
            prob = 0.0
            if w in language_model:
                log_prob = -math.log(language_model[w])
            else:
                log_prob = -math.log(language_model["<unk>"])

            total_log_prob += log_prob
            num_tokens += 1

    h = -1.0 * total_log_prob / num_tokens
    perplexity = math.exp(h)
    with open(output_path, "w") as f:
        f.writelines(str(perplexity))

#Gets the perplexity of trigram by getting the log probability, then the cross-entropy h, then use exp(h) as entropy.

elif model_type == "3":
    total_log_prob = 0.0
    num_tokens = 0

    for snt in testing_sentences:
        snt.insert(0, "[s]")
        snt.insert(0, "[s]")
        snt.insert(len(snt), "[s/]")

        for w in range(0, len(snt), 1):

            if w < len(snt) - 2:
                themark = (snt[w] + " " + snt[w+1] + " " + snt[w+2])
                #print themark

                if themark in language_model:
                    log_prob = -math.log(language_model[themark])
                elif ("<unk>" + " " + snt[w+1] + " " + snt[w+2]) in language_model:
                    log_prob = -math.log(language_model["<unk>" + " " + snt[w+1] + " " + snt[w+2]])
                elif ("<unk>" + " " + snt[w+1] + " " + "<unk>") in language_model:
                    log_prob = -math.log(language_model["<unk>" + " " + snt[w+1] + " " + "<unk>"])
                elif (snt[w] + " " + "<unk>" + " " + snt[w+2]) in language_model:
                    log_prob = -math.log(language_model[snt[w] + " " + "<unk>" + " " + snt[w+2]])



                total_log_prob += log_prob
                log_prob = 0
                num_tokens += 1



    h = -1.0 * total_log_prob / num_tokens
    perplexity = math.exp(h)
    with open(output_path, "w") as f:
        f.writelines(str(perplexity))

elif model_type == "3s":
    total_log_prob = 0.0
    num_tokens = 0

    for snt in testing_sentences:
        snt.insert(0, "[s]")
        snt.insert(0, "[s]")
        snt.insert(len(snt), "[s/]")

        for w in range(0, len(snt), 1):

            if w < len(snt) - 2:
                themark = (snt[w] + " " + snt[w+1] + " " + snt[w+2])
                #print themark

                if themark in language_model:
                    log_prob = -math.log(language_model[themark])
                elif ("<unk>" + " " + snt[w+1] + " " + snt[w+2]) in language_model:
                    log_prob = -math.log(language_model["<unk>" + " " + snt[w+1] + " " + snt[w+2]])
                elif ("<unk>" + " " + snt[w+1] + " " + "<unk>") in language_model:
                    log_prob = -math.log(language_model["<unk>" + " " + snt[w+1] + " " + "<unk>"])
                elif (snt[w] + " " + "<unk>" + " " + snt[w+2]) in language_model:
                    log_prob = -math.log(language_model[snt[w] + " " + "<unk>" + " " + snt[w+2]])
                else:
                    log_prob = -math.log(1 / vocab_size) #Difference here from unsmoothed. This accounts for the adding one and the set of 3 not being in the set.

                total_log_prob += log_prob
                num_tokens += 1



    h = -1.0 * total_log_prob / num_tokens
    perplexity = math.exp(h)
    with open(output_path, "w") as f:
        f.writelines(str(perplexity))
else:
    print("Not implemented!! ")
