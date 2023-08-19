# JobLinker

<div>
  <img src="https://github.com/Erfan4708/JobLinker/blob/main/static/joblinker.png" alt="JobLinker Header Image">
</div>

JobLinker is a web application that aggregates job listings from various job boards and recruitment websites, providing users with a centralized platform to explore and search for job opportunities based on their skills and preferences.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Introduction

Are you tired of visiting multiple job websites and sifting through countless job listings to find the right opportunity? JobLinker solves this problem by collecting job postings from various job boards and presenting them in one place. Job seekers can easily browse through the listings, filter results based on their skills, experience, and preferences, and save time in their job search process.

## Features

- **Centralized Job Search:** JobLinker fetches job listings from multiple job boards and displays them in a unified interface, eliminating the need for users to visit each site separately.

- **Customized Filtering:** Users can apply filters based on their skills, location, job type, and other preferences to narrow down the job listings and find the best-suited opportunities.

- **Regular Updates:** The platform utilizes automated web crawlers powered by Selenium to scrape job postings from various websites. These crawlers run at regular intervals to ensure that the job database remains up-to-date.

- **User-Friendly Interface:** JobLinker offers an intuitive and user-friendly interface, making it easy for job seekers to navigate, search, and save job listings.

## How It Works

JobLinker employs Selenium-powered web crawlers to scrape job listings from a curated list of job boards and recruitment websites. The scraped data is then stored in a database. The project uses Celery for task management, allowing the web crawlers to run periodically. Every half hour, the crawlers fetch and update the database with newly published job listings.

**Scheduled Task Management:** JobLinker uses Celery Beat for task scheduling, which automates the periodic execution of web crawlers to update the job database with fresh listings.

**Custom Driver Configuration:** You can configure your own Webdriver settings in the `task.py` file to suit your requirements.

## Installation

To run JobLinker locally, follow these steps:

1. Clone the repository: `git clone https://github.com/Erfan4708/JobLinker`
2. Navigate to the project directory: `cd joblinker`
3. Install the required dependencies: `pip install -r requirements.txt`
4. Set up your database configuration in `settings.py`
5. Configure your Webdriver settings in `task.py`
6. Run migrations: `python manage.py migrate`
7. Start the Celery worker: `celery -A config worker -l info`
8. Start the development server: `python manage.py runserver`

## Usage

1. Access the application via your web browser.
2. Browse through the aggregated job listings on the homepage.
3. Use the filters to refine your search based on your skills, location, and preferences.
4. Click on a job listing to view more details and apply.

## Deployment

JobLinker has been deployed and is accessible at the following URL:
[https://joblinker.iran.liara.run/](https://joblinker.iran.liara.run/)

## Contributing

Contributions to JobLinker are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request. For major changes, please discuss them with the project maintainers first.


## Note

This project is intended for educational purposes and serves as a demonstration of web scraping and application development. It has the potential for further enhancements and improvements. If you have any suggestions or encounter any issues, feel free to reach out and contribute to its growth.

---
