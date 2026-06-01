# Professor Rating System

A clean and interactive professor rating website for students to search, filter, and compare professor information from **De Anza College** and **UC San Diego**.

Live Demo:
https://williamlizi94.github.io/Professor-Rating-System/

## Overview

Professor Rating System is a front-end web project that helps students quickly browse professor ratings, departments, difficulty levels, and recent student reviews. The goal of this project is to make professor information easier to access and compare in one simple interface.

The website is built as a static GitHub Pages project using HTML, CSS, JavaScript, Bootstrap, and JSON data. It does not require a backend server, so users can access it directly through the browser.

## Features

* Search professors by name or department
* Filter professors by school: All Schools, De Anza College, or UC San Diego
* Filter by minimum rating and maximum difficulty
* Browse departments from both schools
* View professor details including:

  * Average rating
  * Average difficulty
  * Number of reviews
  * Would-take-again percentage
  * Recent student comments
* View statistics such as total professors, total reviews, average rating, and top departments
* Fully deployed using GitHub Pages

## Tech Stack

* HTML
* CSS
* JavaScript
* Bootstrap
* Font Awesome
* JSON
* GitHub Pages

## Pages

| Page               | Description                                      |
| ------------------ | ------------------------------------------------ |
| `index.html`       | Main search page for finding professors          |
| `departments.html` | Browse departments by school                     |
| `professors.html`  | View professor list and filtered results         |
| `stats.html`       | View overall professor and department statistics |

## Project Structure

```text
Professor-Rating-System/
├── index.html
├── departments.html
├── professors.html
├── stats.html
├── rmp_deanza_all_professors.json
├── rmp_ucsd_all_professors.json
└── README.md
```

## What I Learned

While building this project, I practiced turning raw data into a usable web application. I also learned how to debug real deployment issues, including GitHub Pages routing problems, static file paths, browser caching, and replacing local API calls with static JSON data.

This project helped me better understand how front-end applications work after deployment, not just on localhost. It also improved my skills in JavaScript data filtering, DOM manipulation, responsive design, and practical debugging.

## Future Improvements

* Add professor detail pages
* Improve mobile layout
* Add sorting by rating, difficulty, and number of reviews
* Add charts for department-level statistics
* Add dark mode
* Improve data loading performance for large JSON files

## Author

**William Lizi**
Computer Science Student at UC San Diego

GitHub: https://github.com/Williamlizi94
