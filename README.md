# JobTrack — Job Application Management System

JobTrack is a full-stack web application designed to help job seekers, especially freshers, organize and manage their job search in one place. Users can discover jobs, apply through official company websites, track application statuses, manage interviews, and receive website notifications.

## Features

- **User Authentication:** Register, login, and Google sign-in.
- **Job Search:** Search and filter jobs by title, company, location, skills, and experience.
- **Job Details:** View job descriptions, requirements, salary, and application deadlines.
- **External Applications:** Visit official company websites to apply for jobs.
- **Application Tracking:** Track applications through Applied, Interview, Selected, Rejected, and Withdrawn statuses.
- **Saved Jobs:** Bookmark job opportunities for later.
- **Interview Management:** Store interview dates, times, meeting links, and notes.
- **Website Notifications:** Receive interview reminders, application updates, and deadline notifications.
- **User Dashboard:** Monitor applications, upcoming interviews, and job-search progress.
- **Admin Dashboard:** Manage users, companies, job listings, categories, and notifications.
- **Responsive Design:** Access the platform across desktop, tablet, and mobile devices.

## Technology Stack

| Category | Technologies |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| UI Framework | Bootstrap 5 |
| Backend | Python, Django |
| REST API | Django REST Framework |
| Database | MongoDB |
| Database Integration | PyMongo |
| Authentication | Django Authentication, Google OAuth 2.0 / OpenID Connect |
| Tools | Git, GitHub, VS Code, Postman, MongoDB Atlas |

## System Architecture

```text
Frontend
HTML + CSS + JavaScript + Bootstrap
              |
              v
       Django Backend
              |
              v
    Django REST Framework
              |
              v
           PyMongo
              |
              v
      MongoDB / Atlas
```

## User Workflow

1. Register or log in to JobTrack.
2. Browse, search, and filter available jobs.
3. View job details and visit the official company application page.
4. Complete the application on the company's website.
5. Return to JobTrack and mark the job as applied.
6. Track application progress and update statuses.
7. Manage interviews and receive relevant website notifications.

## Installation and Setup

### Prerequisites

- Python
- MongoDB or MongoDB Atlas account
- Git
- pip

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd JobTrack
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and configure the required settings:

```env
SECRET_KEY=your-secret-key
DEBUG=True
MONGODB_URI=your-mongodb-connection-string
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

Use the variable names expected by your Django settings. Never commit real credentials or secrets to GitHub.

### 5. Run the Application

```bash
python manage.py runserver
```

Open the local development server at:

```text
http://127.0.0.1:8000/
```

**Note:** Complete the MongoDB, Google authentication, and environment configuration required by your project before running the application. Apply migrations if your Django configuration requires them.

## Main Modules

- Accounts and User Profiles
- Job Listings and Search
- Job Applications and Tracking
- Saved Jobs
- Interview Management
- Website Notifications
- User Dashboard
- Admin Dashboard
- REST API

## Security

- Password hashing and secure authentication
- Role-based authorization
- CSRF protection and input validation
- Protected admin routes
- Secure resume upload validation
- Environment-based configuration
- HTTPS for production deployment

## Future Enhancements

- AI-powered resume analysis
- Resume-to-job matching
- Personalized job recommendations
- AI interview preparation
- Email and WhatsApp reminders
- Calendar integration
- Advanced application analytics
- Mobile application

## Project Objective

The main goal of JobTrack is to simplify job searching and application management by providing a centralized platform where freshers and other job seekers can organize opportunities, track progress, and prepare for interviews efficiently.

## Author

**Krishna Prasanna**

Developed as a full-stack web development project using Python, Django, MongoDB, and modern web technologies.

---

*JobTrack — Discover opportunities. Track applications. Manage your career.*
