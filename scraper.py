from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_page(url):
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")

    service = Service('/path/to/chromedriver')  # Update with your path to chromedriver
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        time.sleep(5)  # Wait for the page to fully load
        html_content = driver.page_source
        return html_content
    except Exception as err:
        logging.error(f'An error occurred: {err}')
    finally:
        driver.quit()
    return None

def parse_indeed(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    job_listings = []

    jobs = soup.find_all('div', class_='job_seen_beacon')
    logging.info(f"Found {len(jobs)} job cards")

    for job in jobs:
        try:
            title = job.find('h2', class_='jobTitle').get_text(strip=True)
            company = job.find('span', class_='companyName').get_text(strip=True)
            location = job.find('div', class_='companyLocation').get_text(strip=True)
            link = 'https://www.indeed.com' + job.find('a', href=True)['href']
            description = job.find('div', class_='job-snippet').get_text(strip=True)

            job_info = {
                'Title': title,
                'Company': company,
                'Location': location,
                'Link': link,
                'Description': description
            }
            job_listings.append(job_info)
        except Exception as e:
            logging.error(f"Error parsing job details: {e}")
            logging.debug(f"Job HTML: {job}")

    return job_listings

def save_to_csv(jobs, filename='indeed_job_details.csv'):
    if not jobs:
        logging.error("No data to save")
        return
    
    keys = jobs[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(jobs)

def scrape_indeed_jobs(url):
    html_content = fetch_page(url)
    if html_content:
        jobs = parse_indeed(html_content)
        return jobs
    else:
        logging.error("Failed to retrieve the webpage.")
        return []

def main():
    url = input("Enter the Indeed job search URL to scrape: ")
    
    jobs = scrape_indeed_jobs(url)
    
    if jobs:
        save_to_csv(jobs)
        print(f"Scraped {len(jobs)} job details and saved to indeed_job_details.csv")
        print("\nExtracted Information (first 5 jobs):")
        for job in jobs[:5]:
            print("\n---")
            for key, value in job.items():
                print(f"{key}: {value[:100]}..." if len(str(value)) > 100 else f"{key}: {value}")
    else:
        print("Failed to scrape job details.")

if __name__ == '__main__':
    main()