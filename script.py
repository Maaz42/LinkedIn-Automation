import getpass
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

# Load campaign configuration
with open('config/config.json') as f:
    config = json.load(f)

# Set up Selenium WebDriver
# Define the custom user data directory path
user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")

# Set up Chrome options to use the custom user data directory
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"user-data-dir={user_data_dir}")

# Initialize the WebDriver with the custom options
# chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

# Function to wait for an element to be clickable
def wait_for_clickable(by, identifier, timeout=30):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, identifier))
    )

# Function to wait for an element to be present
def wait_for_element(by, identifier, timeout=30):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, identifier))
    )

# Function to read content from the content library
def get_content_from_library(content_type):
    folder_path = os.path.join(os.getcwd(), f'content_library/{content_type}/')
    files = os.listdir(folder_path)
    return [os.path.abspath(os.path.join(folder_path, file)) for file in files]

# Custom delay function
def delay(seconds):
    time.sleep(seconds)

# Function to scroll an element into view using JavaScript
def scroll_into_view(element):
    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)


# Read content from the content library
video_files = get_content_from_library('video')
image_files = get_content_from_library('image')
text_files = get_content_from_library('text')

# Select the first available file for each content type as an example
selected_video = video_files[0] if video_files else None
selected_image = image_files[0] if image_files else None
selected_text = text_files[0] if text_files else None

# Login to LinkedIn
print("Logging in to LinkedIn...")
driver.get("https://www.linkedin.com/login")
try:
    username_field = wait_for_clickable(By.ID, "username", timeout=5)
    password_field = driver.find_element(By.ID, "password")

    # Get email and password from the user
    # email = input("Enter your LinkedIn email: ")
    # password = getpass.getpass("Enter your LinkedIn password: ")

    username_field.send_keys(config["email"])
    password_field.send_keys(config["password"])
    password_field.send_keys(Keys.RETURN)

    # Handle 2FA
    # Wait for the 2FA input field to be present
    two_fa_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "input__phone_verification_pin"))
    )
    two_fa_code = input("Enter the 2FA code sent to your device: ")
    two_fa_field.send_keys(two_fa_code)
    two_fa_field.send_keys(Keys.RETURN)
except Exception as e:
    print(f"Bypassing Login {e}")

# Wait to ensure login was successful
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.ID, "voyager-feed"))
)
print("2FA successful and logged in.")


# Navigate to Campaign Manager
print("Navigating to Campaign Manager...")
driver.get("https://www.linkedin.com/campaignmanager/accounts")

# Create a new account
print("Creating a new account...")
create_account_button = wait_for_clickable(By.XPATH, "//button[span[text()='Create']]")
create_account_button.click()
account_name = wait_for_clickable(By.ID, "account-name")
account_name.clear()
account_name.send_keys(config['account_name'])
delay(2)
currency = driver.find_element(By.ID, "account-currency")
currency_select = Select(currency)
currency_select.select_by_value(config['currency'])
delay(2)
company_page = driver.find_element(By.ID, "account-reference")
company_page.send_keys(str(config['linkedin_page_url']))
delay(2)
create_account = wait_for_clickable(By.XPATH, "//button[span[text()='Save']]")
create_account.click()

# checking for accelerate popup
try:
    accelerate_popup = wait_for_clickable(By.XPATH, f"//button[.//span[text()='No thanks']]", timeout=3)
    accelerate_popup.click()
except Exception as e:
    print(f"Accelerate popup not found. Bypassing")

# Create a new campaign
print("Creating a new campaign...")
delay(2)
create_campaign_button = wait_for_clickable(By.XPATH, "//*[@aria-label='Dropdown to create an entity such as an account, campaign group, or campaign']")
create_campaign_button.click()
delay(2)
create_campaign_button_v2 = wait_for_clickable(By.XPATH, "//button[.//div[text()='Campaign']]")
create_campaign_button_v2.click()

# lets_get_started = wait_for_clickable(By.XPATH, "//button[text()=\"Let's get started\"]")
# lets_get_started.click()

# quick_mode = wait_for_clickable(By.XPATH, "//button[span[text()='Quick']]")
# quick_mode.click()
# campaign_name = wait_for_clickable(By.ID, "campaign-name")
# campaign_name.send_keys(config['campaign_name'])

# Choose a campaign objective
print("Choosing a campaign objective...")
try:
    # Check if a specific element is present
    try:
        objective = wait_for_clickable(By.XPATH, f"//label[.//p[text()='{config['objective']}']]", timeout=5)
        # Element found, perform some actions
        objective.click()
    except Exception as e:
        # Element not found, perform alternative actions
        print("Element not found, performing alternative actions", str(e))
        # Conditional find based on element's attribute
        objective = wait_for_clickable(By.XPATH, f"//button[.//p[text()='{config['objective']}']]")
        objective.click()
except Exception as e:
    print(f"Error: {e}")


# Campaign group details name
print("Setting campaign group details...")
campaign_name = wait_for_clickable(By.ID, "campaign-group-name")
campaign_name.clear()
campaign_name.send_keys(config['campaign_name'])
delay(2)


# Find the checkbox input with  start and end date
print("Setting campaign start and end date...")
campaign_start_end_date_checkbox = driver.find_element(By.ID, "campaign_group_schedule_scheduled")
if not campaign_start_end_date_checkbox.is_selected():
    campaign_start_end_date_checkbox.click()


# set start and end date
start_date = driver.find_element(By.XPATH, "//*[@aria-label='Start date, press enter to open calendar flyout']")
driver.execute_script("arguments[0].value = arguments[1];", start_date, config['start_date'])
driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", start_date)
driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", start_date)

end_date = driver.find_element(By.XPATH, "//*[@aria-label='End date, press enter to open calendar flyout']")
driver.execute_script("arguments[0].value = arguments[1];", end_date, config['end_date'])
driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", end_date)
driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", end_date)
delay(2)

# move to audience step
print("Moving to audience step...")
next_button = driver.find_element(By.XPATH, f"//button[.//span[text()='Next']]")
scroll_into_view(next_button)
delay(2)
next_button.click()

# location div is hidden by default, so we need to click on the button to show it
print("Setting audience location...")
location_button = wait_for_clickable(By.XPATH, "//button[@aria-label='Edit included locations']")
scroll_into_view(location_button)
location_button.click()
# search for the location
location_search = wait_for_clickable(By.XPATH, "//input[@aria-label='Search for locations to add to target audience' and @type='search']")
location_search.send_keys(config['location'])
delay(1)
# select the location
location_option = wait_for_clickable(By.XPATH, f"//li[.//span[text()='{config['location']}']]")
location_option.click()
delay(2)

# Set the audience
# audience_option = wait_for_clickable(By.XPATH, f"//label[.//p[text()='{config['audience_option']}']]")
# audience_option.click()

# choose_template_dropdown = wait_for_clickable(By.XPATH, "//input[@placeholder='Search by name or select from the list']")
# choose_template_dropdown.click()
# choose_template_dropdown.send_keys(config['linkedin_template'])

# choose_template_dropdown_select = wait_for_clickable(By.XPATH, f"//li[.//p[text()='{config['linkedin_template']}']]")
# choose_template_dropdown_select.click()

# Set the ad format
print("Setting ad format...")
ad_format = wait_for_clickable(By.XPATH, f"//label[.//p[text()='{config['ad_format']}']]")
ad_format.click()
delay(2)

# set associated company page (one time)
print("Associating company page...")
# budget = wait_for_element(By.ID, "company-association")
try:
    associate_page = wait_for_element(By.XPATH, "//input[@placeholder='Enter the page name, url, or create a new one']")
    associate_page.click()
    scroll_into_view(associate_page)
    delay(1)
    associate_page.send_keys(config['linkedin_page_url'])
    delay(1)
    associate_page_button = wait_for_clickable(By.XPATH, f"//button[.//span[text()='Associate Company Page']]")
    associate_page_button.click()
    delay(1)
    associate_page_button_confirm = wait_for_clickable(By.XPATH, f"//button[.//span[text()='Confirm']]")
    associate_page_button_confirm.click()
    delay(1)
except Exception as e:
    print(f"Association log: {e}")
# conditional text above for first time association only


# # Wait for the div with aria-label="Placement" to be present
# placement_div = WebDriverWait(driver, 30).until(
#     EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Section for Placement']"))
# )
# # Find the checkbox input within the div
# checkbox = placement_div.find_element(By.XPATH, ".//input[@type='checkbox']")

# # Wait for the checkbox to be clickable and then click it
# wait_for_clickable(By.XPATH, ".//input[@type='checkbox']")
# if not checkbox.is_selected():
#     checkbox.click()


# Set budget, start date, and end date
print("Setting budget, start date, and end date...")
budget_type_dropdown =  wait_for_clickable(By.XPATH, "//select[@title='Budget']")
budget_type_dropdown_select = Select(budget_type_dropdown)
budget_type_dropdown_select.select_by_value("lifetime")
scroll_into_view(budget_type_dropdown)
delay(2)

budget = wait_for_clickable(By.ID, "bid-and-budget__total-budget")
driver.execute_script("arguments[0].value = arguments[1];", budget, config['budget'])

# select start and end date option
# start_end_checkbox_inside = wait_for_clickable(By.ID, "bid-and-budget__schedule-fixed")
# start_end_checkbox_inside.click()

start_date =  wait_for_element(By.XPATH, "//input[@aria-label='Start date, press enter to open calendar flyout' and @type='text']")
driver.execute_script("arguments[0].value = arguments[1];", start_date, config['start_date'])
driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", start_date)
driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", start_date)


end_date =  wait_for_element(By.XPATH, "//input[@aria-label='End date, press enter to open calendar flyout' and @type='text']")
driver.execute_script("arguments[0].value = arguments[1];", end_date, config['end_date'])
driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", end_date)
driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", end_date)
delay(2)
# issue here with date picker


# move to ads step
print("Moving to ads step...")
next_button = wait_for_clickable(By.XPATH, f"//button[.//span[text()='Next']]")
next_button.click()
scroll_into_view(next_button)
delay(2)
next_button_v2 = wait_for_clickable(By.XPATH, f"//button[.//span[text()='Save']]")
next_button_v2.click()


# create new ad
print("Creating a new ad...")
create_ad_button = wait_for_clickable(By.XPATH, "//button[.//span[text()='Create new ad(s)']]")
create_ad_button.click()
delay(2)

# add ad name
print("Adding ad name and introductory text...")
ad_name = wait_for_clickable(By.ID, "name")
ad_name.send_keys(config['ad_name'])
delay(2)

# add introductory text
ad_introductory_text = wait_for_clickable(By.ID, "introductoryText")
ad_introductory_text.send_keys(config['ad_introductory_text'])
delay(2)


# upload content
print("Uploading content...")
upload_content_button = wait_for_clickable(By.XPATH, "//button[.//span[text()='Upload or select']]")
upload_content_button.click()
delay(2)

upload_content_upload_button = wait_for_clickable(By.XPATH, "//input[@aria-label='Upload button to choose files to upload' and @type='file']")
upload_content_upload_button.send_keys(selected_image)
delay(2)

add_to_library_button = wait_for_clickable(By.XPATH, "//button[.//span[text()='Add to Library']]")
add_to_library_button.click()
delay(2)

add_to_library_select_button = wait_for_clickable(By.XPATH, "//button[.//span[text()='Select']]")
add_to_library_select_button.click()
delay(2)

save_add_button = wait_for_clickable(By.XPATH, "//button[.//span[text()='Save ad']]")
save_add_button.click()
delay(2)

# next step
print("Moving to next step...Review and launch")

next_step_button = wait_for_clickable(By.XPATH, "//button[.//span[text()='Next'] and not(@disabled)]")
scroll_into_view(next_step_button)
next_step_button.click()
delay(2)

# save and exit
print("Saving and exiting...")
save_exit_button = wait_for_clickable(By.XPATH, "//button[.//span[text()='Save and exit']]")
save_exit_button.click()

delay(5)

# Close the browser
print("Closing the browser...")