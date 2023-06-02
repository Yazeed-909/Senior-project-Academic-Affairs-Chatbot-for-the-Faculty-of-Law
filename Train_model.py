from ChatbotModel import  ChatbotModel

with open("Model_data.pkl", 'wb') as file:
    M = ChatbotModel("Model_data\\Dataset.json")
