import nltk

nltk.download('punkt')
import json


class DatasetPars:
    def __init__(self, Dataset_location):
        self.Loading_Dataset(Dataset_location)

    def Loading_Dataset(self, Dataset_location):
        # a list to save vocabulary (each word in the dataset)
        self.Vocabulary = []
        # tags of the dataset
        self.Tags = []
        # a dictionary used to give each tag an index in order to use it with number selection in the menu
        self.Index = {}
        # list with a list in it for each sentence
        self.Words_list = []
        # a list that has the tag for each word in the vocabulary is store the tag for each word
        self.Words_list_Tags = []
        # dictionary with responses in it
        self.Response = {}

        try:
            with open(Dataset_location, encoding="utf-8") as Dataset_content:
                # open the dataset file
                Dataset_file = json.load(Dataset_content)
                # get the set in the dataset
                for Set in Dataset_file['dataset']:
                    # store response with the tag
                    self.Response.update({Set["tag"]: Set['response']})
                    # if the index is not 00 (we don't want to store it in the index dictionary)
                    if Set["index"] is not "00":
                        # if not, then store it
                        self.Index.update({int(Set["index"]): Set["tag"]})
                    # we get the input in the set
                    for Input in Set['input']:
                        # tokenize it with nltk tokenize method
                        word_tokenized = nltk.word_tokenize(Input)
                        # store the tokenized word in the vocabulary as word by word,
                        # Words list as a list and then store the current tag in words_list_tags
                        self.Vocabulary.extend(word_tokenized)
                        self.Words_list.append(word_tokenized)
                        self.Words_list_Tags.append(Set["tag"])

                    if Set['tag'] not in self.Tags:
                        # if the tag was not stored yet, then store it in the list tags
                        self.Tags.append(Set['tag'])
                # make vocabulary a (set) by removing repeated words
                self.Vocabulary = sorted(list(set(self.Vocabulary)))

        except FileNotFoundError:
            print("Dataset file was not found")
