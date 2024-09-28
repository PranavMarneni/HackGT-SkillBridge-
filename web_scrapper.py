import requests
from bs4 import BeautifulSoup
import csv

# Add a comment to remind the user to install webdriver_manager if needed
# To use ChromeDriverManager, install webdriver_manager:
# pip install webdriver_manager

def validate_linkedin_job_url(url):
    return url.startswith("https://www.linkedin.com/jobs/")

def extract_job_details(soup):
    job_details = {}
    try:
        # Extract the job title
        job_details['Title'] = soup.select_one("h1.job-title").text.strip()

        # Extract the company name
        job_details['Company'] = soup.select_one("a.company-name").text.strip()

        # Extract the location
        job_details['Location'] = soup.select_one("span.job-location").text.strip()

        # Extract the job description
        job_details['Description'] = soup.select_one("div.job-description").text.strip()

    except Exception as e:
        print("Job details not found or different structure.")
        print(f"Error: {e}")
    
    return job_details

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

def main():
    linkedin_job_url = input("Enter the LinkedIn job URL: ")
    
    if not validate_linkedin_job_url(linkedin_job_url):
        print("Invalid LinkedIn job URL. Please enter a valid URL.")
        return
    
    try:
        # Send a GET request to the LinkedIn job page
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(linkedin_job_url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        job_data = extract_job_details(soup)
        
        print("Extracted Job Data:")
        print(job_data)
        
        save_to_csv(job_data, "linkedin_job.csv")
        print("Data saved to linkedin_job.csv")
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the page: {e}")

if __name__ == "__main__":
    main()
