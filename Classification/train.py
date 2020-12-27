import argparse
import random
import json

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--file_name', type=str, default='train.json')
args = parser.parse_args()
file_name = args.file_name

with open('train.json', 'r', encoding='utf8') as train_set_json:
    train_set = json.load(train_set_json)
# print(train_set[0])


data_x = list()
data_y = list()
random.shuffle(train_set)
for i in train_set:
    data_x.append(i['data'])
    data_y.append(i['label'])

from sklearn.model_selection import train_test_split

test_data, train_data, test_label, train_label = train_test_split(data_x, data_y, test_size=0.8, random_state=2)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

text_clf = Pipeline([('vector', TfidfVectorizer()),
                     ('tfidf', TfidfTransformer()),
                     ('clf', LogisticRegression())])

text_clf.fit(train_data, train_label)
predict = text_clf.predict(test_data)

import numpy as np

np.mean(predict == test_label)
score = text_clf.score(test_data, test_label)
print(score)
