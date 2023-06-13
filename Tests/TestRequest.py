import unittest
from flask import Flask, request
from Chatbot import app
class TestRequest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_Chatbot(self):
        # Prepare mock request data
        request_data = {
            'WaId': 'sender_number',
            'ProfileName': 'profile_name',
            'Body': 'user_input'
        }
        # Send a mock POST request to /Chatbot with the request data
        response = self.app.post('/Chatbot', data=request_data)
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)



if __name__ == '__main__':
    unittest.main()
