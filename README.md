# Ceylon AgriData

**Project Name:** Enhancing Productivity in Sri Lanka’s Agriculture Sector with a Cloud-Based System for Data Acquisition and Representation to Facilitate Informed Decision Making  

**Course:** Individual Project for Master of Information Technology  

**Institution:** University of Colombo School of Computing  

## Overview

**Ceylon AgriData** is a cloud-based system designed to enhance Sri Lanka's agricultural productivity by transitioning from paper-based data collection to a digital platform. The system features:

- A **mobile app** for agricultural officers, facilitating streamlined data collection directly from the field, thereby improving data accuracy and accessibility.
- A **web application** providing user-friendly dashboards for data visualization, enabling informed decision-making and policy development.
- A **report generation tool** for creating detailed reports from aggregated agricultural data to facilitate operations.
- A **message broadcasting service** for timely dissemination of important information among stakeholders.
- A **free advertising service** that allows farmers to market their products directly, improving sales opportunities and supporting government price regulation efforts.
- A **REST API** for seamless communication between the mobile app and web application.

Built using **Python, Flask, React,** and **Flutter**, Ceylon AgriData utilizes a service-oriented multi-tier architecture to manage agricultural data effectively.

### Key Technologies
- **Mobile App:** Flutter framework with Dart
- **Web App:** React.js with JavaScript
- **Backend:** Python Flask REST API
- **Database:** MySQL (production), SQLite (development)

## Repository Contents
- **frontend/:** AgriData-FE - Contains the source code for the React.js web application.
- **backend/:** AgriData-BE - Contains the Python Flask backend with the necessary API endpoints and database connection settings.
- **mobile_app/:** AgriData_MobileApp - Contains the source code for the Flutter-based mobile application.

## Implementation Methodology
The **Ceylon AgriData** system follows a service-oriented multi-tier architecture:
- **Presentation Layer:** Mobile application (Flutter) and web application (React).
- **Application Logic Layer:** REST API developed using Python Flask.
- **Data Layer:** MySQL database for production, SQLite for initial development.

### Project Links
- **Mobile App Repository:** [Ceylon AgriData Mobile App](https://github.com/SanduniDR/AgriData_MobileApp)
- **Web App (Front End) Repository:** [Ceylon AgriData Front End](https://github.com/SanduniDR/AgriData-FE)
- **Web App (Back End) Repository:** [Ceylon AgriData Back End](https://github.com/SanduniDR/Agri-project-BE)

## Installation and Setup

### Prerequisites
- Node.js (v18.16.0) and npm (v9.5.1) for the web application.
- Flutter SDK for the mobile application.
- Python (3.0+) and pip for the backend.
- WAMP server for the MySQL database.

### Steps
1. **Clone the repository:**
   ```bash
   git clone REPOSITORY_LINK
   cd FOLDER_NAME
   
2. **Install dependencies:**
- For the mobile app (Flutter):
    ```bash
    cd myapp
    flutter pub get
   
 - For the web app (React.js):
    ```bash
    cd AgriData-FE
    npm install
    
  - For the backend (Flask):
    ```bash
    cd AgriData-BE
    pip install -r requirements.txt
    
3. **Run the applications:**
- Mobile app:
    ```bash
    flutter run

- Web app (React.js):
    ```bash
    npm start
    
- Backend (Flask):
    ```bash
    flask run

## Database Management

The project uses SQLAlchemy ORM to interact with databases in an object-oriented manner:

- SQLite was used in the development phase.
- MySQL is used in production for larger datasets.

## Implementation Environment

### Hardware Environment

| Environment         | Details                                   |
|---------------------|-------------------------------------------|
| Mobile Application   | Intel i5-1235U, 16GB RAM, Android Phone (Samsung A30, Android 11, 4GB RAM) |
| Web Application      | Intel i5-1235U, 16GB RAM                 |

### Software Environment

| Component           | Framework/Software      | Programming Language | Web Server                        | IDE           | Other Tools             |
|---------------------|-------------------------|----------------------|----------------------------------|---------------|-------------------------|
| Mobile App          | Flutter                 | Dart                 | -                                | Android Studio | Ngrok, Canva, Draw.io   |
| Web App             | React (v18.2.0)         | JavaScript           | React Inbuilt Server (Node.js)  | VS Code       | Canva, Draw.io          |
| Backend             | Flask (v3.0.0)         | Python               | Flask Development Server         | VS Code       | Flask-CORS, Pip, Marshmallow |
| Database            | MySQL (v8.0.31), SQLite | Python               | Apache (WAMP v3.3.0)            | -             | SQLAlchemy, Marshmallow  |





  

  


