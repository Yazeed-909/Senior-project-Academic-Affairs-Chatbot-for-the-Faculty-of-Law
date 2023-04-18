# Import necessary libraries
import json
import random
import numpy as np
import pandas as pd
import tensorflow.python.keras
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from pyarabic.araby import *  # library for Arabic text preprocessing
from sklearn.preprocessing import LabelEncoder

Tags = []  # An empty list to store all the tags associated with the dataset intents
Inputs = []  # An empty list to store all the input sentences associated with the dataset intents
Responses = {}  # An empty dictionary to store all the responses associated with the dataset intents


# Define a function for loading the dataset from a JSON file
def Loading_Dataset(Dataset_location):
    with open(Dataset_location, encoding="utf-8") as Dataset_content:
        data1 = json.load(Dataset_content)

        # Extract input and output pairs from the dataset
        for intent in data1['intents']:
            Responses[intent['tag']] = intent['responce']
            for lines in intent["input"]:
                Inputs.append(lines)
                Tags.append(intent['tag'])
        # Create a pandas DataFrame containing inputs and their corresponding tags
        Dataset = pd.DataFrame({"input": Inputs, "tags": Tags})
    return Dataset


# Define a function for cleaning the text
def Clean_Text(Dataset):
    # Preprocess the text by removing Arabic diacritics and other special characters
    return ' '.join(tokenize(Dataset,
                             conditions=[],
                             morphs=[strip_tashkeel, strip_harakat, strip_tatweel]))


# Define a function for preprocessing the text
def Preprocess_Text(Dataset):
    from keras.preprocessing.text import Tokenizer
    # Tokenize the input text using Keras' Tokenizer class
    Tokenizer = Tokenizer(oov_token="<OOV>")
    Tokenizer.fit_on_texts(Dataset['input'])
    Sequences = Tokenizer.texts_to_sequences(Dataset['input'])
    # Pad the sequences using Keras' pad_sequences function
    return Tokenizer, pad_sequences(Sequences)


# Define a function for training the model
def Model_Training(Vocabulary, Output_length, Input_shape, Leabels, Padding):
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
def Predict():
    # Get user input and preprocess it
    Prediction_input = input('You : ')
    Prediction_input = Clean_Text(Prediction_input)
    Text_list = []
    Text_list.append(Prediction_input)
    # Tokenize and pad the preprocessed text
    Prediction_input = Tokenizer.texts_to_sequences(Text_list)
    Prediction_input = np.array(Prediction_input).reshape(-1)
    Prediction_input = pad_sequences([Prediction_input], Input_shape)
    return Prediction_input


# Load the dataset and preprocess it
Dataset = Loading_Dataset("C:\\Users\\yzeed\\Desktop\\json.json")
Dataset['input'].apply(Clean_Text)
Tokenizer, Padding = Preprocess_Text(Dataset)
Labelencoder = LabelEncoder()
Leabels = Labelencoder.fit_transform(Dataset['tags'])
Input_shape = Padding.shape[1]
Vocabulary = len(Tokenizer.word_index)
Output_length = Labelencoder.classes_.shape[0]
# Train the model
Model = Model_Training(Vocabulary, Output_length, Input_shape, Leabels, Padding)
# A loop that simulate chatbot session, it takes the user input and generate bot responses after it feeds the text to the model
while True:
    Predicted_input = Model.predict(Predict())
    Predicted_input = Predicted_input.argmax()
    Predicted_input_Tag = Labelencoder.inverse_transform([Predicted_input])[0]
    print('Chatbot: ', random.choice(Responses[Predicted_input_Tag]))
    if Predicted_input_Tag == 'goodbye':
        break
