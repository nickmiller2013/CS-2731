
"""""
Nick Miller
Homework 2
March 2, 2017

"""

import numpy as np

import sys

def Viterbi(observations, state_graph, startProb, transitionProbability, emissionProbability):
    #print state_graph
    viterbi = np.zeros((len(observations), len(state_graph))) #Path probability matrix
    backpointers = np.zeros((len(observations),len(state_graph)))
    #print emissionProbability[0][1]
    for s in range(0,len(state_graph)): #Initialization step
        #print s
        #print state_graph[s]
        #print float(startProb[state_graph[s]])
        #print float(emissionProbability[s,(int(observations[0])-1)])
        #print emissionProbability[s, int(observations[0])-1]
        #print "Here %d" % (float(startProb[state_graph[s]]) * float(emissionProbability[s,(int(observations[0])-1)]))
        viterbi[0,s] = float(startProb[state_graph[s]]) * float(emissionProbability[s,(int(observations[0])-1)])
    #print viterbi
    #print backpointers
    for k in range(1, len(observations)):# Recursion Step
        for s in range(0, len(state_graph)): #For each state
            #print k
            #print s

            store = np.zeros(len(state_graph))
            for j in range(0, len(state_graph)):
                store[j] = viterbi[int(k)-1, j] * transitionProbability[j, s] # Get the different values for the different states
            #print max(store)
            viterbi[k,s] = max(store) * emissionProbability[s, int(observations[k])-1] # Take the max value
            #print store
            #print "The store: "
            #print store
            backpointers[k,s] = np.argmax(store) #Get the index for the backpointers
            #print backpointers
            #print viterbi
            #print backpointers
    #print viterbi

    backtrack = np.zeros(len(observations))
    #backtrack[len(observations)-1]=backpointers[len(observations)-1, np.argmax(viterbi[len(observations)-1])]
    for i in reversed(range(0, len(observations)-1)):
        #print i
        #print np.argmax(viterbi[i])
        #print np.argmax(viterbi[i])
        backtrack[i] = backpointers[i+1, np.argmax(viterbi[i+1])] # Get the max positioning
    #print backpointers
    weather = []
    for k in backtrack:
        if k == 0:
            weather.append("Hot")
        if k == 1:
            weather.append("Cold")
    print "\n----------------Answer------------------"

    print ("->").join(weather)

    print "----------------Answer------------------"

    #print backtrack



filename = str(sys.argv[1])
observations = str(sys.argv[2])
#print observations


i=0
alphaCheck = 0
alphaNum = 0
Alphabet = {}
statesCheck = 0
statesNum = 0
States = {}
startProbCheck = 0
startProb = {}
transProbCheck = 0
tprc = 0
transitionProbability = np.zeros((1,1))
emissionProbability = np.zeros((1,1))
emisProbCheck = 0
eprc = 0


#This big thing is just for reading in the file and setting thiings up, like the probabilities.

f=open(filename,'r')
for line in f.readlines():
    values = line.split()

    if len(values) > 0:
        if alphaCheck == 2:
            Alphabet = values
            #print Alphabet
            alphaCheck = 0
        if alphaCheck == 1:
            alphaNum = values[0]
            alphaCheck = 2
            #print alphaNum
        if values[0] in "Alphabet":
            alphaCheck = 1
        if statesCheck == 2:
            States = values
            #print States
            statesCheck = 0
        if statesCheck == 1:
            statesNum = values[0]
            statesCheck = 2
            #print statesNum
        if values[0] in "States":
            statesCheck = 1
        if startProbCheck == 1:
            for i in range(0, int(statesNum)):
                startProb[States[i]] = values[i]

            #print startProb

            startProbCheck = 0
        if values[0] in "StartProbability":
            startProbCheck = 1
        if transProbCheck == 1:
            #print values

            if tprc is not int(statesNum):
                for l in range(len(values)):
                    transitionProbability[tprc][l] = values[l]
                tprc += 1
            if tprc is int(statesNum):
                transProbCheck = 0
            #print transitionProbability
        if values[0] in "TransitionProbability":
            transitionProbability = np.lib.pad(transitionProbability, ((0,int(statesNum)-1),(0,int(statesNum)-1)), 'constant', constant_values=(0))
            #print transitionProbability
            transProbCheck = 1

        if emisProbCheck == 1:
            #print values

            if eprc is not int(statesNum):
                for l in range(len(values)):
                    emissionProbability[eprc][l] = values[l]
                eprc += 1
            if eprc is int(statesNum):
                emisProbCheck = 0
            #print emissionProbability
        if values[0] in "EmissionProbability":
            emissionProbability = np.lib.pad(emissionProbability, ((0,int(statesNum)-1),(0,int(alphaNum)-1)), 'constant', constant_values=(0))
            #print transitionProbability
            emisProbCheck = 1
f.close()

#print Alphabet
#print States
#print startProb
#print transitionProbability
#print emissionProbability

Viterbi(observations,States, startProb, transitionProbability, emissionProbability)






