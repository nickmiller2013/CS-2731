from nltk.corpus import stopwords
import nltk
s1 = 'Some big dog went to get the work at 7.'

s1 = nltk.word_tokenize(s1)

words = [w for w in s1 if w not in stopwords.words('english')]
bow = " ".join(words)

print bow