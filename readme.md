# **AutoStream: Autonomous AI Video Generation Pipeline**

**AutoStream** is an end-to-end engineered pipeline that converts a simple text prompt into a fully produced narrative video. Unlike simple model wrappers, this system orchestrates multiple AI agents (LLMs, TTS, Diffusion, ASR) to script, narrate, visualize, and edit video content autonomously.

🔗 **Live Demo:** [Hugging Face Space](https://huggingface.co/spaces/NexusAI4/TTV_App)

## **🏗 System Architecture**

The pipeline follows a modular micro-service architecture wrapped in a containerized environment. It decouples the generative logic from the video rendering engine to ensure scalability.

graph TD  
    User\[User Input\] \--\>|Topic & Style| Orchestrator\[App Orchestrator\]  
      
    subgraph "Content Generation Layer"  
        Orchestrator \--\>|Prompt| LLM\[LLM Service (Groq/Llama3)\]  
        LLM \--\>|Script| TTS\[TTS Service (EdgeTTS)\]  
        LLM \--\>|Visual Prompts| IMG\[Image Service (SDXL Flash)\]  
    end  
      
    subgraph "Processing Layer"  
        TTS \--\>|Audio| ASR\[WhisperX Alignment\]  
        ASR \--\>|Word Timestamps| Sync\[Synchronization Engine\]  
        IMG \--\>|Assets| Sync  
    end  
      
    subgraph "Rendering Layer"  
        Sync \--\>|Composition| MoviePy\[MoviePy Engine\]  
        MoviePy \--\>|Encoding| FFmpeg\[FFmpeg Optimization\]  
    end  
      
    FFmpeg \--\>|MP4 Video| Output\[Final Delivery\]

## **🚀 Key Engineering Features**

### **1\. High-Performance Inference & Latency Optimization**

* **LLM Engine:** Utilizes **Groq API** with Llama-3-70B to achieve sub-second script generation, significantly reducing the "Time to First Token."  
* **Visual Synthesis:** Implements **SDXL-Flash** via the Hugging Face Inference Client. This model was selected for its ability to generate high-fidelity images in \<8 steps, optimized for T4 GPU execution.  
* **Redundancy:** Includes a fallback image generation service (pollinations.py) to ensure pipeline stability if the primary inference API is rate-limited.

### **2\. Precise Audio-Visual Synchronization (Forced Alignment)**

* **Problem:** Standard TTS engines provide audio but lack precise timing data for subtitles.  
* **Solution:** The pipeline integrates **WhisperX** (OpenAI Whisper with Phoneme Alignment). It processes the generated audio to extract word-level timestamps, allowing for millisecond-precision subtitle burning that matches the speech perfectly.

### **3\. Production-Ready Infrastructure**

* **Dockerized Environment:** A custom Dockerfile handles complex OS-level dependencies (imagemagick, ghostscript, ffmpeg) often missing in standard Python environments.  
* **Policy Management:** Automates the configuration of ImageMagick security policies (policy.xml) to permit text rendering on Linux containers.  
* **Asset Management:** A dedicated MediaUtils class handles the downloading, verification, and caching of fonts and background music to prevent runtime IO errors.

## **📂 Project Structure**

/  
├── Dockerfile              \# Container definition with OS dependencies  
├── app.py                  \# Gradio UI & Application Entry Point  
├── services/               \# Microservices Logic  
│   ├── genai\_service.py    \# LLM Interaction (Groq)  
│   ├── speech\_service.py   \# TTS Generation (EdgeTTS)  
│   ├── video\_service.py    \# Video Compositing (MoviePy)  
│   ├── whisperx\_service.py \# Audio Alignment (WhisperX)  
│   └── ai\_image\_generator/ \# Pluggable Image Models  
│       ├── sdxl\_flash\_hf.py  
│       └── pollination.py  
├── utils/                  \# Helper Utilities  
│   ├── media\_utils.py      \# Asset download/verification  
│   └── file\_utils.py       \# IO operations  
├── fonts/                  \# Custom typography assets  
├── bg\_music/               \# Background audio tracks  
├── requirements.txt        \# Python dependencies (pinned)  
└── packages.txt            \# System dependencies (apt-get)

## **🛠️ Tech Stack**

| Component | Technology | Rationale |
| :---- | :---- | :---- |
| **Orchestration** | Python 3.10, Gradio | Rapid UI prototyping and async capability. |
| **Scripting** | Groq (Llama 3\) | Lowest latency LLM for real-time generation. |
| **Audio** | EdgeTTS | Natural sounding neural voices with zero latency. |
| **Alignment** | WhisperX | State-of-the-art forced alignment for accurate subtitles. |
| **Visuals** | SDXL Flash | High-speed diffusion models optimized for T4 GPUs. |
| **Editing** | MoviePy, FFmpeg | Programmatic non-linear editing (NLE). |

## **💻 Local Installation**

To run this pipeline locally, you must have ffmpeg and imagemagick installed on your system.

**1\. Clone the Repository**

git clone \[https://github.com/YourUsername/AutoStream.git\](https://github.com/YourUsername/AutoStream.git)  
cd AutoStream

**2\. System Dependencies (Ubuntu/Debian)**

sudo apt-get update && sudo apt-get install ffmpeg imagemagick ghostscript  
\# Fix ImageMagick policy for text rendering  
sudo sed \-i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml

**3\. Install Python Dependencies**

\# Recommended to use a virtual environment  
pip install \-r requirements.txt

4\. Environment Configuration  
Create a .env file in the root directory:  
HF\_TOKEN=your\_huggingface\_token\_here  
GROQ\_API\_KEY=your\_groq\_api\_key\_here

**5\. Run the App**

python app.py

## **🐳 Docker Deployment**

The recommended way to run the application to ensure all system dependencies are met.

\# Build the image  
docker build \-t autostream-app .

\# Run the container (Map port 7860\)  
docker run \-it \-p 7860:7860 \--env-file .env autostream-app

## **🔮 Future Roadmap**

* \[ \] **Vector Database Integration:** To allow RAG-based video generation from PDF documents.  
* \[ \] **Asynchronous Queueing:** Implementing Celery/Redis for handling concurrent user requests.  
* \[ \] **Multi-Speaker Support:** Diarization to assign different AI voices to different characters in the script.

### **Author**

**Shubhankar Rawat** *AI Engineer & Researcher* [LinkedIn]([https://www.google.com/search?q=https://linkedin.com/in/shubhankar-rawat](https://www.linkedin.com/in/shubhankarrawat/?originalSubdomain=au))
