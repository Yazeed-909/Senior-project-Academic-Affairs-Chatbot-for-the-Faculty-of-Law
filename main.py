import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# function to click a button in a page
def click_submit_button(driver):
    submit = driver.find_element_by_xpath("//input[@type='submit']")
    submit.click()


# Define the URL you want to scrape
url = "https://odusplus-ss.kau.edu.sa/PROD/xwckctlg.p_disp_dyn_ctlg"


# Set the chrome options for running the browser in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")

# Initialize a browser with the headless option
driver = webdriver.Chrome("C:\\Users\\Wael\\Chromedriver\\chromedriver.exe", options=chrome_options)

# Load the page
driver.get(url)

# Calc. execution time for benchmark later
start_time = time.time()

# List of Semesters
semesters = driver.find_elements_by_tag_name('option')

print('Chosen Semester: '+ semesters[2].text)

# Choose the current semester
# Might change it later to loop through semesters and find current semester
semesters[2].click()

# Click on the Submit button
click_submit_button(driver)

# Find the courses dropdown
courses_dropdown = driver.find_elements_by_tag_name('option')

# Filter Masters/PhD Courses
crse_id_from = driver.find_element_by_id('crse_id_from')
crse_id_from.send_keys('100')
crse_id_to = driver.find_element_by_id('crse_id_to')
crse_id_to.send_keys('499')


for courseCode in range(len(courses_dropdown)):

            # Select the course from the dropdown
            courses_dropdown[courseCode].click()
            selected_course_index = courseCode

            print('Chosen Course Code: ' + courses_dropdown[courseCode].text)

            # Click on the Submit button
            click_submit_button(driver)

            courses = driver.find_elements_by_class_name('default')

            for i in range(len(courses)):
                course = courses[i]
                course_details = course.text.split('\n')
                course_title = course_details[0]
                credit_hours = course_details[1]
                section_btn = course.find_element_by_class_name('pldefault')
                # will store in a list later
                print('#' + str(i) + ' Course name: ' + course_title + '\n' + 'Credit hours: ' + credit_hours)

                if section_btn.text == 'عرض الشعب':
                    section_btn.click()

                    sections = driver.find_elements_by_class_name('datadisplaytable')
                    # Check if the sections table is available on the page
                    if len(sections) > 0:
                        print(sections[0].text + '\n')
                    else:
                        print('No sections available\n')

                    driver.back()
                else:
                    print(section_btn.text + '\n')

                # Find the course elements again after going back to the previous page
                courses = driver.find_elements_by_class_name('default')

            driver.back()


            # Refresh the courses dropdown after going back to the previous page
            courses_dropdown = driver.find_elements_by_tag_name('option')
            courses_dropdown[selected_course_index].click()

end_time = time.time()
execution_time = end_time - start_time

execution_time_minutes = int(execution_time // 60)
execution_time_seconds = int(execution_time % 60)

print("Execution time: {} minutes {} seconds".format(execution_time_minutes, execution_time_seconds))
# course_title = []
# course_details = []
# section_status = []
# crn = []
# section_num = []
# section_type = []
# section_time = []
# section_days = []
# section_bld = []
# section_room = []
# section_instr = []