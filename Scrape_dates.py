from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from hijridate import Hijri, Gregorian
import json

from DatabaseConnection import DatabaseConnection

# URL to scrape
url = "https://lpcal.kau.edu.sa/AdmissionCal.aspx"

options = Options()
options.add_argument("--headless=new")
DBconnection=DatabaseConnection.GetDBConnection()
DBconnection.Delete_Importantdate()
# Initialize a browser
driver = webdriver.Chrome(options=options)

# Load the page
driver.get(url)

# Switch to "الانتظام" tab
tab = driver.find_element(By.XPATH, '//a[contains(text(), "الانتظام")]').click()

semester_dropdown = driver.find_element(By.ID, "DropDownList_term")
select_semester = Select(semester_dropdown)

# select last index (usually the option for current semester)
last_index = len(select_semester.options) - 1
select_semester.select_by_index(last_index)

events = driver.find_elements(By.XPATH, "//table[@class='mGrid']//td[1]")
dates_from = driver.find_elements(By.XPATH, "//table[@class='mGrid']//td[2]")
dates_to = driver.find_elements(By.XPATH, "//table[@class='mGrid']//td[3]")
statuses = driver.find_elements(By.XPATH, "//table[@class='mGrid']//td[4]/img")

important_dates = {

}

for i in range(len(events)):
    event = events[i].text
    date_from = dates_from[i].text
    date_from_split = dates_from[i].text.split('/')


    date_from_gregorian = Hijri(int(date_from_split[2]), int(date_from_split[1]), int(date_from_split[0])).to_gregorian()
    date_from_gregorian = date_from_gregorian.dmyformat()
    date_from_gregorian = json.dumps(date_from_gregorian, default=str)

    date_to = dates_to[i].text
    date_to_split = dates_to[i].text.split('/')

    date_to_gregorian = Hijri(int(date_to_split[2]), int(date_to_split[1]), int(date_to_split[0])).to_gregorian()
    date_to_gregorian = date_to_gregorian.dmyformat()
    date_to_gregorian = json.dumps(date_to_gregorian, default=str)

    status = statuses[i].get_attribute('src')

    if "recent" in status:
        status = "حاليا"
    elif "finish" in status:
        status = "انتهى"
    elif "soon" in status:
        status = "قريبا"
    else:
        status = "غير معروف"

    info = {
        'الحدث': event,
        'من تاريخ (هجري)': date_from,
        'من تاريخ (ميلادي)': date_from_gregorian.replace('\"', ''),
        'إلى تاريخ (هجري)': date_to,
        'إلى تاريخ (ميلادي)': date_to_gregorian.replace('\"', ''),
        'الحالة': status
    }

    DBconnection.Insert_Importantdate(info)

print("Data was inserted in the database successfully.")