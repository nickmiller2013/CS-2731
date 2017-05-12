# Author: Yuhuan Jiang
# Version: 1.0
# Language: Python 2

import argparse
from decimal import *
import math


argument_parser = argparse.ArgumentParser("Genre detection task runner. ")
argument_parser.add_argument('--wsjmodel', help='The path to the directory of the model files for the WSJ language model.', required=True)
argument_parser.add_argument('--sbmodel', help='The path to the directory of the model files for the Switchboard language model.', required=True)
argument_parser.add_argument('-i', '--input', help='The path to the file containing the sentences to be labeled. ', required=True)
argument_parser.add_argument('-o', '--output', help='The path to the file of the answer output of this script. ', required=True)

args = argument_parser.parse_args()

# Use these variables to detect the model requested by the command line user
wsj_model_dir = args.wsjmodel
sb_model_dir = args.sbmodel
input_path = args.input
output_path = args.output

print("Running the genre detection task with wsj model found at " + wsj_model_dir)
print("                                      sb  model found at " + sb_model_dir)
print("  using the test sentences found at " + input_path)
print("The answers will be output at " + output_path)
print("")

# START OF YOUR IMPLEMENTATION
with open(wsj_model_dir + "/vocab_size.txt") as f:
    wsj_vocab_size = float(f.readline())
with open(sb_model_dir + "/vocab_size.txt") as f:
    sb_vocab_size = float(f.readline())
wsj_language_model = {}
sb_language_model = {}

with open(wsj_model_dir + "vocab_prob.txt") as f:
    for line in f:
        #print line
        toSplit = line.split(" ")
        #print len(toSplit)
        if len(toSplit) == 4:
        #    print Decimal(toSplit[3])
            wsj_language_model[toSplit[0] + " " + toSplit[1] + " " + toSplit[2]] = float(Decimal(toSplit[3]))
        else:
            wsj_language_model[toSplit[0]] = float(Decimal(toSplit[1]))

with open(sb_model_dir + "vocab_prob.txt") as f:
    for line in f:
        #print line
        toSplit = line.split(" ")
        #print len(toSplit)
        if len(toSplit) == 4:
        #    print Decimal(toSplit[3])
            sb_language_model[toSplit[0] + " " + toSplit[1] + " " + toSplit[2]] = float(Decimal(toSplit[3]))
        else:
            sb_language_model[toSplit[0]] = float(Decimal(toSplit[1]))

snts = [line.rstrip('\n').split(' ') for line in open(input_path)]

labels = ["wsj" for snt in snts]
count = 0
for snt in snts:
    snt.insert(0, "[s]")
    snt.insert(0, "[s]")
    snt.insert(len(snt), "[s/]")
    num_tokens = 0
    probability_wsj = 0
    probability_sb = 0
    #Gets the log probability per sentence, adds it together and decides whether or which log probability is higher.
    #There is a bug somewhere because results aren't results from gold.txt. I just can't figure out the bug.
    for w in range(0, len(snt), 1):


        if w < len(snt) - 2:
            themark = (snt[w] + " " + snt[w+1] + " " + snt[w+2])
            #print themark
            prob = 0
            if themark in wsj_language_model:
                prob = wsj_language_model[themark]
            elif ("<unk>" + " " + snt[w+1] + " " + snt[w+2]) in wsj_language_model:
                prob = (wsj_language_model["<unk>" + " " + snt[w+1] + " " + snt[w+2]])
            elif ("<unk>" + " " + snt[w+1] + " " + "<unk>") in wsj_language_model:
                prob = (wsj_language_model["<unk>" + " " + snt[w+1] + " " + "<unk>"])
            elif (snt[w] + " " + "<unk>" + " " + snt[w+2]) in wsj_language_model:
                prob = (wsj_language_model[snt[w] + " " + "<unk>" + " " + snt[w+2]])
            else:
                prob = (1 / wsj_vocab_size)
            #print("The prob for wsj & %s is: %.20f" % (themark, prob))

            probability_wsj = probability_wsj + -math.log(prob)
            #print("The prob for wsj is: %.20f" % (probability_wsj))


            #print themark
            prob = 0
            if themark in sb_language_model:
                prob = sb_language_model[themark]
            elif ("<unk>" + " " + snt[w+1] + " " + snt[w+2]) in sb_language_model:
                prob = (sb_language_model["<unk>" + " " + snt[w+1] + " " + snt[w+2]])
            elif ("<unk>" + " " + snt[w+1] + " " + "<unk>") in sb_language_model:
                prob = (sb_language_model["<unk>" + " " + snt[w+1] + " " + "<unk>"])
            elif (snt[w] + " " + "<unk>" + " " + snt[w+2]) in sb_language_model:
                prob = (sb_language_model[snt[w] + " " + "<unk>" + " " + snt[w+2]])
            else:
                prob = (1 / sb_vocab_size)
            #print("The prob for sb & %s is: %.20f" % (themark, prob))

            probability_sb = probability_sb + -math.log(prob)
            num_tokens += 1
            #print("The prob for sb is: %.20f" % (probability_sb))

    h = -1.0 * probability_sb / num_tokens
    sb_perplexity = math.exp(h)
    h = -1.0 * probability_wsj / num_tokens
    wsj_perplexity = math.exp(h)
    print("The prob for wsj is: %.20f" % (probability_wsj))

    print("The prob for sb is: %.20f" % (probability_sb))

    if wsj_perplexity > sb_perplexity:

        labels[count] = "wsj"
    else:
        labels[count] = "sb"
    count += 1
#print labels

#Write out to file.
with open(output_path, "w") as f:
    f.writelines("\n".join(labels))
