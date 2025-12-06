AI Insurance Claim Processing System

AI-powered insurance claim automation with OCR, fraud detection, & reimbursement prediction using FastAPI + PostgreSQL + React + OpenRouter AI.

🚀 Features
Feature	Status
User & Admin Authentication	✔ JWT-based
Claim Upload with Bills/Reports	✔ Upload multiple images/PDFs
OCR Text Extraction	✔ pdfplumber + pytesseract
AI Claim Evaluation	✔ via OpenRouter API
Fraud/Mismatch Detection	✔ Policy & Data Validation
Confidence Score & Reimbursement Calculation	✔ Auto computed
Claim History Page	✔ User-wise
Admin Dashboard	✔ Approve/Reject Claims
Database Seeder	✔ Sample users + policies
File Upload Storage	✔ Stored locally /uploads/
🛠 Tech Stack
Backend

Python FastAPI

PostgreSQL + SQLAlchemy ORM

JWT Authentication

OCR (pytesseract + pdfplumber)

AI Analysis (OpenRouter)

Frontend

React + Vite/CRA (based on your folder)

shadcn UI Components

Axios API Integration

🔧 Backend Setup
1️⃣ Create Virtual Environment
cd app
python -m venv venv
venv\Scripts\activate

2️⃣ Install Requirements
pip install -r requirements.txt

3️⃣ Configure .env

Create .env in backend root:

DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/insurance_db
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=openai/gpt-4.1-nano
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

4️⃣ Start PostgreSQL
CREATE DATABASE insurance_db;

5️⃣ Seed Sample Data
python seed_data.py


You will get:

Admin: admin@insurance.com / admin123
User1: user1@example.com / password123

6️⃣ Run Backend
uvicorn server:app --reload


API Running at:

http://127.0.0.1:8000
Swagger Docs → http://127.0.0.1:8000/docs

🧾 Frontend Setup
cd frontend
npm install --legacy-peer-deps
npm run dev


Runs at:

http://localhost:5173  (Vite)
or
http://localhost:3000  (CRA)

Install Tesseract OCR manually:

Windows Download

https://github.com/UB-Mannheim/tesseract/wiki

After install, add to PATH environment:

C:\Program Files\Tesseract-OCR\tesseract.exe

Troubleshooting
Issue	Fix
Claim AI response defaulting	Add/OpenRouter API key
OCR extracting 0 text	Install tesseract correctly
psycopg2 error	Install psycopg2-binary
React dependency conflict	npm install --legacy-peer-deps
402 API Error	Reduce model or upgrade credits

To-Do Future Enhancements

Web dashboard analytics
Auto identify fraud pattern dataset training
Claim PDF structured parsing engine
Email/SMS notification on approval
