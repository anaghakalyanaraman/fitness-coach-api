# AI Fitness & Nutrition Coach API

A production-ready REST API that generates personalized workout plans, meal plans, and recipes using LLM APIs. Built with FastAPI, PostgreSQL, and Groq.

**Live API:** https://fitness-coach-api-8r2k.onrender.com/docs  
**Frontend:** https://fitness-coach-ui-qk6l.vercel.app  
**Demo:** [Watch Demo](https://www.youtube.com/watch?v=s2y2ual-MF0)

---

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL, SQLAlchemy ORM, Alembic migrations
- **AI:** Groq LLM API (llama-3.1-8b-instant), prompt engineering, structured JSON outputs
- **Auth:** JWT (python-jose), bcrypt
- **Deployment:** Render

---

## Features

- JWT Authentication (register, login, protected routes)
- User fitness profile (age, weight, height, goal, activity level)
- AI-generated personalized 7-day workout plans
- AI-generated meal plans from available ingredients
- AI-generated detailed recipes with instructions and nutrition info
- Conversational AI fitness coach with memory of conversation history
- Workout session logging (multiple exercises per session)
- Weight tracking over time
- Progress dashboard (total workouts, weight change, recent exercises)

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | /auth/register | Create account | No |
| POST | /auth/login | Get JWT token | No |
| POST | /profile | Create fitness profile | Yes |
| GET | /profile | Get current profile | Yes |
| PUT | /profile | Update profile | Yes |
| POST | /workout-plan | Generate AI workout plan | Yes |
| POST | /workout-plan/save | Save generated plan | Yes |
| POST | /nutrition/meal-plan | Generate meal plan from ingredients | Yes |
| POST | /nutrition/recipe | Generate detailed recipe | Yes |
| POST | /chat | Chat with AI fitness coach | Yes |
| POST | /logs | Log a workout session | Yes |
| GET | /logs | Get all workout logs | Yes |
| DELETE | /logs/{id} | Delete a log | Yes |
| POST | /weight-log | Log current weight | Yes |
| GET | /weight-log | Get weight history | Yes |
| GET | /progress | Get progress summary | Yes |

---

## Running Locally

```bash
git clone https://github.com/anaghakalyanaraman/fitness-coach-api
cd fitness-coach-api
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env
echo "SECRET_KEY=your_secret_key" >> .env

# Start PostgreSQL
docker run --name fitness-db -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=password -e POSTGRES_DB=fitnesscoach -p 5432:5432 -d postgres

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload
```

API docs at `http://localhost:8000/docs`
