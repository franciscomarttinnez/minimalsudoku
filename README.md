# 🧩 Sudoku Web App — Full Stack Project

A complete and modern Sudoku web application built with a **minimal full-stack architecture**, designed as a **strong portfolio project**.

The project focuses on **clarity, simplicity, clean code, and real backend logic**, avoiding unnecessary technologies or overengineering.

Deployed on Render: https://minimalsudoku.onrender.com
---

## ✨ Features
<img width="591" height="854" alt="image" src="https://github.com/user-attachments/assets/47e83e54-9bb3-4565-a132-874709d48bca" />

### 🎮 Game
- 9×9 Sudoku board with 3×3 visual blocks
- Valid and always solvable Sudoku generation
- Difficulty selector:
  - Easy
  - Medium
  - Hard
- Interactive number selector
- Real-time validation:
  - Rows
  - Columns
  - 3×3 blocks
- Maximum of **3 errors** per game
- Game Over and Win pop-ups
- Timer and error counter
- Scoring system:
  - Correct numbers
  - Completed rows / columns / blocks
  - Win bonus
  - Error penalties

---

### 👤 User System
- Register & Login with hashed passwords
- Session-based authentication (cookies)
- Persistent user data
- Individual game state per user

---

### 💾 Persistence
- Active game saving (Continue Game)
- User statistics stored in SQLite:
  - Games played
  - Games won
  - Win rate
  - Perfect wins
  - Best time
  - Best score
  - Total accumulated score

---

### 🎨 UI / UX
- Desktop-first design
- Fully responsive (tablet & mobile)
- Minimalist white & blue theme
- Gradient background
- Hover interactions on desktop
- Touch-friendly feedback on mobile
- Smooth button animations
- Centered layout without scroll

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3 (no frameworks)
- Vanilla JavaScript

### Backend
- Python
- Flask
- SQLite
- Cookie-based sessions

### Not Used (by design)
- No JavaScript frameworks
- No JWT
- No Firebase
- No ORMs
- No frontend libraries

---
## ▶️ How to Run Locally

1. Clone the repository

git clone https://github.com/your-username/minimalsudoku.git
cd sudoku-web-app

2. Create and activate a virtual environment (optional but recommended)

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

3. Install dependencies

Install dependencies

4. Run the application

python app.py

5. Open your browser at

http://127.0.0.1:5000


📌 Why This Project?

This project was built to demonstrate:

Clean full-stack architecture

Backend persistence without overengineering

Vanilla frontend logic

Real authentication flow

Thoughtful UX decisions

Maintainable and readable code

<img width="591" height="854" alt="image" src="https://github.com/user-attachments/assets/4ca38c10-e764-41dd-b337-c120b7fa2c6f" />
<img width="585" height="557" alt="image" src="https://github.com/user-attachments/assets/96d39ee0-99cb-4241-87b7-befa22f38470" />
<img width="600" height="764" alt="image" src="https://github.com/user-attachments/assets/c1bb0b6e-f034-4872-b4f6-f1bfac1a78d5" />



👨‍💻 Author

Francisco Martinez

Full-Stack Developer (Junior / Intermediate)


📄 License

This project is open-source and free to use for learning and portfolio purposes.
