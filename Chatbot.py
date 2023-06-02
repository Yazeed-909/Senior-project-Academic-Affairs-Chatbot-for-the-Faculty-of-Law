# -- coding: utf-8 --
import logging
import os
import pickle
import random
import re
import firebase_admin
import numpy
from firebase_admin import exceptions
from firebase_admin.exceptions import FirebaseError
from flask import Flask, request
from pyarabic.araby import strip_tashkeel, strip_tatweel
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from DatabaseConnection import DatabaseConnection

app = Flask(__name__)
First_message = True
attempts = 0
# The list of offered services

menu = \
    "الخدمات التي استطيع خدمتك فيها حاليا:\n\n1️⃣ الخطة الدراسية.\n2️⃣ التقويم الاكاديمي.\n3️⃣ قاعات المواد.\n4️⃣ " \
    "بيانات التواصل الرسمية مع الكلية.\n5️⃣ بيانات اعضاء هيئة التدريس.\n6️⃣ الاختبارات " \
    "النصفية.\n7️⃣ الاختبارات النهائية.\n8️⃣ مواعيد مهمة.\n\nيرجى كتابة اي من الاستفسارات الاتية لاستطيع خدمتك او " \
    "بامكانك كتابة الرقم للاختيار من القائمة."

# get twilio sid and auth token that are stored in the environment values
try:
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    if account_sid is None or auth_token is None:
        raise EnvironmentError("environment value not found ")
except EnvironmentError as e:
    print(e)
    exit(1)

client = Client(account_sid, auth_token)

DBconnection = DatabaseConnection.GetDBConnection()

# enable logging to see the request and response
logging.basicConfig()
client.http_client.logger.setLevel(logging.INFO)

# loading the model from a file
try:
    with open("Model_data.pkl", 'rb') as file:
        Model_data = pickle.load(file)
        Model_data.Load_model()
# if model was not found the program terminates
except FileNotFoundError:
    print("Model was not found please run Train_model.py to train the model ")
    exit(1)


def strip_unwanted_chars(text):
    # This method is responsible to remove unwanted words
    # Define a pattern for removing: \w\(english characters,numbers,special characters) \s\ for taps and spaces

    pattern = r'[^\w\s\u0621-\u063A\u0641-\u064A]+'
    text = re.sub(pattern, ' ', text)
    # Remove tashkeel in the text
    text = strip_tashkeel(text)
    # Remove tatweel in the text
    text = strip_tatweel(text)
    return text


def extract_number(text):
    # This method is responsible to strip numbers from words
    # Define the pattern to match numbers including all arabic and english
    pattern = r'[\d٠١٢٣٤٥٦٧٨٩]+'

    # Find all matches in the string
    matches = re.findall(pattern, text)

    if matches:
        # Concatenate all matched digits and convert to an integer
        extracted_number = int(''.join(matches))

        return extracted_number
    else:
        return None


# Make the app receive requests from type (POST) on /Chatbot
@app.route('/Chatbot', methods=['POST'])
def Chatbot():

    # The main method responsible for handling the requests
    try:
        # storing  sender number , profile name , user input
        global Sender_number
        Sender_number = request.values.get('WaId')
        ProfileName = request.values.get("ProfileName")
        User_input = request.values.get('Body')
        message, tag = Check_if_firstmessage(User_input)
        DBconnection.InsertMessage(Sender_number, ProfileName, tag, User_input)
        if tag == "studyplan":
            Studyplan(message)
            return ""
        if tag == "faculty_office" and message == "":
            Faculty_office(message,User_input)
            return ""
        if tag == "section_info" and message == "":
            Section_info(message,User_input)
            return ""
        if tag == "impotent_dates":
            Important_dates(message)
            return ""
        if tag == "academic_calender":
            Academic_calender(message)
            return ""
        if tag == "final_exam":
            Finalexam(message)
            return ""
        if tag == "mid_exam":
            Midexam(message)
            return ""
        Send(None, message)
    except FirebaseError:
        print("Cant communicate with the database server")
    except TwilioRestException as e:
        print("Status code: ", e.status, "Message: ", e.msg, "Details: ", e.details)

    return ""


def Check_if_firstmessage(User_input):
    # Define a method for checking if the incoming message was the first one
    global First_message
    if First_message is True:
        # if it was the first message, the make the flag false and send
        # the following message with the services available
        message = "مرحبا بك في خدمة الرد الالي للشؤون التعليمة في كلية الحقوق (النسخة التجربية)\n" + menu
        tag = "greeting"

        First_message = False

    else:
        # if no then check if it contains number the extract it to use it for selecting from the menu
        # if it doesn't have numbers, it will return None
        # after that the result will be given to HandelInput()

        if "عرض بيانات" in User_input:
            return "","faculty_office"
        if "عرض شعبة" in User_input:
            return "","section_info"

        extracted_number = extract_number(User_input)

        message, tag = HandelInput(extracted_number, User_input)
    return message, tag


def HandelInput(extracted_number, User_input):
    # Define a method for dealing with text and numbers
    tag = "no_tag"
    # if the text was not known by the model, then the message will be the following
    message = "عذرا لم استطع فهم استفسارك،ولكن استطيع خدمتك حالياً في المواضيع الاتية:" + menu
    message = re.sub("الخدمات التي استطيع خدمتك فيها حاليا:", "", message)

    if extracted_number is None:
        # if extracted_number is None (text) then strip the unwanted chars
        User_input = strip_unwanted_chars(User_input)
        # change user input to bag of words so the model can understand it
        Input_to_bag_of_words = [Model_data.bag_of_words(User_input)]
        # predict on Input_to_bag_of_words and then take the first index as the results
        results = Model_data.Model.predict(Input_to_bag_of_words)[0]
        # take the maximum value in results
        results_index = numpy.argmax(results)
        print(results[results_index])
        if results[results_index] > 0.80:
            # if that maximum value is more the 0.80 then take the tag given the index
            tag = Model_data.Dataset.Tags[results_index]
            # select a random message from a list of responses
            message = random.choice(Model_data.Dataset.Response.get(tag))
            # if the tag was "greeting" then append the response with the menu
            if tag == "greeting":
                message = message + " " + menu

    elif 8 >= extracted_number >= 1:
        # if it was not text and a number from 1 to 8, then get the tag from "Index" dictionary
        tag = Model_data.Dataset.Index.get(extracted_number)
        # select a random message from a list of responses
        message = random.choice(Model_data.Dataset.Response.get(tag))
    return message, tag


def Studyplan(message):
    # define a method that is responsible for getting the study plan to form the database and then send it to the user
    try:
        Studyplan = DBconnection.GetStudyplan()
        Send(None, message)
        Send(Studyplan, "الخطة الدراسية لكلية الحقوق")
    except firebase_admin.exceptions.NotFoundError:
        Send(None, "عذرا لم استطع ايجاد الخطة الدراسية")

def Faculty_office(message,User_input):

    try:
        facultyOffice = DBconnection.GetFacultyMembersOfficeHours(User_input)

        Send(None, facultyOffice)
    except firebase_admin.exceptions.NotFoundError:
        return ""

def Section_info(message,User_input):

    try:
        sectionInfo = DBconnection.Get_SectionInfo(User_input)
        print(sectionInfo)
        Send(None, sectionInfo)
    except firebase_admin.exceptions.NotFoundError:
        return ""

def Academic_calender(message):
    # define a method that is responsible for getting
    # the academic calendar form the database and then send it to the user
    try:
        calender = DBconnection.GetAcademic_calender()
        Send(None, message)
        Send(calender, "التقويم الاكاديمي للفصل الحالي")
    except firebase_admin.exceptions.NotFoundError:
        Send(None, "عذرا لم استطع ايجاد التقويم الاكاديمي")


def Important_dates(message):
    # define a method that is responsible for getting
    # the important dates to form the database and then send it to the user
    try:
        dates = DBconnection.Get_Importantdates()
        Send(None, message)
        Send(None, dates)
    except firebase_admin.exceptions.NotFoundError:
        Send(None, "عذرا لم يتم العثور على مواعيد مهمة")


def Finalexam(message):
    # define a method that is responsible for getting
    # the final exam schedule to form the database and then send it to the user
    try:
        finalexam = DBconnection.Get_finalexam()
        Send(None, message)
        Send(finalexam, "جدول الاختبارات النهائية للفصل الحالي")
    except firebase_admin.exceptions.NotFoundError:
        Send(None, "عذرا لم يتم العثور على جدول الاختبارات النهائية")


def Midexam(message):
    # define a method that is responsible for getting
    # the midterm exam schedule to form the database and then send it to the user
    try:
        midexam = DBconnection.Get_midexam()
        Send(None, message)
        Send(midexam, "جدول الاختبارات النصفية للفصل الحالي")
    except firebase_admin.exceptions.NotFoundError:
        Send(None, "عذرا لم يتم العثور على جدول الاختبارات النصفية")


def Send(Media_url, Message):
    # define a method that is responsible for sending the message to user by taking
    # the number, message, and url if applicable
    client.messages.create(
        to='whatsapp:+' + Sender_number,
        from_='whatsapp:+17782008610',
        body=Message
        , media_url=Media_url)


# run only if it is in a Python interpreter
if __name__ == "__main__":
    app.run(debug=True, threaded=True)
