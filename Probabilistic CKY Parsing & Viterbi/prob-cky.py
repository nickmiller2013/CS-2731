
"""""
Nick Miller
Homework 2
March 2, 2017

"""

import sys




#def setGrammar(filename):


#The Tree class is what I used to build the output of the program.
class Tree(object):
    def __init__(self):
        self.left = None
        self.right = None
        self.pref = None
        self.probability = None
        self.word = None


#Used for error checking the grammar
def print_grammar(grammar_dict):
    for x in grammar_dict:
        print (x)
        for y in grammar_dict[x]:
            print (y,grammar_dict[x][y])


#Simplify combined the grammar if there was was a single value on the right side of the -> and it wasn't a word
#Put it in dictionary grammar_add then combined the 2 dictionaries.
def simplify(grammar_dict, word_storage):
    grammar_add = {}
    #terminals = ["Det", "Noun", "Verb", "Pronoun", "Proper-Noun", "Aux", "Preposition"]
    for k in grammar_dict:
        if k in word_storage:
            continue
            #print k

        else:
            #print "Outside " + k
            for y in grammar_dict[k]:
                #print "Right here " + y.strip()

                for j in grammar_dict:
                    #print j
                    if j == y.strip():
                        #print j
                        for z in grammar_dict[y.strip()]:
                            #print z
                            #print "The continuing is: " + z
                            #print j
                            #print y
                            #print k
                            #print z
                            grammar_add[k + " " + z] = grammar_dict[j][z] * grammar_dict[k][y]

                        #print "Inside"

    #for k in grammar_add:
        #print k

    for x in grammar_add:
        #print x
        k = x.split(" ")
        #print k
        #print k[0]
        #print k
        #print ("Printing out: " + k[1] + " " + k[2])
        if len(k) is 3:
            if (k[2]) not in grammar_dict[k[0]]:

                grammar_dict[k[0]][(" " + k[2])] = grammar_add[x]
        elif len(k) is 4:
            if (k[2] + " " + k[3]) not in grammar_dict[k[0]]:

                grammar_dict[k[0]][(" " + k[2] + " " + k[3])] = grammar_add[x]
    #print grammar_add
    return grammar_dict

#Binarize is where I broke down rules that had more than 2 non-terminals on the right hand side.
#I did this by looping through the established grammar and finding all with a length of 3 (4 because I accounted for space).
# Once I got there I took away the first 2 non terminals and replaced it with a new value (which were "X1, X2, X3, .... XN") and with a probability of 1.0
#I then put this into a new dictionary big_add which accounted for these values that had a new value and new terminals (i.e. X1 -> Aux NP)
#I also had to account for the new rule that resulted from replacing the first 2 non-terminals with this new value and this was addressed
#by putting these in another dictionary grammar_add. #While doing this kept track of the rules that also needed to be removed.
#Adding big_add was easy because just had to update the dictionary. For grammar_add I had to loop through the dictionary and place the values
#with there new holders.
def binarize(grammar_dict):
    count = 1
    grammar_add = {}
    big_add = {}
    toRemove = []
    for x in grammar_dict:
        #print x
        for y in grammar_dict[x]:
            j = y.split(" ")
            if len(j) is 4:
                #print j
                toAdd = (j[1] + " " + j[2])
                grammar_add[x + " " + "X" + str(count) + " " + j[3]] = grammar_dict[x][y] #Fixing rule
                big_add["X" + str(count)] = {(" " + toAdd):1.0} #New rules
                toRemove.append(x + " " + y) #Getting rule to remove

                count += 1

    grammar_dict.update((big_add))#Added new rule
    #print_grammar((grammar_dict))
    #print big_add

    for x in grammar_add:#Adjusting fixed rules
        #print x
        k = x.split(" ")
        #print k
        grammar_dict[k[0]][" " + (k[1] + " " + k[2])] = grammar_add[x]
    #print grammar_add
    #print_grammar((grammar_dict))
    for k in toRemove: #Removing old rules
        j = k.split("  ")
        del grammar_dict[j[0]][" " + j[1]]
    #print toRemove

    #print_grammar((grammar_dict))

    #print count

    return grammar_dict


##This sets up out grammar from the input file into list
def inputGrammar(filename):
    with open(filename) as f:
        lines = f.readlines()
    return [x.strip("\n").split("->") for x in lines]

#This takes in the list from input grammar and puts it into a dictionary that has the associated values correct.
def dict_grammar(split_grammar):
    grammar_dict = {}
    word_storage = []
    #print split_grammar
    for k in split_grammar:
        #print k
        grammar_split = k[0].split(" ")
        #print grammar_split
        if len(grammar_split) is 3:
            if grammar_split[1] in grammar_dict:
                grammar_dict[grammar_split[1]][k[1]] = float(grammar_split[0].strip("[]"))
            else:
                grammar_dict[grammar_split[1]] = {k[1]: float(grammar_split[0].strip("[]"))}
        elif len(grammar_split) is 2:
            #print grammar_split
            word_storage.append(grammar_split[0])

            #print grammar_split[0]
            for x in k[1].split("|"):
                j = x.split(" ")
                #print j
                if grammar_split[0] in grammar_dict:
                    grammar_dict[grammar_split[0]][(" " + j[1])] = float(j[2].strip("[]"))
                else:
                    grammar_dict[grammar_split[0]] = {(" " + j[1]): float(j[2].strip("[]"))}

    return (grammar_dict , word_storage)
    #print grammar_dict

#This is for looping through the tree
def print_root(root,k):
    if root.left is not None:
        #print "left"
        k.append("[")
        #print_tree(root.left)
        k.append(root.left.pref)
        #k.append(str(root.left.probability))

        #print root.left.pref

        k = print_root(root.left, k)
        k.append("]")

    if root.right is not None:
        #print "right"
        k.append("[")
        #print_tree(root.right)

        k.append(root.right.pref)
        #k.append(str(root.right.probability))

        #print root.right.pref
        #print root.right.pref

        k = print_root(root.right, k)

        k.append("]")



    if root.left is None and root.right is None:
        #print root.pref
        #print "Word"
        k.append(root.word)



   # print root.pref

    #print "Back"
    return k

#This finds the max probability of the tree in the top right corner and prints out the results
def print_br(backRoot):
    n = len(backRoot)
    min = 0
    root = Tree()

    node_store = []

    for nodes in backRoot[0][n-1]:
        k = []

        # print nodes
        if nodes.pref == "S":
            #k.append("[S")
            #k = print_root(nodes, k)
            #k.append("]")
            #print " ".join(k)

            if nodes.probability >= min:
                #print "in"
                #print "[s "
                root = nodes
                #print root.probability
                min = nodes.probability
                node_store.append(nodes)
    #k.append("s")
    k = []
    printer = []
    #print node_store

    for j in node_store:
        k = ["[S"]
        k = print_root(j, k)
        k.append("]")
        printer.append(" ".join(k))

    print "\n----------------Answer------------------"
    print max(printer, key=len)
    print "The probability of the sentence in the tree is: " + str(node_store[0].probability)
    print "----------------Answer------------------"



#This is the actual process of going through the cky parse
def cky(sentence, grammar):
    words = sentence.split()
    #print words
    n = len(words)

    diagnol = [[[] for i in range(n)] for j in range(n)] #Sets up NxN matrix for values
    backRoot = [[[] for i in range(n)] for j in range(n)] #Sets up NxN matrix for backtracking

    for j in range(0, n):#Loops through the sentences
        for k in grammar:#Loops through our grammar dictionary
            #print "The context: " + k
            for l in grammar[k]: #This just sets up the JxJ spots in the matrix -- The diagnol
                #print l
                #print "The words: " + words[j-1]
                #print "The indexs: " + l
#                print words[j]
#                print l
#                print j

                if l == (" " + words[j]):
                    #print "In"
                    root = Tree()
                    root.pref = k
                    root.probability = grammar[k][l]
                    #print words[j]
                    root.word = words[j]
                    diagnol[j][j].append(k + ": " + str(grammar[k][l]))
                    backRoot[j][j].append(root)
                    #print k + "->" + l + ": " + str(grammar[k][l])
        #print "1st: " + str(j)
        if j > 0: #Used because this loop won't have any effect in the top left of the matrix or 0x0 part
            for i in reversed(range(0, j)): #Go in reverse up the matrix from J-1xJ
                #print i
                #print diagnol[i][j]
                #for k in range(i+1, j):
                #    print diagnol[k][j]
                #print j #j is the col
                #print i #i is the row
                #print "Here" + str(diagnol[i][j])
                for k in reversed(range(0, j)):
                    #print "To the left: " + str(diagnol[i][k])
                    #print "To the bottom: " + str(diagnol[j][j])
                    for a in grammar_dict: #Loop through our dictionary

                        for b in grammar_dict[a]:

                            d = b.strip().split(" ")
                            if len(d) is 2:
                                #print d
                                #print "new"
                                for c in diagnol[i][k]: #Check if the rule is here
                                    splitIn = c.split(": ")
                                    #print splitIn
                                    #print b[0]
                                    #print splitIn[0]
                                    if d[0] == splitIn[0]:
                                        for p in reversed(range(i,j+1)):
                                           # print p
                                            for e in diagnol[p][j]:
                                                splitOut = e.split(": ")
                                                if d[1] == splitOut[0]:
                                                   # print d[0] + " and " + d[1]
                                                   # print "i is currently: " + str(i)
                                                   # print "j is currently: " + str(j)

                                                    diagnol[i][j].append(a + ": " + str(grammar_dict[a][b] * float(splitIn[1]) * float(splitOut[1]))) #Add the rule and associated probabilities
                                                    for u in backRoot[i][k]: #Adding the tree nodes to the specific index
                                                        for v in backRoot[p][j]:
                                                            if u.pref == d[0] and v.pref == d[1]:
                                                                #print str(i) + " and " + str(j)
                                                                #print a + "->" + b + ": " + str(grammar_dict[a][b] * float(splitIn[1]) * float(splitOut[1]))
                                                                root = Tree()
                                                                root.pref = a
                                                                root.probability = grammar_dict[a][b] * float(splitIn[1]) * float(splitOut[1])
                                                                root.left = u
                                                                root.right = v
                                                                backRoot[i][j].append(root)







   # print "This area"
    #for k in range(len(diagnol)):
    #    for j in range(len(diagnol[k])):
    #        print backRoot[k][j]

    #    print "\n"

    print_br(backRoot)




filename = str(sys.argv[1])
sentence = str(sys.argv[2])
split_grammar = inputGrammar(filename)
grammar_dict, word_storage = dict_grammar(split_grammar)
#print_grammar(grammar_dict)

grammar_dict = binarize(grammar_dict)
#print_grammar(grammar_dict)
#print word_storage

#Simplified twice to cut down on some rules -- what she does on slide in some cases.
grammar_dict = simplify(grammar_dict, word_storage)
grammar_dict = simplify(grammar_dict, word_storage)

cky(sentence, grammar_dict)

#print_grammar(grammar_dict)

#print split_grammar