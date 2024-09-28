import requests
from bs4 import BeautifulSoup
import csv
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
import markdown
import re
import json
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def get_default_branch(repo_owner, repo_name):
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data.get('default_branch', 'main')
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get repository information: {e}")
        return 'main'

def fetch_github_jobs(repo_owner="SimplifyJobs", repo_name="Summer2025-Internships", file_path="README.md", branch=None):
    if branch is None:
        branch = get_default_branch(repo_owner, repo_name)
    
    url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/{file_path}"
    logging.info(f"Attempting to fetch content from: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        
        content = response.text
        logging.info("Successfully fetched content from GitHub.")
        
        job_postings = parse_markdown_jobs(content)
        return job_postings
        
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        if e.response.status_code == 404:
            logging.error(f"404 Error: The requested resource was not found. URL: {url}")
        elif e.response.status_code == 403:
            logging.error("403 Error: Access forbidden. Check if the repository is private or if you've exceeded the API rate limit.")
        else:
            logging.error(f"HTTP {e.response.status_code} error occurred.")
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching the content: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    
    return []

def parse_markdown_jobs(markdown_content):
    html = markdown.markdown(markdown_content, extensions=['tables'])
    soup = BeautifulSoup(html, 'html.parser')
    job_postings = []

    # Find the table containing job postings
    table = soup.find('table')
    if not table:
        logging.warning("No table found in the content. Checking for alternative formats...")
        return parse_alternative_format(soup)

    headers = [th.get_text(strip=True) for th in table.find('tr').find_all('th')]

    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        if len(cells) != len(headers):
            continue

        job_data = {}
        for header, cell in zip(headers, cells):
            if cell.find('a'):
                job_data[header] = {
                    'text': cell.get_text(strip=True),
                    'link': cell.find('a')['href']
                }
            else:
                job_data[header] = cell.get_text(strip=True)

        job_postings.append(job_data)

    logging.info(f"Found {len(job_postings)} job postings.")
    return job_postings

def parse_alternative_format(soup):
    job_postings = []
    # Check for list format
    job_list = soup.find('ul')
    if job_list:
        for item in job_list.find_all('li'):
            job_data = parse_list_item(item)
            if job_data:
                job_postings.append(job_data)
    else:
        logging.warning("No recognized job posting format found.")
    
    return job_postings

def parse_list_item(item):
    text = item.get_text(strip=True)
    link = item.find('a')
    if link:
        return {
            'Company': link.get_text(strip=True),
            'Details': text.replace(link.get_text(strip=True), '').strip(),
            'Link': link['href']
        }
    return None

def save_job_postings(job_postings, filename='github_job_postings.json'):
    if not job_postings:
        logging.info("No job postings to save.")
        return

    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(job_postings, jsonfile, indent=2)

    logging.info(f"Job postings saved to {filename}.")

def get_job_details(url):
    page_source = get_selenium_page(url)
    if page_source:
        soup = BeautifulSoup(page_source, 'html.parser')
        return extract_job_details(soup, url)
    return None

def load_job_postings(filename='github_job_postings.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"File {filename} not found.")
        return []
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {filename}.")
        return []

def display_job_postings(job_postings):
    print("\nAvailable Job Postings:")
    for index, job in enumerate(job_postings, start=1):
        company = job.get('Company', {})
        company_name = company.get('text', 'N/A') if isinstance(company, dict) else company or 'N/A'
        role = job.get('Role', 'N/A')
        location = job.get('Location', 'N/A')
        print(f"{index}. {company_name} - {role} ({location})")

def get_user_selection(job_postings):
    while True:
        try:
            selection = int(input("\nEnter the number of the job you want to view (or 0 to exit): ")) - 1
            if selection == -1:
                return None
            if 0 <= selection < len(job_postings):
                return job_postings[selection]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def fetch_job_page(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching the job page: {e}")
        return None

def parse_job_details(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    domain = urlparse(url).netloc
    job_details = {'URL': url}

    if 'greenhouse.io' in domain:
        job_details['Title'] = soup.find('h1', class_='app-title').get_text(strip=True) if soup.find('h1', class_='app-title') else 'N/A'
        company_elem = soup.find('div', class_='company-name')
        job_details['Company'] = company_elem.get_text(strip=True) if company_elem else 'N/A'
        location_elem = soup.find('div', class_='location')
        job_details['Location'] = location_elem.get_text(strip=True) if location_elem else 'N/A'
        description_elem = soup.find('div', id='content')
        job_details['Description'] = description_elem.get_text(strip=True) if description_elem else 'N/A'
    elif 'lever.co' in domain:
        job_details['Title'] = soup.find('h2', class_='posting-headline').get_text(strip=True) if soup.find('h2', class_='posting-headline') else 'N/A'
        company_elem = soup.find('div', class_='posting-category company')
        job_details['Company'] = company_elem.get_text(strip=True) if company_elem else 'N/A'
        location_elem = soup.find('div', class_='posting-category location')
        job_details['Location'] = location_elem.get_text(strip=True) if location_elem else 'N/A'
        description_elem = soup.find('div', class_='section page-full-width')
        job_details['Description'] = description_elem.get_text(strip=True) if description_elem else 'N/A'
    else:
        job_details['Title'] = soup.title.string if soup.title else 'N/A'
        job_details['Description'] = soup.get_text(strip=True)

    return job_details

def display_job_details(job_details):
    print("\nScraped Job Details:")
    for key, value in job_details.items():
        if key == 'Description':
            print(f"{key}: {value[:200]}...") # Print only first 200 characters of description
        else:
            print(f"{key}: {value}")

def save_job_details(job_details, filename='scraped_job_details.json'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(job_details, f, ensure_ascii=False, indent=4)
        logging.info(f"Job details saved to {filename}.")
    except IOError as e:
        logging.error(f"Error saving job details: {e}")

def main():
    job_postings = load_job_postings()
    if not job_postings:
        print("No job postings available.")
        return

    while True:
        display_job_postings(job_postings)
        selected_job = get_user_selection(job_postings)
        
        if selected_job is None:
            print("Exiting program.")
            break

        application_link_data = selected_job.get('Application/Link')
        if isinstance(application_link_data, dict):
            application_link = application_link_data.get('link', '')
        else:
            application_link = application_link_data or ''

        if not application_link:
            print("No application link available for the selected job.")
            continue

        print(f"\nFetching details for the selected job from: {application_link}")
        html_content = fetch_job_page(application_link)
        if not html_content:
            print("Failed to fetch the job posting page.")
            continue

        job_details = parse_job_details(html_content, application_link)
        display_job_details(job_details)
        save_job_details(job_details)

        choice = input("\nDo you want to view another job? (y/n): ").lower()
        if choice != 'y':
            print("Exiting program.")
            break

if __name__ == '__main__':
    main()