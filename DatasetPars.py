import nltk

nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer

stemmer = LancasterStemmer()

import json


class DatasetPars:
    def __init__(self, Dataset_location):
        self.Loading_Dataset(Dataset_location)

    def Loading_Dataset(self, Dataset_location):
        self.Vocabulary = []
        self.Labels = []
        self.Words_list = []
        self.Words_list_labels = []
        self.Responce = {}
        with open(Dataset_location, encoding="utf-8") as Dataset_content:
            data1 = json.load(Dataset_content)

            # Extract input and output pairs from the dataset
            for intent in data1['intents']:

                self.Responce.update({intent["tag"]: intent['responce']})

                for Input in intent['input']:
                    wrds = nltk.word_tokenize(Input)
                    self.Vocabulary.extend(wrds)
                    self.Words_list.append(wrds)
                    self.Words_list_labels.append(intent["tag"])

                if intent['tag'] not in self.Labels:
                    self.Labels.append(intent['tag'])
            self.Vocabulary = [stemmer.stem(w) for w in self.Vocabulary if w != "?"]
            self.Vocabulary = sorted(list(set(self.Vocabulary)))
        # Define a function for loading the dataset from a JSON file
