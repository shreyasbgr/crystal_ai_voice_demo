# 🎙️ Voice AI Demo App (Crystal AI Generalist Task)

This project is a voice-based AI assistant that:
- Takes user voice input either by recording or by taking audio file input 🎤
- Transcribes it using OpenAI Whisper 🧠
- Generates a reply using GPT-3.5 💬
- Converts the reply to voice using OpenAI TTS 🔈
- Logs the interaction to a logs file and also into an Airtable Table 📝

Built using **FastAPI** and the **OpenAI API stack**.

---

## 🚀 How to Run (Local Dev)

```bash
# Step 1: Clone and setup
git clone https://github.com/shreyasbgr/crystal_ai_voice_demo.git
cd crystal_ai_voice_demo
python -m venv venv
# Mac:
source venv/bin/activate  
# Windows:
venv\Scripts\activate

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Run the app
uvicorn main:app --reload

# Open your browser
http://localhost:8000
