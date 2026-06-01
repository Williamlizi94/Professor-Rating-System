# 🎓 Professor Rating System

A clean and interactive professor rating website that helps students search, filter, and compare professor information from **De Anza College** and **UC San Diego**.

🌐 **Live Demo:**
https://williamlizi94.github.io/Professor-Rating-System/

---

## 🚀 Overview

**Professor Rating System** is a front-end web application designed to help students quickly browse professor ratings, departments, difficulty levels, and recent student reviews.

The goal of this project is to make professor information easier to access and compare in one simple interface. The deployed website runs as a static GitHub Pages project using HTML, CSS, JavaScript, Bootstrap, and JSON data.

This project also includes Python scripts that were used during development to collect, update, and test professor rating data. The Python files are mainly for data preparation and local testing, while the public website itself runs fully in the browser.

---

## ✨ Features

* 🔍 Search professors by name or department
* 🏫 Filter professors by school: De Anza College or UC San Diego
* ⭐ Filter by minimum rating
* 📊 Filter by maximum difficulty
* 🏢 Browse departments from both schools
* 💬 View recent student reviews and comments
* 📈 View statistics such as:

  * Total professors
  * Total reviews
  * Average rating
  * Department count
  * Top departments
* 🌐 Fully deployed with GitHub Pages
* 🐍 Includes Python scripts for data collection and local testing

---

## 🛠️ Tech Stack

<p>
  <img src="https://img.shields.io/badge/HTML-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/CSS-1572B6?style=for-the-badge&logo=css3&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" />
  <img src="https://img.shields.io/badge/Font%20Awesome-538DD7?style=for-the-badge&logo=fontawesome&logoColor=white" />
  <img src="https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/GitHub%20Pages-222222?style=for-the-badge&logo=github&logoColor=white" />
</p>

---

## 📄 Pages

| Page               | Description                                      |
| ------------------ | ------------------------------------------------ |
| `index.html`       | Main search page for finding professors          |
| `departments.html` | Browse departments by school                     |
| `professors.html`  | View professor list and filtered results         |
| `stats.html`       | View overall professor and department statistics |

---

## 📁 Project Structure

```text
Professor-Rating-System/
├── index.html
├── departments.html
├── professors.html
├── stats.html
├── rmp_deanza_all_professors.json
├── rmp_ucsd_all_professors.json
├── De Anza And UCSD/
│   ├── DeAnza_AllProfessors.py
│   ├── UCSD_AllProfessors.py
│   ├── api.py
│   ├── measure_latency.py
│   ├── requirements.txt
│   ├── run_api_server.py
│   ├── start_api.bat
│   ├── test_api.py
│   ├── test_api_simple.py
│   └── update_data.py
└── README.md
```

---

## 🐍 Data Scripts

The `De Anza And UCSD/` folder contains Python files used during the development process.

These scripts were used for:

* Collecting professor rating data
* Updating local JSON files
* Testing API-style data access locally
* Measuring basic local performance
* Preparing data for the static front-end website

The deployed GitHub Pages website does **not** require a running Python backend. Instead, it reads from the static JSON files in the main project folder.

---

## 🧠 What I Learned

While building this project, I practiced turning raw data into a usable web application. I also learned how to debug real deployment issues, including GitHub Pages routing problems, static file paths, browser caching, and replacing local API calls with static JSON data.

This project helped me better understand how front-end applications work after deployment, not just on localhost. It also improved my skills in JavaScript data filtering, DOM manipulation, responsive design, data preparation, and practical debugging.

---

## 🔮 Future Improvements

* Add professor detail pages
* Improve mobile layout
* Add sorting by rating, difficulty, and number of reviews
* Add charts for department-level statistics
* Add dark mode
* Improve loading performance for large JSON files
* Organize Python scripts into a cleaner `scripts/` folder
* Add screenshots to the README

---

## 👤 Author

**William Lizi**
Computer Science Student at UC San Diego

GitHub: https://github.com/Williamlizi94
