# Import necessary libraries
import pickle
import nltk
import numpy
import tflearn
from nltk import LancasterStemmer
stemmer = LancasterStemmer()
from DatasetPars import DatasetPars


class My_Model:

    def __init__(self, Dataset_location):
        self.Dataset = DatasetPars(Dataset_location)
        self.Onehotencode()
        with open("Model_data.pkl", 'wb') as file:

            pickle.dump(self, file)
        self.Model_Training()

    def Load_model(self):
    #method used to load the model
        layer = tflearn.input_data(shape=[None, len(self.Training[0])])
        layer = tflearn.fully_connected(layer, 8)
        layer = tflearn.fully_connected(layer, 8)
        layer = tflearn.fully_connected(layer, len(self.Output[0]), activation="softmax")
        layer = tflearn.regression(layer)
        self.Model = tflearn.DNN(layer)
        self.Model.load("Model_data\\model.tflearn")

    def Onehotencode(self):
    #this method is used to onehotencode words and then save them in a bag of words
        Training = []
        Output = []

        Output_temp = [0 for _ in range(len(self.Dataset.Labels))]

        for List_count, Word in enumerate(self.Dataset.Words_list):
            Bag = []
            wrds = [stemmer.stem(w.lower()) for w in Word]
            # if this vocabulary word is on the list append 1 on the bag of words otherwise append 0
            for w in self.Dataset.Vocabulary:
                if w in wrds:
                    Bag.append(1)
                else:
                    Bag.append(0)

            Output_row = Output_temp[:]
            Output_row[self.Dataset.Labels.index(self.Dataset.Words_list_labels[List_count])] = 1

            Training.append(Bag)
            Output.append(Output_row)

            self.Training = numpy.array(Training)
            self.Output = numpy.array(Output)


    def Model_Training(self):
    # Define the architecture of the model.

        layer = tflearn.input_data(shape=[None, len(self.Training[0])])
        layer = tflearn.fully_connected(layer, 8)
        layer = tflearn.fully_connected(layer, 8)
        layer = tflearn.fully_connected(layer, len(self.Output[0]), activation="softmax")
        layer = tflearn.regression(layer)

        self.Model = tflearn.DNN(layer)

        self.Model.fit(self.Training, self.Output, n_epoch=1000, batch_size=8, show_metric=True)

        self.Model.save("Model_data\\model.tflearn")

    def bag_of_words(self,User_input):
    # This method takes the user input and then return a bag of words
    # it does that by comparing user input to the voabulary
        bag = [0 for _ in range(len(self.Dataset.Vocabulary))]

        User_input = nltk.word_tokenize(User_input)

        for Word in User_input:
            for i, sentence in enumerate(self.Dataset.Vocabulary):
                if sentence == Word:
                    bag[i] = 1

        return numpy.array(bag)