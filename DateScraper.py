from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from hijridate import Hijri, Gregorian
from DatabaseConnection import DatabaseConnection


class DateScraper:
    def __init__(self):
        try:
            # Run the browser in headless mode
            self.options = Options()
            self.options.add_argument("--headless=new")

            # Initialize a browser
            self.driver = webdriver.Chrome(options=self.options)
        except WebDriverException:
            print("Couldn't find ChromeDriver!")
            exit(1)

        # Create a dictionary to store every date information
        self.info = {}

    def save_to_db(self):
        # Establish a database connection
        DBconnection = DatabaseConnection.GetDBConnection()

        # Insert data to the database
        DBconnection.Insert_SectionInfo(self.info)

    def scrape_important_dates(self):
        # URL to scrape
        url = "https://lpcal.kau.edu.sa/AdmissionCal.aspx"

        try:
            # Load the page
            self.driver.get(url)

            # Switch to "الانتظام" tab
            tab = self.driver.find_element(By.XPATH, '//a[contains(text(), "الانتظام")]').click()

            # Get the semester dropdown element
            semester_dropdown = self.driver.find_element(By.ID, "DropDownList_term")
            select_semester = Select(semester_dropdown)

            # select last index (usually the option for current semester)
            last_index = len(select_semester.options) - 1
            select_semester.select_by_index(last_index)

            # Scrape the table data for important dates
            events = self.driver.find_elements(By.XPATH, "//table[@class='mGrid']//td[1]")
            dates_from = self.driver.find_elements(By.XPATH, "//table[@class='mGrid']//td[2]")
            dates_to = self.driver.find_elements(By.XPATH, "//table[@class='mGrid']//td[3]")

            # Loop through the table data and scrape important dates
            for i in range(len(events)):
                event = events[i].text
                date_from = dates_from[i].text
                date_from_split = dates_from[i].text.split('/')

                # Convert the "from" date from Hijri to Gregorian and format it as a string
                date_from_gregorian = Hijri(int(date_from_split[2]), int(date_from_split[1]),
                                            int(date_from_split[0])).to_gregorian()
                date_from_gregorian = date_from_gregorian.dmyformat()

                # Convert the "to" date from Hijri to Gregorian and format it as a string
                date_to = dates_to[i].text
                date_to_split = dates_to[i].text.split('/')

                date_to_gregorian = Hijri(int(date_to_split[2]), int(date_to_split[1]),
                                          int(date_to_split[0])).to_gregorian()
                date_to_gregorian = date_to_gregorian.dmyformat()

                # Store every date information
                info = {
                    'الحدث': event,
                    'من تاريخ (هجري)': date_from,
                    'من تاريخ (ميلادي)': date_from_gregorian.replace('\"', ''),
                    'إلى تاريخ (هجري)': date_to,
                    'إلى تاريخ (ميلادي)': date_to_gregorian.replace('\"', '')
                }

                # Insert data to database
                self.save_to_db()

            print("Important Dates Data was inserted in the database successfully!")
        except NoSuchElementException:
            print("Couldn't find the element")


if __name__ == '__main__':
    DateScraper().scrape_important_dates()
