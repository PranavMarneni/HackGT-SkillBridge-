import kaggle
import os

os.environ['KAGGLE_USERNAME'] = "ryderpongracic"
os.environ['KAGGLE_KEY'] = "1489bdeda5bfcedb5cb221506ce84198"

def get_datasets_for_skills(skills):
    print("\nFetching dataset recommendations for skills...")
    for skill in skills:
        print(f"\nDatasets for skill: {skill}")
        try:
            datasets = kaggle.api.dataset_list(search=skill, sort_by='hottest')
            for dataset in datasets[:5]:  # Limit to top 5 results
                print(f" - {dataset.title}: https://www.kaggle.com/{dataset.ref}")
        except Exception as e:
            print(f"Error fetching datasets for {skill}: {e}")

def get_competitions_for_skills(skills):
    print("\nFetching competition recommendations for skills...")
    for skill in skills:
        print(f"\nCompetitions for skill: {skill}")
        try:
            competitions = kaggle.api.competitions_list(search=skill, sort_by='recentlyCreated')
            for competition in competitions[:5]:  # Limit to top 5 results
                print(f" - {competition.title}: https://www.kaggle.com/c/{competition.ref}")
        except Exception as e:
            print(f"Error fetching competitions for {skill}: {e}")

def get_projects_for_skills(skills):
    print("\nFetching Kaggle kernel recommendations for skills...")
    for skill in skills:
        print(f"\nKernels for skill: {skill}")
        try:
            kernels = kaggle.api.kernels_list(search=skill, sort_by='hotness')
            for kernel in kernels[:5]:  # Limit to top 5 results
                print(f" - {kernel.title}: https://www.kaggle.com/{kernel.ref}")
        except Exception as e:
            print(f"Error fetching kernels for {skill}: {e}")

# Main function to input skills and get recommendations
if __name__ == "__main__":
    # Replace this list of skills with your preferred skills
    skills = ["Python", "Machine Learning", "Data Science", "NLP"]

    # Fetch datasets based on skills
    get_datasets_for_skills(skills)
    
    # Fetch competitions based on skills
    get_competitions_for_skills(skills)

    # Fetch project ideas based on skills
    get_projects_for_skills(skills)
