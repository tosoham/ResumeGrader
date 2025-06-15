
ResumeGrader is a simple, fast, and AI-powered resume evaluation tool. It allows users to upload their resumes in PDF format and instantly receive grading, analysis, and constructive feedback — all powered by cutting-edge AI.

Built as a hackathon project, ResumeGrader combines modern backend, AI models, and a sleek frontend to deliver quick insights on resume quality.

---

## 🚀 Features

- 📄 PDF Upload — Upload your resume directly via an intuitive interface.
- 🔍 AI-Powered Parsing — Resumes are parsed and analyzed using Sarvam AI models.
- 🎯 Grading System — The AI provides a score based on resume quality, structure, and content.
- 📝 Feedback Generator — Get actionable suggestions to improve your resume.
- ☁️ File Storage — Uploaded files are securely stored for processing.
- ⚡ Fast API Response — Near-instant results via optimized backend processing.

---

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI — REST API server
- Node.js — Auxiliary backend logic and file handling
- Sarvam AI — Resume parsing, grading, and feedback generation
- Render — Backend deployment

### Frontend
- Next.js — Frontend framework (React-based)
- Vercel — Frontend deployment

### Others
- PDF Handling — Parsing and processing uploaded resumes

---

## 🌐 Architecture Overview

1️⃣ User uploads PDF via the Next.js frontend  
2️⃣ Request is sent to the FastAPI backend hosted on Render  
3️⃣ Backend parses the PDF, sends content to Sarvam AI for grading and feedback  
4️⃣ Sarvam AI returns the score and suggestions  
5️⃣ Frontend displays the grade and feedback to the user

---

## 📦 Deployment

- Frontend: Vercel
- Backend: Render
- Both are connected via API calls using FastAPI endpoints.

---

## 🔧 Setup (For Local Development)

### Clone the repository

```bash
git clone https://github.com/your-username/ResumeGrader.git
cd ResumeGrader
```

### Backend (Python + FastAPI)
```bash
Copy
Edit
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
### Frontend (Next.js)
```bash
Copy
Edit
cd frontend
npm install
npm run dev
```
### Environment Variables
Create a .env file for your environment variables:
```bash
export SARVAM_API_KEY=your_sarvam_ai_api_key
export STORAGE_PATH=/path/to/storage
```