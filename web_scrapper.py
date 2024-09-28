import requests
from bs4 import BeautifulSoup
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time

logging.basicConfig(level=logging.INFO)

def validate_job_url(url):
    valid_domains = [
        'ziprecruiter.com', 'craigslist.org', 'simplyhired.com',
        'reed.co.uk', 'dice.com', 'facebook.com/jobs', 'indeed.com',
        'greenhouse.io', 'lever.co', 'workday.com', 'smartrecruiters.com',
        'myworkdayjobs.com', 'jobs.lever.co', 'boards.greenhouse.io'
    ]
    return any(domain in url for domain in valid_domains)

def get_selenium_page(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        logging.info(f"Navigating to URL: {url}")
        driver.get(url)
        
        time.sleep(5)  # Wait for page to load
        
        page_source = driver.page_source
        driver.quit()
        return page_source
    except Exception as e:
        logging.error(f"Error fetching page with Selenium: {e}")
        return None

def extract_job_details(soup, url):
    job_details = {'URL': url}
    
    if 'indeed.com' in url:
        logging.info("Extracting details for Indeed job")
        
        title = soup.select_one('h1.jobsearch-JobInfoHeader-title')
        if title:
            job_details['Title'] = title.text.strip()
        else:
            logging.warning("Could not find job title")
        
        company = soup.select_one('div[data-company-name="true"]')
        if company:
            job_details['Company'] = company.text.strip()
        else:
            logging.warning("Could not find company name")
        
        location = soup.select_one('div[data-testid="job-location"]')
        if location:
            job_details['Location'] = location.text.strip()
        else:
            logging.warning("Could not find job location")
        
        description = soup.select_one('div#jobDescriptionText')
        if description:
            job_details['Description'] = description.text.strip()
        else:
            logging.warning("Could not find job description")
    
    elif 'ziprecruiter.com' in url:
        job_details['Title'] = soup.select_one('h1.job_title').text.strip()
        job_details['Company'] = soup.select_one('a.hiring_company').text.strip()
        job_details['Location'] = soup.select_one('div.location').text.strip()
        job_details['Description'] = soup.select_one('div.jobDescriptionSection').text.strip()
    
    elif 'craigslist.org' in url:
        logging.info("Extracting details for Craigslist job")
        
        title = soup.select_one('span#titletextonly')
        if title:
            job_details['Title'] = title.text.strip()
        else:
            logging.warning("Could not find job title")
        
        location = soup.select_one('div.mapaddress')
        if location:
            job_details['Location'] = location.text.strip()
        else:
            logging.warning("Could not find job location")
        
        description = soup.select_one('section#postingbody')
        if description:
            # Remove the "QR Code Link to This Post" text if present
            for element in description.select('p.print-information'):
                element.decompose()
            job_details['Description'] = description.text.strip()
        else:
            logging.warning("Could not find job description")
        
        # Try to extract compensation if available
        compensation = soup.select_one('p.attrgroup > span:contains("compensation:")')
        if compensation:
            job_details['Compensation'] = compensation.text.replace('compensation:', '').strip()
        
        # Try to extract employment type if available
        employment_type = soup.select_one('p.attrgroup > span:contains("employment type:")')
        if employment_type:
            job_details['Employment Type'] = employment_type.text.replace('employment type:', '').strip()
    
    elif 'simplyhired.com' in url:
        job_details['Title'] = soup.select_one('h1.JobDetailsHeader_jobTitle').text.strip()
        job_details['Company'] = soup.select_one('span.JobDetailsHeader_company').text.strip()
        job_details['Location'] = soup.select_one('span.JobDetailsHeader_location').text.strip()
        job_details['Description'] = soup.select_one('div.JobDescription_jobDescription').text.strip()
    
    elif 'reed.co.uk' in url:
        job_details['Title'] = soup.select_one('h1.job-header__job-title').text.strip()
        job_details['Company'] = soup.select_one('div.job-header__company-name').text.strip()
        job_details['Location'] = soup.select_one('span.job-header__location').text.strip()
        job_details['Description'] = soup.select_one('div.description').text.strip()
    
    elif 'dice.com' in url:
        job_details['Title'] = soup.select_one('h1.jobTitle').text.strip()
        job_details['Company'] = soup.select_one('a.company-name-link').text.strip()
        job_details['Location'] = soup.select_one('span.location').text.strip()
        job_details['Description'] = soup.select_one('div.job-description').text.strip()
    
    elif 'facebook.com/jobs' in url:
        job_details['Title'] = soup.select_one('div._8sel').text.strip()
        job_details['Company'] = soup.select_one('div._8sen').text.strip()
        job_details['Location'] = soup.select_one('div._8seo').text.strip()
        job_details['Description'] = soup.select_one('div._8sep').text.strip()
    
    return job_details

def get_job_details(url):
    page_source = get_selenium_page(url)
    if page_source:
        soup = BeautifulSoup(page_source, 'html.parser')
        return extract_job_details(soup, url)
    return None

def main():
    job_url = input("Enter the job URL: ")
    
    if not validate_job_url(job_url):
        print("Invalid job URL. Please enter a valid URL from supported job sites.")
        return
    
    try:
        job_data = get_job_details(job_url)
        
        if job_data:
            print("Extracted Job Data:")
            for key, value in job_data.items():
                print(f"{key}: {value}")
            return job_data
        else:
            print(f"Failed to fetch the page from {job_url}. Please try again later.")
        
    except Exception as e:
        print(f"An error occurred while processing the page: {e}")
        logging.exception("Error details:")

if __name__ == "__main__":
    job_details = main()
    if job_details:
        print(job_details)