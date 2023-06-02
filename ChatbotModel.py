# Import necessary libraries
import pickle
import nltk
import numpy
import tflearn
from DatasetPars import DatasetPars


class ChatbotModel:

    def __init__(self, Dataset_location):
        # in the constructor we first pars the dataset and then do one hot encoding
        # after that we save the model in a file
        self.Dataset = DatasetPars(Dataset_location)
        self.Onehotencode()
        with open("Model_data.pkl", 'wb') as file:
            pickle.dump(self, file)
        self.Model_Training()

    def Load_model(self):
        # method used to load the model
        Input_length = len(self.Training[0])
        Output_length = len(self.Output[0])
        layer = tflearn.input_data(shape=[None, Input_length])
        layer = tflearn.fully_connected(layer, 8)
        layer = tflearn.fully_connected(layer, 8)
        layer = tflearn.fully_connected(layer, Output_length, activation="softmax")
        layer = tflearn.regression(layer)
        self.Model = tflearn.DNN(layer)
        # load the model
        self.Model.load("Model_data\\model.tflearn")

    def Onehotencode(self):
        # this method is used to onehotencode words and then save them in a bag of words
        # variable training is used as x to feed it to the model
        Training = []
        # variable output is used as y to feed it to the model
        Output = []
        # variable output_temp is a list that has zeros on the length of dataset tags
        Output_temp = [0 for i in range(len(self.Dataset.Tags))]
        # index is a counter on the length of Words_list
        # Word_list is a list that contain a list with the words from the dataset
        for Index, Word_list in enumerate(self.Dataset.Words_list):

            Bag = []
            # if this vocabulary word is on the list append 1 on the bag of words, otherwise append 0
            for Vocabulary_word in self.Dataset.Vocabulary:
                if Vocabulary_word in Word_list:
                    Bag.append(1)
                else:
                    Bag.append(0)
            # take a copy of output_tamp
            Output_row = Output_temp[:]

            # get the tag from words_list_tags with current index
            Tag = self.Dataset.Words_list_Tags[Index]
            # get that tag index from list tags
            Tag_index = self.Dataset.Tags.index(Tag)
            # but one on output_row using tag_index
            Output_row[Tag_index] = 1
            # append the current bag to training and the same thing with output
            Training.append(Bag)
            Output.append(Output_row)
        self.Training = numpy.array(Training)
        self.Output = numpy.array(Output)

    def Model_Training(self):
        # Define the architecture of the model.
        # get Training first row length and output first row to pass it to the model
        # as an input length and output length
        Input_length = len(self.Training[0])
        Output_length = len(self.Output[0])
        # first layer in the neural network in an input layer
        layer = tflearn.input_data(shape=[None, Input_length])
        # then we define two hidden layers with length of 8
        layer = tflearn.fully_connected(layer, 8)
        layer = tflearn.fully_connected(layer, 8)
        # then finally, we connect them with an output layer
        layer = tflearn.fully_connected(layer, Output_length, activation="softmax")
        # activation softmax used here to convert vector to probability
        # apply regression to minimize loss
        layer = tflearn.regression(layer)
        # create a deep learning model
        self.Model = tflearn.DNN(layer)
        # train the model with the training as x and output as y
        self.Model.fit(self.Training, self.Output, n_epoch=500, batch_size=8, show_metric=True)
        # then we save the model
        self.Model.save("Model_data\\model.tflearn")

    def bag_of_words(self, User_input):
        # This method takes the user input and then return a bag of words
        # it does that by comparing user input to the vocabulary
        bag = [0 for _ in range(len(self.Dataset.Vocabulary))]

        User_input = nltk.word_tokenize(User_input)

        for Word in User_input:
            for i, sentence in enumerate(self.Dataset.Vocabulary):
                if sentence == Word:
                    bag[i] = 1

        return numpy.array(bag)
