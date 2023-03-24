import os

from flask import Flask, request
from twilio.jwt import client
from twilio.rest import Client

app = Flask(__name__)
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)


@app.route('/bot', methods=['POST'])
# Bot method is responsible for handling the user request it takes the request and the process
# it and after that it reply back to the user with the correct response
def bot():
    user_message = request.values.get('Body', ' ').lower()
    url = None
    if 'الخطة الدراسية' in user_message:
        text = "الخطة الدراسية"
        url = "https://www.africau.edu/images/default/sample.pdf"
    elif 'القاعات' in user_message:
        text = "القاعات"
    elif 'الاختبارات' in user_message:
        text = "الاختبارات"
    else:
        text = "ممكن تعيد صياغة الرسالة بشكل افضل؟"
    message = client.messages.create(
        to='whatsapp:+' + request.values.get('WaId'),
        from_='whatsapp:+14155238886',
        body=text,
        media_url=url)
    return "test"


if __name__ == "__main__":
    app.run(debug=True)
