# HackGT-SkillBridge
Overall Goals and User Story

### **User Story**:
As a user, I want to input multiple job postings (or links to them) so that the application can analyze the required skills and compare them to my resume, providing a personalized study plan to address any skill gaps.

### **Implementation Plan**:

1. **Job Postings Input**:
   - Initially, users will submit job posting links (e.g., from LinkedIn or similar websites). These links will be processed in real-time using a web scraper (like BeautifulSoup) to extract job descriptions and relevant skill requirements.
   - For simplicity, we will **not build a full job database**, as it's not scalable or feasible for this application. Instead, we’ll focus on scraping and processing links to extract job descriptions dynamically.

2. **Skills Extraction with LLM**:
   - After extracting the text from job postings, the application will utilize a LLM to analyze and summarize the required skills for each role. This process reduces the raw text into a concise, easy-to-manage skills list.
   - By storing only the refined list of required skills rather than the full job descriptions, we optimize data storage and improve efficiency.

3. **Temporary Data Storage**:
   - For the hackathon version of the application, **persistent data storage is not necessary**. The skills list will only be held temporarily while the user interacts with the app, and will be discarded after generating the study plan.
   - We’ll evaluate how much information the LLM can process in a single session. If storage constraints arise (based on token limits), a temporary database may be used to manage data.

4. **Skill Assessment & Study Plan Generation**:
   - Once multiple job postings have been processed, the LLM will **analyze the skills extracted from each** to identify key areas where the user’s resume lacks.
   - The application will generate a **personalized study plan**, complete with:
     - **Video tutorials**
     - **Practice problems**
     - **Projects that target specific skill gaps**

5. **APIs for Learning Resources**:
   - To provide high-quality study materials, the application will integrate:
     - **Udemy API** for relevant courses and tutorials.
     - **LeetCode API** for coding challenges and practice problems aligned with the required skills.
     - **Kaggle API** for advanced project and dataset recommendations, particularly for higher-level skills like data science and machine learning.

6. **Dynamic Project Recommendations**:
   - The application will also recommend **projects at different skill levels**, allowing users to gain hands-on experience in areas where they need improvement. This helps users grow through real-world tasks rather than just theory.
TechStack
Frontend - React(or if someone is good at another frontend framework thats chill too)
Backend - Django(to handle APIs, job posting processing, and LLM calls)
Web Scraping - BeautifulSoup(extract job descriptions out of provided links)
LLM - OpenAI API(tested it, gives rly solid study plan and recommendations)
Database: Session-based data storage or SQLite (if necessary).
APIs:
Udemy API for video tutorials.
LeetCode API for coding challenges.
Kaggle API for project recommendations.
GitHub API for open-source project suggestions.
