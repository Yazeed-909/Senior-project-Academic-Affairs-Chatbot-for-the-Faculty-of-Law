import json
import os
import re
from datetime import datetime, date
from string import Template

import firebase_admin
from firebase_admin import credentials, db, exceptions
from firebase_admin.auth import CertificateFetchError

Database_certificate_path = os.environ.get("certificate_path")
Database_url = os.environ.get("database_url")
if Database_certificate_path is None or Database_url is None:
    raise EnvironmentError("environment value not found")


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
        Studyplan = self.__DB_connection.child("Links").child("Studyplan").get()
        if Studyplan is None:
            raise firebase_admin.exceptions.NotFoundError("No record was found")

        return Studyplan

    def GetAcademic_calender(self):
        # method to get the academic calendar from the database
        Calender = self.__DB_connection.child("Links").child("Academic_calender").get()
        if Calender is None:
            raise firebase_admin.exceptions.NotFoundError("No record was found")

        return Calender

    def GetFacultyMembersOfficeHours(self, command_input):
        faculty_office = self.__DB_connection.child("FacultyMembersOfficeHours").get()
        if faculty_office is None:
            raise firebase_admin.exceptions.NotFoundError("No record was found")

        # Initialize an empty string to hold the final message
        Message = ""

        # Define a list of prefixes commonly used
        prefixes = ["أ.", "د.", "دكتور", "د ", "الدكتور"]

        # If the command doesn't start with "عرض بيانات", return statement
        if not command_input.startswith("عرض بيانات"):
            return "يجب كتابة الأمر 'عرض بيانات' قبل كتابة أسم الدكتور."

        # Command starts with "عرض بيانات"!
        # Remove "عرض بيانات" text from the input
        name = command_input.replace("عرض بيانات", "").strip()

        # Remove any title prefixes from the name
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name.replace(prefix, "").strip()

        # If the name is empty, return statement
        if not name:
            return "تأكد من كتابة الأسم بالصيغة الصحيحة.\nيرجى الإلتزام بالتنسيق الآتي \"عرض بيانات اسم عضو هيئة التدريس\"\n\nمثال: عرض بيانات د. خالد الغامدي"

        # Initialize a boolean flag to indicate if the name was found
        found = False

        # Loop through all the data in the "FacultyMembersOfficeHours" db
        for info in faculty_office:
            # If the name is found in the data, add all the information for that faculty member to the message
            clean_name = info["الأسم"]

            # Remove any title prefixes from clean_name
            for prefix in prefixes:
                if clean_name.startswith(prefix):
                    clean_name = clean_name.replace(prefix, "").strip()

            if clean_name.startswith(name):
                for key, value in info.items():
                    Message += f"{key}: {value if value else 'لا يوجد'}\n"
                # Set the flag to true to indicate that the name was found
                found = True
                # break


        # If the name was not found, return statement
        if not found:
            return "الأسم غير موجود\n\n" +"الأسماء المتوفرة بياناتهم: \n "+ self.getAllFacultyMembersNames()

        # Return the final message
        return Message

    def getAllFacultyMembersNames(self):
        faculty_office = self.__DB_connection.child("FacultyMembersOfficeHours").get()
        if faculty_office is None:
            raise firebase_admin.exceptions.NotFoundError("No record was found")
            return None

        # Initialize an empty string to hold the final message
        Message = ""
        for info in faculty_office:
            Message += info["الأسم"] + "\n"

        return Message

    def Delete_SectionInfo(self):
        self.__DB_connection.child("Courses").delete()

    def Insert_SectionInfo(self, SectionInfo):
        self.__DB_connection.child("Courses").set(SectionInfo)

    def Get_SectionInfo(self, command_input):
        # Get the courses data from the database
        Courses = self.__DB_connection.child("Courses").get()

        # If no courses data is found, raise a NotFoundError
        if Courses is None:
            raise firebase_admin.exceptions.NotFoundError("No record was found")

        # Initialize an empty string to hold the final message
        Message = ""

        # Check if the command starts with "عرض شعبة"
        # If not then return statement. Else, proceed with the code
        if not command_input.startswith("عرض شعبة"):
            return "الأمر غير صالح.\n"

        # Command starts with "عرض شعبة"!
        # Split the command to parts |course code|-|course number|-|section number|
        command_parts = command_input.replace("عرض شعبة", "").strip().split('-')

        # Check if command is in correct format (contains at least |course code|-|course number|)
        if len(command_parts) < 2:
            return "تأكد من أنك أدخلت رمز ورقم المقرر.\n"

        # Combine the |course code| and |course number| into a one string
        course_input = command_parts[0].upper() + " " + command_parts[1]
        section_input = command_parts[2].upper() if len(command_parts) >= 3 else ""

        # Get the details for the specified course from the Courses db
        course_details = Courses.get(course_input)
        # If the specified course is not found in the Courses db, return statement. Else, proceed with the code
        if not course_details:
            return "المقرر الذي أدخلته غير موجود.\n"

        Message += f"اسم المقرر: {course_details['CourseName']}\n"
        Message += f"عدد الساعات الدراسية: {course_details['CreditHours']}\n\n"

        # Get the data of the sections of the specified course
        section_data = course_details.get("Section(s)")

        # If there were no sections found in db for the specified course, return statement. Else, proceed with the code
        if not section_data:
            return Message + "لا توجد شعب متاحة لهذا المقرر في الفصل الحالي.\n"

        # If no section number is specified in Message input, list all available sections for the course
        if not section_input:
            Message += "الشعب المتاحة:\n"
            for section_key, section_value in section_data.items():
                Message += section_value["الشعبة"] + "\n"
            return Message

        # Section number is specified in Message input!
        # Find the section with the specified "الشعبة" value
        found_section = None
        for section_key, section_value in section_data.items():
            if section_value["الشعبة"] == section_input:
                found_section = section_value
                section_crn = section_key
                break

        # If the specified section is not found, return statement. Else, proceed with the code
        if not found_section:
            return Message + "الشعبة غير موجودة.\n"

        # Section is found!
        section_num = found_section["الشعبة"]
        section_time = found_section["الوقت"]
        section_day = found_section["الأيام"]
        section_bld = found_section["المبنى"]
        section_room = found_section["الغرفة"]
        section_instr = found_section["الاساتذة"]

        Message += f"الرقم المرجعي: {section_crn}\n"
        Message += f"الشعبة: {section_num}\n"
        Message += f"المبنى: {section_bld}\n"
        Message += f"الغرفة: {section_room}\n"
        Message += "\nالمحاضرات:\n"
        Message += f"الأيام: {section_day}\n"
        Message += f"الوقت: {section_time}\n"
        Message += f"الأساتذة: {section_instr}\n\n"

        # Get the data for any other lectures for the specified section
        other_lectures = found_section.get("محاضرات أخرى")

        # If no other lectures are found, return statement. Else, proceed with the code
        if not other_lectures:
            return Message

        # Found other lectures!
        # Add the data for each additional lecture to the output string
        for lecture in other_lectures:
            lecture_day = lecture["الأيام"]
            lecture_time = lecture["الوقت"]
            lecture_instr = lecture["الاساتذة"]

            Message += f"الأيام: {lecture_day}\n"
            Message += f"الوقت: {lecture_time}\n"
            Message += f"الاساتذة: {lecture_instr}\n\n"

        # Return the final message
        return Message

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
        Finalexam_file = self.__DB_connection.child("Links").child("Finalexam").get()
        if Finalexam_file is None:
            raise firebase_admin.exceptions.NotFoundError("No record was found")
        return Finalexam_file

    def __Check_if_ongoing(self, Deadline_date, Start_date):
        # method to get check if the event is finished, ongoing, or soon
        # it does that by subtracting today date with the date from the database
        Deadline_date = datetime.strptime(Deadline_date, "%d/%m/%Y")
        Start_date = datetime.strptime(Start_date, "%d/%m/%Y")
        Today_date = date.today()
        Today_date = datetime.combine(Today_date, datetime.min.time())

        status = "انتهى"
        if Deadline_date >= Today_date:
            status = "حاليا"
        if Start_date > Today_date:
            status = "قريبا"
        return status

    def Get_midexam(self):
        # method to get the midterm-exam from the database
        midexam_file = self.__DB_connection.child("Links").child("Midexam").get()
        if midexam_file == None:
            raise firebase_admin.exceptions.NotFoundError("No record was found")
        return midexam_file
