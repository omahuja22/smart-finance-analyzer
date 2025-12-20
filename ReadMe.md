# 💰 Smart Personal Finance Analyzer

A full-stack FinTech web application that helps users track expenses, analyze spending behavior, manage budgets, and gain financial insights using data analytics and machine learning.

Designed with real-world finance use cases in mind, this project demonstrates backend engineering, data processing, and ML integration in a production-style application.

---

## 🚀 Features

### 🔐 Authentication
- User registration and login
- Secure session management using Flask-Login

### 🧾 Expense Management
- Add expenses manually
- Automatic expense category prediction using ML
- Delete expenses securely (user-specific)

### 📊 Visual Analytics
- Category-wise spending (Pie Chart)
- Daily spending trend (Line Chart)
- Monthly spending trend (Bar Chart)

### 📥 CSV Import & Export
- Upload bank statements in CSV format
- Automatic categorization on CSV upload
- Export expenses as a downloadable CSV report

### 📅 Smart Budgeting
- Set category-wise monthly budgets
- Automatic monthly budget reset
- Budget usage visualization with progress bars
- Delete budget categories when not required

### 🧠 Financial Intelligence
- Savings prediction based on income and spending
- Financial health score
- Anomaly detection for unusual spending spikes

### 🧮 Financial Summary
- Monthly income
- Total spending
- Net savings
- Savings rate percentage

---

## 🧠 Machine Learning
- Text-based expense categorization
- Trained on real-world expense descriptions
- Model serialized using `pickle`
- Integrated directly into the Flask backend

---

## 🛠 Tech Stack

**Backend**
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login

**Database**
- SQLite (stored safely in instance folder)

**Machine Learning**
- scikit-learn
- pandas
- pickle

**Frontend**
- HTML5
- Bootstrap 5
- Chart.js

---

## 🏗 Project Structure

smart-finance-analyzer/
│
├── app.py
├── models.py
├── extensions.py
├── expense_model.pkl
├── instance/
│ └── finance.db
├── ml/
│ └── savings_predictor.py
├── templates/
│ ├── base.html
│ ├── landing.html
│ ├── login.html
│ ├── register.html
│ └── dashboard.html
├── static/
│ └── css/
├── requirements.txt
└── README.md

---

## ⚙️ Local Setup

```bash
git clone https://github.com/omahuja22/smart-finance-analyzer.git
cd smart-finance-analyzer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py

Open browser at:

http://127.0.0.1:5000

📈 Use Cases
Students managing monthly expenses
Working professionals tracking spending habits
Budget planning and financial awareness
FinTech / Data Science portfolio project

📌 Future Enhancements

PDF monthly reports

Yearly analytics dashboard

Expense insights engine

Cloud database (PostgreSQL)

👤 Author

Om
Engineering Student (AI & ML)
Interested in FinTech, Data Science & Backend Engineering

