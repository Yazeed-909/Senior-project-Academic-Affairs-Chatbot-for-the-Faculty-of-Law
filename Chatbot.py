import random

from My_Model import My_Model

M = My_Model('C:\\Users\\yzeed\\Desktop\\json.json')
Dataset=M.Loading_Dataset('C:\\Users\\yzeed\\Desktop\\json.json')
while True:
    Predicted_input = M.Model.predict(M.Predict())
    Predicted_input = Predicted_input.argmax()
    Predicted_input_Tag = M.Labelencoder.inverse_transform([Predicted_input])[0]
    print('Chatbot: ', random.choice(M.Responses[Predicted_input_Tag]))
    if Predicted_input_Tag == 'goodbye':
        break
# A loop that simulate chatbot session, it takes the user input and generate bot responses after it feeds the text to the model

