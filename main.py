import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import json

# function to click a button in a page
def click_submit_button(driver):
    submit = driver.find_element(By.XPATH, "//input[@type='submit']")
    submit.click()
    # Wait for the page to load
    driver.implicitly_wait(10)

# Record start time of execution
start_of_exec_time = time.time()

# URL to scrape
url = "https://odusplus-ss.kau.edu.sa/PROD/xwckctlg.p_disp_dyn_ctlg"

# Initialize a browser
driver = webdriver.Chrome()

# Load the page
driver.get(url)

# Get the semester dropdown element and select the second option
semester_dropdown = driver.find_element(By.ID, "term_input_id")
select_semester = Select(semester_dropdown).select_by_index(2)

# Click on the Submit button
click_submit_button(driver)

# Get the course dropdown element and select multiple courses by their values
course_dropdown = driver.find_element(By.ID, "subj_id")
course_codes = ['ARAB', 'BL', 'CPIT', 'ELIA', 'IS', 'ISLS', 'MATH', 'STAT']
select_course = Select(course_dropdown)

for code in course_codes:
    select_course.select_by_value(code)

# Filter Diploma/Masters/PhD Courses by setting course ID range
crse_id_from = driver.find_element(By.ID, "crse_id_from")
crse_id_from.send_keys('100')
crse_id_to = driver.find_element(By.ID, "crse_id_to")
crse_id_to.send_keys('499')

# Click on the Submit button
click_submit_button(driver)

# Get the course titles for each course
course_titles = driver.find_elements(By.XPATH, "//table[@id='COREQ']//td[@class='title']")

# Get the course table element
course_table = driver.find_elements(By.XPATH, "//td[@class='default']")


# Create a dictionary to store Courses and their Sections information
section_info = {
    'Courses': {}
}

# Loop through the course table and extract Courses information
for i in range(len(course_table)):
    # Extract course title, course name, credit hours, and section availability
    course_info = course_table[i].text.split("\n")

    # Ex. "ARAB 101"
    course_title = course_info[0].split(" - ")[0]
    # Ex. "ARAB 101 - اللغة العربية -1-"
    course_name = course_info[0]
    # Ex. 4
    credit_hours = course_info[1][-6:-4].strip()
    # Ex. if the section is available it will return "عرض الشعب" else "لاتوجد شعب متاحة في الفصل المحدد"
    section_available = course_info[-1]

    # Create a key with the course_title in the section_info dictionary if it doesn't exist
    if course_title not in section_info['Courses']:
        section_info['Courses'][course_title] = {
            'CourseName': course_name,
            'CreditHours': credit_hours,
            'Section(s)': []
        }

    # Click on the "عرض الشعب" button to see available sections for the course
    view_section = course_table[i].find_elements(By.XPATH, "//td[@class='pldefault']")[i]

    if "عرض الشعب" in section_available:
        view_section.click()
        # Record start time for scraping the course
        start_time = time.time()

        # Get all the section information from the table
        crns = driver.find_elements(By.XPATH, "//td[@class='dddefault'][1]") #الرقم المرجعي
        section_nums = driver.find_elements(By.XPATH, "//td[@class='dddefault'][2]") # الشعبة
        section_types = driver.find_elements(By.XPATH, "//td[@class='dddefault'][3]") # نوع الجدول
        section_times = driver.find_elements(By.XPATH, "//td[@class='dddefault'][4]") # الوقت
        section_days = driver.find_elements(By.XPATH, "//td[@class='dddefault'][5]") # الأيام
        section_blds = driver.find_elements(By.XPATH, "//td[@class='dddefault'][6]") # المبنى
        section_rooms = driver.find_elements(By.XPATH, "//td[@class='dddefault'][7]") # الغرفة
        section_instrs = driver.find_elements(By.XPATH, "//td[@class='dddefault'][8]") # الاساتذة

        print("Scraping", course_title, "sections now...")

        # Loop through all the sections and extract their information
        for i in range(len(crns)):

            crn = crns[i].text
            section_num = section_nums[i].text
            section_type = section_types[i].text
            section_time = section_times[i].text
            section_day = section_days[i].text
            section_bld = section_blds[i].text
            section_room = section_rooms[i].text
            section_instr = section_instrs[i].text.replace('(P)', '').strip()

            # Create a dictionary to store the section information
            section = {
                # 'اسم المقرر': course_name,
                'الرقم المرجعي': crn,
                'الشعبة': section_num,
                'نوع الجدول': section_type,
                'الوقت': section_time,
                'الأيام': section_day,
                'المبنى': section_bld,
                'الغرفة': section_room,
                'الاساتذة': section_instr
            }

            # Add the section information to the section_info dictionary
            section_info["Courses"][course_title]["Section(s)"].append(section)

        # Record end time of section scraping for this course
        end_time = time.time()
        # Calculate the execution time for scraping the sections of this course
        execution_time = end_time - start_time

        execution_time_minutes = int(execution_time // 60)
        execution_time_seconds = int(execution_time % 60)
        execution_time_milliseconds = int((execution_time % 1) * 1000)

        # Print the execution time for scraping this course
        print(f"Time it took to scrape {course_title}: {execution_time_minutes} minutes {execution_time_seconds} seconds {execution_time_milliseconds} milliseconds\n")

        # Go back to the previous page that contains other courses information
        driver.back()

        # selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: stale element not found. Couldn't find course_table. To fix it:
        # Refresh the course table element to avoid stale element reference error
        course_table = driver.find_elements(By.XPATH, "//td[@class='default']")
    else:
        # If there are no available sections for this course, store the value of section_available which is "لاتوجد شعب متاحة في الفصل المحدد"
        section_info["Courses"][course_title]["Section(s)"].append(section_available)


# Convert section_info to JSON
json_data = json.dumps(section_info, indent=4, ensure_ascii=False)

# Write JSON data to a file
with open('section_info.json', 'w', encoding='utf-8') as file:
    file.write(json_data)

print("JSON file created successfully.")

# Record end time of execution
end_of_exec_time = time.time()

# Calculate the total execution time
full_execution_time = end_of_exec_time - start_of_exec_time

full_execution_time_minutes = int(full_execution_time // 60)
full_execution_time_seconds = int(full_execution_time % 60)
execution_time_milliseconds = int((full_execution_time % 1) * 1000)

# Print the total execution time
print(f"Execution time: {full_execution_time_minutes} minutes {full_execution_time_seconds} seconds {execution_time_milliseconds} milliseconds")