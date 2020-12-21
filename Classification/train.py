import argparse
import random
import json
from sklearn.datasets import load_iris
from sklearn import feature_extraction
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


parser = argparse.ArgumentParser()
parser.add_argument('-t', '--file_name', type=str, default='train.json')
args = parser.parse_args()
file_name = args.file_name


with open('train.json', 'r', encoding='utf8') as train_set_json:
    train_set = json.load(train_set_json)
print(train_set[0])

# train_vector = feature_extraction.DictVectorizer
# train_data = train_vector.fit_transform('data')


