import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from hijridate import Hijri, Gregorian
from selenium.webdriver.support.select import Select


class ScraperTestCase(unittest.TestCase):
    def setUp(self):
        # Run the browser in headless mode
        options = Options()
        options.add_argument("--headless=new")

        # Initialize a browser
        self.driver = webdriver.Chrome(options=options)

        # URL to scrape
        self.url = "https://lpcal.kau.edu.sa/AdmissionCal.aspx"

    def tearDown(self):
        # Close the browser after each test
        self.driver.quit()

    def test_Scraping_ImportantDates(self):
        # Load the page
        self.driver.get(self.url)

        # Switch to "الانتظام" tab
        tab = self.driver.find_element(By.XPATH, '//a[contains(text(), "الانتظام")]').click()

        # Get the semester dropdown element
        semester_dropdown = self.driver.find_element(By.ID, "DropDownList_term")
        select_semester = Select(semester_dropdown)

        # Select the last index (usually the option for the current semester)
        last_index = len(select_semester.options) - 1
        select_semester.select_by_index(last_index)

        # Scrape the table data for important dates
        events = self.driver.find_elements(By.XPATH, "//table[@class='mGrid']//td[1]")
        dates_from = self.driver.find_elements(By.XPATH, "//table[@class='mGrid']//td[2]")
        dates_to = self.driver.find_elements(By.XPATH, "//table[@class='mGrid']//td[3]")

        # Check if the number of events, dates_from, and dates_to are the same
        self.assertEqual(len(events), len(dates_from))
        self.assertEqual(len(events), len(dates_to))

        # Loop through the table data and scrape important dates
        for i in range(len(events)):
            event = events[i].text
            date_from = dates_from[i].text
            date_to = dates_to[i].text

            # Verify that the scraped data is not empty
            self.assertNotEqual(event, "")
            self.assertNotEqual(date_from, "")
            self.assertNotEqual(date_to, "")



if __name__ == '__main__':
    unittest.main()
