import json
import os
import boto3
import random
from bs4 import BeautifulSoup
from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['JOB_TABLE'])

USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
    ]

my_skills = ['Java', 'Python', 'C#', '.NET', 'Engineer',
                 'JavaScript', 'Backend', 'Typescript', 'Web Developer', 'Remote',
                 'Software', 'Full Time', 'Full Stack', 'Angular', 'English',
                 'Kotlin', 'Rust', 'Cloud', 'AWS', 'Android', 'Django', 'Spring boot']
wanted_salary = 50


def handler(event, context):
    url = 'https://remoteok.com/remote-dev-jobs'
    headers = {
        'User-Agent': random.choice(USER_AGENTS)
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    jobs = []

    for job in soup.find_all('tr', class_='job'):
        job_id = job.get('data-id')
        if not job_id:
            continue

        title = job.find('h2', itemprop='title').text.strip()
        locations = job.find_all('div', class_='location')
        salary = find_salary(locations)
        tags = job.find_all('div', class_='tag')
        skills = [tag.find('h3').text.strip() for tag in tags if tag.find('h3')]

        if meets_criteria(title, skills, salary):
            jobs.append({
                'job_id': job_id,
                'title': title,
                'skills': skills,
                'salary': salary
            })

        table.put_item(
                Item={
                    'job_id': job_id,
                    'title': title,
                    'skills': skills,
                    'salary': salary
                }
            )

    return {
        'statusCode': 200,
        'body': json.dumps(jobs)
    }



def find_salary(locations):
    for location in locations:
        if "$" in location.text.strip():
            salaries = location.text.strip().split("-")
            return (int(remove_characters(salaries[0])) + int(remove_characters(salaries[1]))) / 2


def has_all_skills(skills, my_skills):
    return all(skill in my_skills for skill in skills)


def meets_criteria(title, skills, salary):
    return ("Senior" not in title) and has_all_skills(skills, my_skills) and salary > wanted_salary


def remove_characters(input_string):
    return ''.join(char for char in input_string if char.isdigit())
