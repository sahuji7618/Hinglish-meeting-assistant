🎙️ Open Meeting AI

> **Free, Privacy-First AI Meeting Assistant for English, Hindi & Hinglish**

Say goodbye to $20/month subscriptions for Otter.ai or Fireflies. **Open Meeting AI** is a fully open-source, locally run meeting assistant that transcribes audio/video, generates structured meeting notes, extracts action items, and lets you chat with your meeting transcripts using Retrieval-Augmented Generation (RAG).

---

## ✨ Features

- 📹 **Flexible Input:** Load meetings directly via YouTube URL or local file upload (`.mp3`, `.wav`, `.mp4`, `.m4a`).
- 🗣️ **Multilingual Transcription:**
  - Fast English transcription via **Groq Whisper API**.
  - Industry-leading Hindi & Hinglish (code-switched) transcription via **Sarvam AI**.
- 📋 **Automated Extraction:**
  - Comprehensive meeting summary.
  - Action items complete with owner and target deadline.
  - Key decisions made during the call.
  - Unresolved questions and follow-ups.
- 💬 **Interactive RAG Chat:** Chat directly with your transcript using local vector search (**ChromaDB**) to retrieve specific context.
- 📄 **Export Options:** Download full reports as plain `.txt` or styled `.pdf` documents.
- 💰 **100% Free Stack:** Leverages generous free API tiers and local execution.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **UI Framework** | Streamlit |
| **Transcription (English)** | Groq Whisper API |
| **Transcription (Hindi/Hinglish)** | Sarvam AI API |
| **LLM & Orchestration** | LangChain (LCEL) + Mistral AI API |
| **Vector DB (RAG)** | ChromaDB |
| **Embeddings** | HuggingFace Inference API (`all-MiniLM-L6-v2`) |


## 🚀 Quick Start

### 1. Prerequisites
Ensure you have Python 3.10 or higher installed, along with `ffmpeg` for audio processing.

bash
# On macOS
brew install ffmpeg

# On Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg 

### 2. Clone the Repository
git clone [https://github.com/YOUR_USERNAME/open-meeting-ai.git](https://github.com/YOUR_USERNAME/open-meeting-ai.git)
cd open-meeting-ai

### 3. Create Virtual Environment & Install Dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

### 4. Set Up Environment Variables
GROQ_API_KEY=your_groq_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here

### 5. Run the Application
streamlit run app.py
