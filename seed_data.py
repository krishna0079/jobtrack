"""
Seed script — Populates MongoDB with demo data for development.
Run: python manage.py shell < seed_data.py
Or:  python seed_data.py (from JobTrack directory)
"""
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

import bcrypt
from datetime import datetime, timezone, timedelta
from config.db import get_db

db = get_db()

# ─── Clear existing data ─────────────────────────────────────
print("Clearing existing data...")
for col in ['users', 'companies', 'jobs', 'applications', 'interviews', 'notifications', 'saved_jobs']:
    db[col].delete_many({})

# ─── Create Admin User ───────────────────────────────────────
print("Creating admin user...")
admin_pw = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
admin = db.users.insert_one({
    'name': 'JobTrack Admin',
    'email': 'admin@jobtrack.com',
    'password': admin_pw,
    'role': 'admin',
    'phone': '',
    'location': '',
    'skills': [],
    'education': '',
    'experience': '',
    'profile_info': '',
    'resume': '',
    'auth_provider': 'local',
    'created_at': datetime.now(timezone.utc),
})

# ─── Create Demo User ────────────────────────────────────────
print("Creating demo user...")
user_pw = bcrypt.hashpw('demo1234'.encode(), bcrypt.gensalt()).decode()
demo_user = db.users.insert_one({
    'name': 'Priya',
    'email': 'priya@example.com',
    'password': user_pw,
    'role': 'job_seeker',
    'phone': '+91 9876543210',
    'location': 'Chennai',
    'skills': ['Python', 'Django', 'JavaScript', 'HTML', 'CSS', 'MongoDB'],
    'education': 'B.Sc Computer Science\nAnna University, 2026',
    'experience': 'Fresher — Academic projects and internships',
    'profile_info': 'Passionate fresher looking for opportunities in Python/Django development.',
    'resume': '',
    'auth_provider': 'local',
    'created_at': datetime.now(timezone.utc) - timedelta(days=30),
})
demo_uid = str(demo_user.inserted_id)

# ─── Create Companies ────────────────────────────────────────
print("Creating companies...")
companies_data = [
    {'name': 'ABC Technologies', 'industry': 'Information Technology', 'location': 'Chennai', 'website': 'https://abc-tech.example.com', 'description': 'A leading IT services company specializing in software development and cloud solutions.'},
    {'name': 'TCS', 'industry': 'Information Technology', 'location': 'Mumbai', 'website': 'https://tcs.com', 'description': 'Tata Consultancy Services is an Indian multinational IT services and consulting company.'},
    {'name': 'Infosys', 'industry': 'Information Technology', 'location': 'Bangalore', 'website': 'https://infosys.com', 'description': 'Infosys is a global leader in next-generation digital services and consulting.'},
    {'name': 'Wipro', 'industry': 'Information Technology', 'location': 'Bangalore', 'website': 'https://wipro.com', 'description': 'Wipro Limited is an Indian multinational corporation providing IT, consulting and business services.'},
    {'name': 'HCL Technologies', 'industry': 'Information Technology', 'location': 'Noida', 'website': 'https://hcltech.com', 'description': 'HCL Technologies is an Indian multinational IT services and consulting company.'},
    {'name': 'Zoho Corporation', 'industry': 'Software', 'location': 'Chennai', 'website': 'https://zoho.com', 'description': 'Zoho Corporation is an Indian multinational technology company making web-based business tools.'},
    {'name': 'Freshworks', 'industry': 'SaaS', 'location': 'Chennai', 'website': 'https://freshworks.com', 'description': 'Freshworks provides innovative SaaS solutions for businesses of all sizes.'},
    {'name': 'Cognizant', 'industry': 'Information Technology', 'location': 'Chennai', 'website': 'https://cognizant.com', 'description': 'Cognizant is a multinational IT services and consulting company.'},
]

comp_ids = {}
for c in companies_data:
    c['logo'] = ''
    c['created_at'] = datetime.now(timezone.utc)
    result = db.companies.insert_one(c)
    comp_ids[c['name']] = str(result.inserted_id)

# ─── Create Jobs ─────────────────────────────────────────────
print("Creating jobs...")
jobs_data = [
    {'title': 'Python Developer', 'company': 'ABC Technologies', 'location': 'Chennai', 'job_type': 'Full Time', 'experience': 'Fresher', 'salary': '4-6 LPA', 'skills': ['Python', 'Django', 'JavaScript', 'MongoDB'], 'description': 'We are looking for a Python Developer to join our growing team. You will be responsible for developing and maintaining web applications using Django and related technologies.\n\nKey responsibilities include writing clean, maintainable code, collaborating with the frontend team, and participating in code reviews.', 'requirements': 'B.Sc/B.Tech in Computer Science or related field\nGood understanding of Python and Django\nBasic knowledge of JavaScript and HTML/CSS\nFamiliarity with Git\nStrong problem-solving skills', 'application_url': 'https://abc-tech.example.com/careers/python-developer', 'deadline_days': 45},
    {'title': 'Software Engineer', 'company': 'TCS', 'location': 'Mumbai', 'job_type': 'Full Time', 'experience': 'Fresher', 'salary': '3.5-5 LPA', 'skills': ['Java', 'Python', 'SQL', 'Spring'], 'description': 'Join TCS as a Software Engineer and work on enterprise-grade applications for global clients. This role involves full-stack development with exposure to modern technologies.', 'requirements': 'BE/BTech/MCA from recognized university\nStrong programming fundamentals\nGood communication skills\nWillingness to relocate', 'application_url': 'https://tcs.com/careers', 'deadline_days': 30},
    {'title': 'Frontend Developer', 'company': 'Infosys', 'location': 'Bangalore', 'job_type': 'Full Time', 'experience': '1-2 Years', 'salary': '5-8 LPA', 'skills': ['JavaScript', 'React', 'HTML', 'CSS', 'TypeScript'], 'description': 'Infosys is looking for a Frontend Developer to create responsive, user-friendly web interfaces. You will work closely with UX designers and backend teams.', 'requirements': '1-2 years of frontend development experience\nProficiency in React.js and modern JavaScript\nExperience with responsive design\nKnowledge of TypeScript is a plus', 'application_url': 'https://infosys.com/careers', 'deadline_days': 21},
    {'title': 'Django Developer', 'company': 'Zoho Corporation', 'location': 'Chennai', 'job_type': 'Full Time', 'experience': 'Fresher', 'salary': '4.5-7 LPA', 'skills': ['Python', 'Django', 'REST API', 'PostgreSQL'], 'description': 'Join Zoho to build scalable web applications using Django. You will design RESTful APIs, implement business logic, and ensure code quality through testing.', 'requirements': 'Strong Python programming skills\nFamiliarity with Django REST Framework\nBasic understanding of databases (SQL/NoSQL)\nPassion for writing clean code', 'application_url': 'https://zoho.com/careers', 'deadline_days': 35},
    {'title': 'Full Stack Developer', 'company': 'Freshworks', 'location': 'Chennai', 'job_type': 'Full Time', 'experience': '1-2 Years', 'salary': '6-10 LPA', 'skills': ['JavaScript', 'Node.js', 'React', 'MongoDB', 'Python'], 'description': 'Freshworks is hiring a Full Stack Developer to build and maintain SaaS products. You will work across the stack, from designing APIs to crafting polished user interfaces.', 'requirements': '1-2 years of full stack development experience\nProficiency in JavaScript/TypeScript\nExperience with Node.js or Python backend\nKnowledge of React or Vue.js\nExperience with cloud deployments is a plus', 'application_url': 'https://freshworks.com/careers', 'deadline_days': 28},
    {'title': 'Backend Developer', 'company': 'Wipro', 'location': 'Bangalore', 'job_type': 'Full Time', 'experience': 'Fresher', 'salary': '3.5-5.5 LPA', 'skills': ['Java', 'Spring Boot', 'MySQL', 'REST API'], 'description': 'Work on large-scale enterprise applications as a Backend Developer at Wipro. This role involves designing microservices, writing APIs, and optimizing database queries.', 'requirements': 'BE/BTech in Computer Science\nGood knowledge of Java and Spring Boot\nUnderstanding of REST APIs and microservices\nFamiliarity with SQL databases', 'application_url': 'https://wipro.com/careers', 'deadline_days': 40},
    {'title': 'Data Analyst', 'company': 'Cognizant', 'location': 'Chennai', 'job_type': 'Full Time', 'experience': 'Fresher', 'salary': '4-6 LPA', 'skills': ['Python', 'SQL', 'Excel', 'Power BI', 'Statistics'], 'description': 'Cognizant is looking for a Data Analyst to analyze business data, create visualizations, and provide insights to stakeholders.', 'requirements': 'Degree in Statistics, Mathematics, or Computer Science\nProficiency in SQL and Python\nExperience with data visualization tools\nStrong analytical and communication skills', 'application_url': 'https://cognizant.com/careers', 'deadline_days': 25},
    {'title': 'DevOps Engineer', 'company': 'HCL Technologies', 'location': 'Noida', 'job_type': 'Full Time', 'experience': '1-2 Years', 'salary': '6-9 LPA', 'skills': ['Linux', 'Docker', 'Kubernetes', 'AWS', 'CI/CD'], 'description': 'Join HCL Technologies as a DevOps Engineer. You will be responsible for building and maintaining CI/CD pipelines, managing cloud infrastructure, and ensuring system reliability.', 'requirements': '1-2 years of DevOps experience\nHands-on experience with Docker and Kubernetes\nFamiliarity with AWS or Azure\nExperience with Jenkins, GitLab CI, or similar tools\nStrong Linux administration skills', 'application_url': 'https://hcltech.com/careers', 'deadline_days': 33},
    {'title': 'Mobile App Developer', 'company': 'Zoho Corporation', 'location': 'Chennai', 'job_type': 'Full Time', 'experience': '1-2 Years', 'salary': '5-8 LPA', 'skills': ['Flutter', 'Dart', 'Firebase', 'REST API'], 'description': 'Build cross-platform mobile applications for Zoho products using Flutter. You will work on features across Android and iOS platforms.', 'requirements': '1+ years of Flutter development experience\nExperience publishing apps on Play Store or App Store\nFamiliarity with Firebase and REST APIs\nGood UI/UX sensibility', 'application_url': 'https://zoho.com/careers', 'deadline_days': 20},
    {'title': 'Python Intern', 'company': 'ABC Technologies', 'location': 'Chennai', 'job_type': 'Internship', 'experience': 'Fresher', 'salary': '15,000/month', 'skills': ['Python', 'Django', 'HTML', 'CSS'], 'description': 'ABC Technologies is offering a 3-month Python internship for final year students. You will work on real projects under the guidance of senior developers.', 'requirements': 'Currently pursuing B.Sc/B.Tech in Computer Science\nBasic knowledge of Python\nEager to learn and grow\nGood communication skills', 'application_url': 'https://abc-tech.example.com/internships', 'deadline_days': 15},
]

job_ids = []
for j in jobs_data:
    comp_name = j.pop('company')
    deadline_days = j.pop('deadline_days')
    j['company_id'] = comp_ids.get(comp_name, '')
    j['company'] = comp_name
    j['deadline'] = datetime.now(timezone.utc) + timedelta(days=deadline_days)
    j['status'] = 'active'
    j['created_at'] = datetime.now(timezone.utc) - timedelta(days=max(0, 60 - deadline_days))
    result = db.jobs.insert_one(j)
    job_ids.append(str(result.inserted_id))

# ─── Create Demo Applications ────────────────────────────────
print("Creating demo applications...")
apps_data = [
    {'job_idx': 0, 'status': 'applied', 'days_ago': 3, 'notes': 'Applied through official company website.'},
    {'job_idx': 1, 'status': 'interview', 'days_ago': 7, 'notes': 'Received interview invitation via email.'},
    {'job_idx': 2, 'status': 'rejected', 'days_ago': 14, 'notes': 'Received rejection email.'},
    {'job_idx': 5, 'status': 'selected', 'days_ago': 21, 'notes': 'Received offer letter. Accepted.'},
]

app_ids = []
for a in apps_data:
    job = db.jobs.find_one({'_id': __import__('bson').ObjectId(job_ids[a['job_idx']])})
    result = db.applications.insert_one({
        'user_id': demo_uid,
        'job_id': job_ids[a['job_idx']],
        'company_id': job.get('company_id', '') if job else '',
        'applied_date': datetime.now(timezone.utc) - timedelta(days=a['days_ago']),
        'status': a['status'],
        'notes': a['notes'],
        'created_at': datetime.now(timezone.utc) - timedelta(days=a['days_ago']),
    })
    app_ids.append(str(result.inserted_id))

# ─── Create Demo Interviews ──────────────────────────────────
print("Creating demo interviews...")
db.interviews.insert_one({
    'application_id': app_ids[1],
    'user_id': demo_uid,
    'company': 'TCS',
    'role': 'Software Engineer',
    'date': datetime.now(timezone.utc) + timedelta(days=5),
    'time': '10:00 AM',
    'type': 'online',
    'meeting_link': 'https://meet.google.com/abc-defg-hij',
    'location': '',
    'notes': 'Prepare: Java fundamentals, OOP concepts, SQL queries, basic Spring Boot.',
    'created_at': datetime.now(timezone.utc) - timedelta(days=2),
})

# ─── Create Demo Notifications ───────────────────────────────
print("Creating demo notifications...")
notifications = [
    {'title': 'Interview Reminder', 'message': 'Your Software Engineer interview with TCS is in 5 days at 10:00 AM.', 'type': 'interview', 'is_read': False, 'days_ago': 0},
    {'title': 'Application Recorded', 'message': 'Your application for Python Developer at ABC Technologies has been recorded.', 'type': 'application', 'is_read': False, 'days_ago': 3},
    {'title': 'Application Update', 'message': 'Your application for Software Engineer at TCS has been moved to Interview.', 'type': 'application', 'is_read': True, 'days_ago': 5},
    {'title': 'New Job Available', 'message': 'A new Mobile App Developer position at Zoho Corporation has been added.', 'type': 'new_job', 'is_read': True, 'days_ago': 7},
    {'title': 'Application Update', 'message': 'Your application for Backend Developer at Wipro has been updated to Selected. Congratulations!', 'type': 'application', 'is_read': True, 'days_ago': 10},
]

for n in notifications:
    days = n.pop('days_ago')
    n['user_id'] = demo_uid
    n['created_at'] = datetime.now(timezone.utc) - timedelta(days=days)
    db.notifications.insert_one(n)

# ─── Create Saved Jobs ───────────────────────────────────────
print("Creating saved jobs...")
for idx in [3, 4, 8]:
    db.saved_jobs.insert_one({
        'user_id': demo_uid,
        'job_id': job_ids[idx],
        'saved_at': datetime.now(timezone.utc) - timedelta(days=idx),
    })

print("\n" + "="*50)
print("  SEED DATA CREATED SUCCESSFULLY")
print("="*50)
print(f"\n  Admin Login:")
print(f"    Email:    admin@jobtrack.com")
print(f"    Password: admin123")
print(f"\n  Demo User Login:")
print(f"    Email:    priya@example.com")
print(f"    Password: demo1234")
print(f"\n  Data Created:")
print(f"    Users:         2 (1 admin + 1 demo)")
print(f"    Companies:     {len(companies_data)}")
print(f"    Jobs:          {len(jobs_data)}")
print(f"    Applications:  {len(apps_data)}")
print(f"    Interviews:    1")
print(f"    Notifications: {len(notifications)}")
print(f"    Saved Jobs:    3")
print("="*50)
