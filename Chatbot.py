import pickle
import random
import numpy
from DatasetPars import DatasetPars
from My_Model import My_Model

# loading dataset
Dataset = DatasetPars("Model_data\\Dataset.json")

try:
    with open("Model_data.pkl", 'rb') as file:
        M = pickle.load(file)
        M.Load_model()
except:
    with open("Model_data.pkl", 'wb') as file:
        M = My_Model("Model_data\\Dataset.json")

while True:
    User_input = input("You: ")
    if User_input.lower() == "quit":
        break
    results = M.Model.predict([M.bag_of_words(User_input)])[0]
    results_index = numpy.argmax(results)
    tag = M.Dataset.Labels[results_index]
    if results[results_index] > 0.80:
        print('Chatbot: ', (random.choice(Dataset.Responce.get(tag))))
    else:
        print("i dont understand ")
