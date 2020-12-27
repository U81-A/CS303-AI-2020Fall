import json
import random
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier

if __name__ == "__main__":
    with open("train.json", 'r', encoding='utf8') as fp:
        json_data = json.load(fp)

    data = []
    label = []
    test_data = []
    test_label = []

    for I in range(0, len(json_data)):
        if random.random() > 0.8:
            test_data.append(json_data[I]["data"])
            test_label.append(json_data[I]["label"])
        else:
            data.append(json_data[I]["data"])
            label.append(json_data[I]["label"])

    text_clf = Pipeline([('vect', CountVectorizer()),
                         ('tfidf', TfidfTransformer()),
                         # ('clf', MultinomialNB()),
                         ('clf', SGDClassifier(loss='hinge',
                                               penalty='l2',
                                               alpha=1e-4,
                                               random_state=42,
                                               max_iter=500,
                                               tol=None)
                          )
                         ])

    text_clf.fit(data, label)
    predicted = text_clf.predict(test_data)
    np.mean(predicted == test_label)
    score = text_clf.score(test_data, test_label)
print(score)
