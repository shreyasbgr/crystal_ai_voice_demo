# 🎙️ Voice AI Demo App (Crystal AI Generalist Task)

This project is a voice-based AI assistant that:
- Takes user voice input 🎤
- Transcribes it using OpenAI Whisper 🧠
- Generates a reply using GPT-4 💬
- Converts the reply to voice using OpenAI TTS 🔈
- Logs the interaction to Airtable or Google Sheets 📝

Built using **FastAPI** and the **OpenAI API stack**.

---

## 🚀 How to Run (Local Dev)

```bash
# Step 1: Clone and setup
git clone https://github.com/yourname/voice-ai-demo.git
cd voice-ai-demo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Run the app
uvicorn app.main:app --reload

# Open your browser
http://127.0.0.1:8000
