# 🎙️ Voice AI Demo App (Crystal AI Generalist Task)

## 🌐 Try the Live App

You can access the deployed Voice AI assistant here:

🔗 [https://crystalai.shreyasbanagar.com](https://crystalai.shreyasbanagar.com)  
🔗 [https://crystal-ai-voice-demo.fly.dev](https://crystal-ai-voice-demo.fly.dev)

## 📊 Airtable Logs

View the log of all voice interactions here (Read-Only):

🔗 [https://airtable.com/appz2zdydPRfjnn4K/shrj3sQoryJT60hcI](https://airtable.com/appz2zdydPRfjnn4K/shrj3sQoryJT60hcI)

---

## 🧠 What This App Does

This project is a voice-based AI assistant that:

- 🎤 Takes user voice input  
- ✍️ Transcribes it using **OpenAI Whisper**  
- 💬 Generates a reply using **GPT-3.5**  
- 🔈 Converts the reply to voice using **OpenAI TTS**  
- 📝 Logs the conversation to both a log file and **Airtable**

Built using **FastAPI** and the **OpenAI API stack**.

---

# Run the app locally

## 🚀 Option 1: Run using local development

```bash
# 1. Clone and setup virtual environment
git clone https://github.com/shreyasbgr/crystal_ai_voice_demo.git
cd crystal_ai_voice_demo
python -m venv venv

# Activate the virtual environment
# For Mac/Linux:
source venv/bin/activate

# For Windows:
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
# Create a .env file using the provided .env.example and fill in:
# - OPENAI_API_KEY
# - AIRTABLE_API_KEY
# - AIRTABLE_BASE_ID
# - AIRTABLE_TABLE_NAME

# 4. Run the FastAPI app
uvicorn main:app --reload

# Open in browser
http://localhost:8000
```

## Option 2: Run with Docker Container
```bash
# Build Docker image
docker build -t voice-ai-app .

# Create .env file from .env.example file
Copy the contents of .env.example into .env file and fill the contents with the required API keys

# Run the container with your environment variables
docker run --env-file .env -p 8000:8000 voice-ai-app

# Open in browser
http://localhost:8000
```