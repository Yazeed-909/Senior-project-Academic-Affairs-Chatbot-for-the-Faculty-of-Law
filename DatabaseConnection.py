import json
import os
from datetime import datetime, date
from string import Template

import firebase_admin
from firebase_admin import credentials, db, exceptions
from firebase_admin.auth import CertificateFetchError

Database_certificate_path = os.environ.get("certificate_path")
Database_url = os.environ.get("database_url")
if Database_certificate_path is None or Database_url is None:
    raise EnvironmentError("environment value not found ")


class DatabaseConnection(object):
    __instance = None
    __DB_connection = None

    @staticmethod
    def GetDBConnection():
        # define a method to return the connection if it was one if not, then it creates one
        # the method purpose is to make sure no more than one connection to the database
        if DatabaseConnection.__instance is None:
            DatabaseConnection()

        return DatabaseConnection.__instance

    def __init__(self):

        if DatabaseConnection.__instance is not None:
            raise Exception("already have an object from class Database_connection")
        else:
            try:
                # load the certificate path and url from environment variables and initialize the app
                cred = credentials.Certificate(Database_certificate_path)
                firebase_admin.initialize_app(cred, {
                    "databaseURL": Database_url})
                self.__DB_connection = db.reference("/")
                DatabaseConnection.__instance = self
            except ValueError:
                print("DatabaseURL is invalid or is already in use ")
            except CertificateFetchError:
                print("Database certificate is invalid ")

            except EnvironmentError as e:
                print(e)
                exit(1)

    def InsertMessage(self, Phonenumber, Username, Tag, Message):

        try:
            # this method stores the current time, tag, message , username , phone-number as a log in the database
            Current_date = datetime.now().replace(microsecond=0)
            Current_date = json.dumps(Current_date, default=str)

            self.__DB_connection.child("Messages").push({"from": Phonenumber
                                                            , "Username": Username
                                                            , "Message": Message
                                                            , "tag": Tag
                                                            , "time": Current_date})
        except ValueError:
            print("Value is defined as None")
        except TypeError:
            print("Object is not JSON type")

    def GetStudyplan(self):
        # method to get the studyplan from the database
        Studyplan = self.__DB_connection.child("Studyplan").get()
        if Studyplan is None:
            raise firebase_admin.exceptions.NotFoundError("No record was found")

        return Studyplan

    def GetAcademic_calender(self):
        # method to get the academic calendar from the database
        Calender = self.__DB_connection.child("Academic_calender").get()
        if Calender is None:
            raise firebase_admin.exceptions.NotFoundError("No record was found")

        return Calender

    def Delete_Importantdate(self):
        # method to delete important dates from the database
        self.__DB_connection.child("Dates").delete()

    def Insert_Importantdate(self, Importantdate):
        # method to insert the Important date to the database after scraping
        try:
            self.__DB_connection.child("Dates").push(Importantdate)
        except ValueError:
            print("Value is defined as None")
        except TypeError:
            print("Object is not JSON type")

    def Get_Importantdates(self):
        # method to get important dates from the database
        Dates = self.__DB_connection.child("Dates").get()
        if Dates is None:
            raise firebase_admin.exceptions.NotFoundError("No record was found")
        Message = ""
        for key in Dates.keys():
            # template to insert into
            Event = "\n--------------------------------------\nالحدث :${event}\nهجري\nمن  ${start_gregorian} الى ——> " \
                    "${end_gregorian} \n ميلادي\nمن ${start} الى ——> ${end} \nالحالة : ${status}"
            # status after processing from the method
            status = self.__Check_if_ongoing(Dates[key]["إلى تاريخ (ميلادي)"], Dates[key]["من تاريخ (ميلادي)"])
            # set the values from the dictionary to the ones in a database
            replacement_text = {
                "event": Dates[key]["الحدث"],
                "start": Dates[key]["من تاريخ (ميلادي)"],
                "end": Dates[key]["إلى تاريخ (ميلادي)"],
                "start_gregorian": Dates[key]["من تاريخ (هجري)"],
                "end_gregorian": Dates[key]["إلى تاريخ (هجري)"],
                "status": status
            }
            # insert the values in the template and return the message
            template = Template(Event)
            Event = template.substitute(replacement_text)
            Message += Event
        return Message

    def Get_finalexam(self):
        # method to get the final-exam from the database
        Finalexam_file = self.__DB_connection.child("Finalexam").get()
        if Finalexam_file is None:
            raise firebase_admin.exceptions.NotFoundError("No record was found")
        return Finalexam_file

    def __Check_if_ongoing(self, Diedline_date, Start_date):
        # method to get check if the event is finished, ongoing, or soon
        # it does that by subtracting today date with the date from the database
        Diedline_date = datetime.strptime(Diedline_date, "%d/%m/%Y")
        Start_date = datetime.strptime(Start_date, "%d/%m/%Y")
        Today_date = date.today()
        Today_date = datetime.combine(Today_date, datetime.min.time())

        status = "انتهى"
        if Diedline_date >= Today_date:
            status = "حاليا"
        if Start_date > Today_date:
            status = "قريبا"
        return status

    def Get_midexam(self):
        # method to get the midterm-exam from the database
        midexam_file = self.__DB_connection.child("Midexam").get()
        if midexam_file == None:
            raise firebase_admin.exceptions.NotFoundError("No record was found")
        return midexam_file
