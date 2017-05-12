# CS 2731 Final Project
Fake News Challenge - Matthew O'Brien, Nick Miller, and Nathaniel Blake

Assignment Page:
http://people.cs.pitt.edu/~yuhuan/teaching/nlp-2017-spring/project/

To run the program:

`python3 main.py bodies.csv train.csv test.csv answers_out.csv`

where the command-line parameters follow [this specification.](http://people.cs.pitt.edu/~yuhuan/teaching/nlp-2017-spring/project/prelim-sub.html)

## Dependencies:
 - numpy-1.12.1
 - scikit-learn-0.18.1
 - nltk-3.2.2
 - nltk.corpus.stopwords
 - nltk.corpus.wordnet

To install them:
```
sudo pip install numpy sklearn nltk
python3 -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"
```
