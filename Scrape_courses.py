import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from DatabaseConnection import DatabaseConnection

# Record start time of execution
start_of_exec_time = time.time()

# URL to scrape
url = 'https://odusplus-ss.kau.edu.sa/PROD/xwckcapp.P_ProcProgMajrPara?ctlg_term=202330&levl_code=UG&camp_code=MCB&coll_code=LA&std_att=REGL&dept_code=0000&majr_conc=LAW%7E%25&program=BS-LAW-LA&submit_btn=تنفيــذ'

# Establish a db connection
DBconnection = DatabaseConnection.GetDBConnection()

# Delete previously stored courses sections to be replaced with new one
DBconnection.Delete_SectionInfo()

# Run the browser in headless mode
options = Options()
options.add_argument("--headless=new")

# Initialize a browser
driver = webdriver.Chrome(options=options)

# Load the page
driver.get(url)

# Find all the course codes, numbers, names, and credit hours on the page
course_codes = driver.find_elements(By.XPATH, "//table[@id='summary_tab']//td[@class='default'][2]")
course_nums = driver.find_elements(By.XPATH, "//table[@id='summary_tab']//td[@class='default'][3]")
course_names = driver.find_elements(By.XPATH, "//table[@id='summary_tab']//td[@class='default'][4]")
credit_hours = driver.find_elements(By.XPATH, "//table[@id='summary_tab']//td[@class='default'][5]")
# Find "الشعب" which is a clickable text the leads to the sections page for each course on the page
view_section = driver.find_elements(By.XPATH, "//table[@id='summary_tab']//td[@class='default'][1]//a[text()='الشعب']")

# Create a dictionary to store Courses and their Sections information
section_info = {}

# Loop to extract Courses information and their sections
for i in range(len(course_codes)):
    # Create the course title by concatenating the course code and number. Ex. ISLS 101
    course_title = course_codes[i].text + " " + course_nums[i].text

    # Create a key with the course_title in the section_info dictionary if it doesn't exist
    if course_title not in section_info:
        section_info[course_title] = {
            'CourseName': course_names[i].text,
            'CreditHours': credit_hours[i].text,
            'Section(s)': {}
        }

    print("Scraping", course_title, "sections now...")

    # Record start time for scraping the course
    start_time = time.time()

    # Click on "الشعب" text to see available sections for the course
    view_section[i].click()

    crns = driver.find_elements(By.XPATH, "//td[@class='dddefault'][1]")  # الرقم المرجعي
    section_nums = driver.find_elements(By.XPATH, "//td[@class='dddefault'][2]")  # الشعبة
    section_types = driver.find_elements(By.XPATH, "//td[@class='dddefault'][3]")  # نوع الجدول
    section_times = driver.find_elements(By.XPATH, "//td[@class='dddefault'][4]")  # الوقت
    section_days = driver.find_elements(By.XPATH, "//td[@class='dddefault'][5]")  # الأيام
    section_blds = driver.find_elements(By.XPATH, "//td[@class='dddefault'][6]")  # المبنى
    section_rooms = driver.find_elements(By.XPATH, "//td[@class='dddefault'][7]")  # الغرفة
    section_instrs = driver.find_elements(By.XPATH, "//td[@class='dddefault'][8]")  # الاساتذة
    section_links = driver.find_elements(By.XPATH, "//td[@class='dddefault'][9]/a")  # تفاصيل (this contains the url of the section and is used to merge lectures of same CRN)

    # Loop through all the sections and extract their information
    for i in range(len(crns)):
        crn = crns[i].text
        section_num = section_nums[i].text
        section_type = section_types[i].text
        section_time = section_times[i].text.replace("AM", "ص").replace("PM", "م")
        section_day = section_days[i].text
        section_bld = section_blds[i].text.replace("TBA", "لم يتم الإعلان")
        section_room = section_rooms[i].text.replace("TBA", "لم يتم الإعلان")
        section_instr = section_instrs[i].text.replace("TBA", "لم يتم الإعلان").replace('(P)', '').strip()
        section_link_crn = section_links[i].get_attribute('href').split("crn_in=")[1]

        # Check if day is empty, if so then skip the entire section.
        if section_day == ' ':
            continue

        # if section_bld "المبنى" has the word Blackboard, then set section_room "الغرفة" to "عن بُعد"
        if "Blackboard" in section_bld:
            section_room = "عن بُعد"

        # Check if the section is already in the section_info dictionary, if not, add it.
        if section_link_crn not in section_info[course_title]["Section(s)"]:
            section_info[course_title]["Section(s)"][section_link_crn] = {
                'الشعبة': section_num,
                'نوع الجدول': section_type,
                'الوقت': section_time,
                'الأيام': section_day,
                'المبنى': section_bld,
                'الغرفة': section_room,
                'الاساتذة': section_instr,
                'محاضرات أخرى': []
            }

        else:
            # If the section is already in the dictionary, add other lectures that belongs to the existing section using CRN as the key.
            existing_section = section_info[course_title]["Section(s)"][section_link_crn]['محاضرات أخرى']

            # Create a dictionary to store the section information
            section = {
                'الوقت': section_time,
                'الأيام': section_day,
                'المبنى': section_bld,
                'الغرفة': section_room,
                'الاساتذة': section_instr
            }
            # Append the section details to the existing section
            existing_section.append(section)

    # Record end time of section scraping for this course
    end_time = time.time()
    # Calculate the execution time for scraping the sections of this course
    execution_time = end_time - start_time

    execution_time_minutes = int(execution_time // 60)
    execution_time_seconds = int(execution_time % 60)
    execution_time_milliseconds = int((execution_time % 1) * 1000)

    # Print the execution time for scraping this course
    print(f"Time it took to scrape {course_title}: {execution_time_minutes} minutes {execution_time_seconds} seconds {execution_time_milliseconds} milliseconds\n")

    # Insert data to database
    DBconnection.Insert_SectionInfo(section_info)

    # Go back to the previous page that contains other courses information
    driver.back()

print("Sections information was inserted in the database successfully.")

# Record end time of execution
end_of_exec_time = time.time()

# Calculate the total execution time
full_execution_time = end_of_exec_time - start_of_exec_time

full_execution_time_minutes = int(full_execution_time // 60)
full_execution_time_seconds = int(full_execution_time % 60)
execution_time_milliseconds = int((full_execution_time % 1) * 1000)

# Print the total execution time
print(f"Execution time: {full_execution_time_minutes} minutes {full_execution_time_seconds} seconds {execution_time_milliseconds} milliseconds")