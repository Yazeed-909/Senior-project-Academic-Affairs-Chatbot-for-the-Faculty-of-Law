# Import necessary libraries
import json
import random

import keras
import numpy as np
import pandas as pd
import tensorflow.python.keras
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from pyarabic.araby import *  # library for Arabic text preprocessing
from sklearn.preprocessing import LabelEncoder



class My_Model:

    def __init__(self, Dataset_location):
        self.Dataset = self.Loading_Dataset(Dataset_location)
        self.Dataset['input'].apply(self.Clean_Text)
        self.Tokenizer, self.Padding = self.Preprocess_Text(self.Dataset)
        self.Labelencoder = LabelEncoder()
        self.Leabels = self.Labelencoder.fit_transform(self.Dataset['tags'])
        self.Input_shape = self.Padding.shape[1]
        self.Vocabulary = len(self.Tokenizer.word_index)
        self.Output_length = self.Labelencoder.classes_.shape[0]
        self.Model = self.Model_Training(self.Vocabulary, self.Output_length, self.Input_shape, self.Leabels, self.Padding)


# Define a function for loading the dataset from a JSON file
    def Loading_Dataset(self,Dataset_location):
        Tags = []  # An empty list to store all the tags associated with the dataset intents
        Inputs = []  # An empty list to store all the input sentences associated with the dataset intents
        self.Responses = {}  # An empty dictionary to store all the responses associated with the dataset intents

        with open(Dataset_location, encoding="utf-8") as Dataset_content:
            data1 = json.load(Dataset_content)

        # Extract input and output pairs from the dataset
            for intent in data1['intents']:
                self.Responses[intent['tag']] = intent['responce']
                for lines in intent["input"]:
                    Inputs.append(lines)
                    Tags.append(intent['tag'])
        # Create a pandas DataFrame containing inputs and their corresponding tags
            Dataset = pd.DataFrame({"input": Inputs, "tags": Tags})
        return Dataset


# Define a function for cleaning the text
    def Clean_Text(self,Dataset):
    # Preprocess the text by removing Arabic diacritics and other special characters
        return ' '.join(tokenize(Dataset,
                                conditions=[],
                                morphs=[strip_tashkeel, strip_harakat, strip_tatweel]))


# Define a function for preprocessing the text
    def Preprocess_Text(self,Dataset):
        from keras.preprocessing.text import Tokenizer
    # Tokenize the input text using Keras' Tokenizer class
        Tokenizer = Tokenizer(oov_token="<OOV>")
        Tokenizer.fit_on_texts(Dataset['input'])
        Sequences = Tokenizer.texts_to_sequences(Dataset['input'])
    # Pad the sequences using Keras' pad_sequences function
        return Tokenizer, pad_sequences(Sequences)


# Define a function for training the model
    def Model_Training(self,Vocabulary, Output_length, Input_shape, Leabels, Padding):
    # Define the architecture of the model
        Model = tensorflow.keras.Sequential([
            tensorflow.keras.layers.Input(shape=Input_shape),
            tensorflow.keras.layers.Embedding(Vocabulary + 1, 32),
            tensorflow.keras.layers.Bidirectional(tensorflow.keras.layers.LSTM(16)),
            tensorflow.keras.layers.Dense(Output_length, activation="softmax")
        ])

    # Compile and train the model
        Model.compile(loss="sparse_categorical_crossentropy", optimizer='adam', metrics=['accuracy'])
        Model.summary()
        Model.fit(Padding, Leabels, epochs=100)
        return Model


# Define a function for predicting responses
    def Predict(self):
    # Get user input and preprocess it
        Prediction_input = input('You : ')
        Prediction_input = self.Clean_Text(Prediction_input)
        Text_list = []
        Text_list.append(Prediction_input)
    # Tokenize and pad the preprocessed text
        Prediction_input = self.Tokenizer.texts_to_sequences(Text_list)
        Prediction_input = np.array(Prediction_input).reshape(-1)
        Prediction_input = pad_sequences([Prediction_input], self.Input_shape)
        return Prediction_input
