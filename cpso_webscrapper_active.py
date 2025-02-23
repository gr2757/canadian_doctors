import platform
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import math

directory = "D:/Dropbox/Remote/CSPO/all_doctors/" #entry directory on this line
chrome_service = Service(executable_path="C:/Users/i5-760/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Python 3.12/chromedriver.exe") #here is the chrome driver path

#this is for the actual doctor page and saves the file
def search_results_function(search_results, directory):
    for result in search_results:
        # Find the <a> tag within the result
        link = result.find_element(By.TAG_NAME, 'a')
        url = link.get_attribute('href')

        # Use JavaScript to open a new tab and navigate to the URL
        script = f"window.open('{url}', '_blank');"
        d.execute_script(script)

        # Switch to the new tab
        d.switch_to.window(d.window_handles[-1])

        # Wait for the new page to load
        try:
            WebDriverWait(d, 1).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
        except Exception as e:
            print(f"Error loading page {url}: {e}")
            d.close()
            d.switch_to.window(d.window_handles[0])
            continue

        # Click the buttons
        try:
            view_more_button = WebDriverWait(d, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-controls='additionallocations']"))
            )
            view_more_button.click()
            time.sleep(1)  # Wait for any dynamic content to load
        except Exception as e:
            pass
        try:
            professional_info_button = WebDriverWait(d, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-controls='professionalcorporationinfo']"))
            )
            professional_info_button.click()
            time.sleep(1)  # Wait for any dynamic content to load
        except Exception as e:
            pass

        # Wait for the dynamic content to load completely
        time.sleep(1)  # Adjust this delay as necessary

        try:
            cpso_number_element = d.find_element(By.XPATH, "//h3[contains(text(), 'CPSO#:')]")
            cpso_number = cpso_number_element.text.strip()
            cpso_match = re.search(r'\d+', cpso_number)
            cpso_number = cpso_match.group(0)
            filename = os.path.join(directory, cpso_number + '.txt')
        except:
            print("cpso error")
            url_name = url.split('/')[-1]  # Extract the last part of the URL (e.g., "0036194-50170")
            match = re.search(r"-(.*)", url_name)  # Extract the part after the last hyphen
            if match:
                cpso_number = match.group(1)
                filename = os.path.join(directory, cpso_number + '.txt')
            else:
               print("no file name")
               break

        
        # Save the entire page as plain text
        try:
            page_text = d.find_element(By.TAG_NAME, 'body').text
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(page_text)
            print("file saved", cpso_number)

        except Exception as e:
            print("error with", cpso_number)

        # Close the current tab and switch back to the main window
        d.close()
        d.switch_to.window(d.window_handles[0])

#this is to scroll through the results pages, it opens the link in a new tab runs the function above to save files
def scroll_pages(directory):
    try:
        pagination_element = WebDriverWait(d, 1).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Page')]"))
        )
        pagination_text = pagination_element.text.strip()
        html_page = d.find_element("id", "CurrentPageNumber").get_attribute("value")
        html_page = int(html_page)
        page_info = pagination_text.split()
        total_pages = int(page_info[3])
    except:
        print("couldn't grab page info")
        

    while html_page < total_pages:

        # try: 
        #     html_page = d.find_element("id", "CurrentPageNumber").get_attribute("value")
        #     html_page = int(html_page)
        # except:
        #     print("html page errror in while loop")

        for i in range(5):
            try:
                html_page = d.find_element("id", "CurrentPageNumber").get_attribute("value")
                html_page = int(html_page)
                next_page = html_page + 1
            except:
                print("no html page found")
                break
            print("current_page:", html_page) 
            # print("what part of loop", i)
            
            try:
                search_results = d.find_elements(By.CLASS_NAME, 'doctor-search-results--result')
                search_results_function(search_results, directory)  # Process results on the current page
            except Exception as e: 
                print(e)
                print("error in search results")
            
            #After it loops throught the 10 results, hit next page
            try:
                next_page_button = WebDriverWait(d, 1).until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[@name='newPageNumber' and @value='{next_page}']"))
                )
                next_page_button.click()
                print("next page buttom pressed, page:", next_page)
            except:
                print("next page error")
        print("end of page loop")

    return()

#this is to skip to the correct page incase if loop breaks due to error
def find_page(target_number):

    presses_needed = math.floor(target_number / 5)

    for _ in range(presses_needed):
        try:

            html_page = d.find_element("id", "CurrentPageNumber").get_attribute("value")
            html_page = int(html_page)
            print(html_page)
        except:
            print("couldn't grab page info")
        

        try:
            next_five_button = WebDriverWait(d, 1).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@name='newPageNumber' and @class='next']"))
            )
            next_five_button.click()
            print("next five pages")
        except:
            print("next five pages button doesn't work")


plain_directory = directory + "plain_search5" #add the folder to here where you'd want the output

d = webdriver.Chrome(service=chrome_service)
d.get('https://www.cpso.on.ca/en/Public/Doctor-Search?search=general') #page to start the web scrape



e = d.find_element(By.ID, 'p_lt_ctl01_pageplaceholder_p_lt_ctl02_CPSO_AllDoctorsSearch_btnSubmit1') #click on active doctors
e.click()



# Wait for the search results to load
WebDriverWait(d, 1).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'doctor-search-results'))
)

find_page(1) 
# Find all article elements with the class doctor-search-results--result
scroll_pages(plain_directory)