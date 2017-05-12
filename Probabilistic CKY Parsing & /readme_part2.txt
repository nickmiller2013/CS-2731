Nick Miller

The python version was Python 2.7.12

There are no known issues in my code.

How I did Binarization:

    Binarize is where I broke down rules that had more than 2 non-terminals on the right hand side.
I did this by looping through the established grammar and finding all with a length of 3 (4 because I accounted for space).
Once I got there I took away the first 2 non terminals and replaced it with a new value (which were "X1, X2, X3, .... XN") and with a probability of 1.0
I then put this into a new dictionary big_add which accounted for these values that had a new value and new terminals (i.e. X1 -> Aux NP)
I also had to account for the new rule that resulted from replacing the first 2 non-terminals with this new value and this was addressed
by putting these in another dictionary grammar_add. #While doing this kept track of the rules that also needed to be removed.
Adding big_add was easy because just had to update the dictionary. For grammar_add I had to loop through the dictionary and place the values
with there new holders.

Notes:

For the output I wasn't sure if you wanted the tree to have all the probabilities for each part or not. I asked
Professor Litman and she said just the probability of the whole sentence in the tree is what you were expecting so that
is what gets printed out under neath the tree.
