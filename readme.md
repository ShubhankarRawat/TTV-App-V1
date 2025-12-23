# AutoStream: Autonomous AI Video Generation Pipeline

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python)
![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED?logo=docker)
![Hugging Face](https://img.shields.io/badge/Cloud-Hugging%20Face%20Spaces-FFD21E?logo=huggingface)
![FFmpeg](https://img.shields.io/badge/Media-FFmpeg-007808?logo=ffmpeg)
![Status](https://img.shields.io/badge/Status-Production-success)

**AutoStream** is an end-to-end engineered pipeline that converts a simple text prompt into a fully produced narrative video. Unlike simple model wrappers, this system orchestrates multiple AI agents (LLMs, TTS, Diffusion, ASR) to script, narrate, visualize, and edit video content autonomously.

🔗 **Live Demo:** [Hugging Face Space](https://huggingface.co/spaces/NexusAI4/TTV_App)

---

## 🏗 System Architecture

The pipeline follows a modular micro-service architecture wrapped in a containerized environment:

```mermaid
graph TD
    User[User Input] -->|Topic & Style| Orchestrator[App Orchestrator]
    
    subgraph "Content Generation Layer"
        Orchestrator -->|Prompt| LLM[LLM Service (Groq/Llama3)]
        LLM -->|Script| TTS[TTS Service (EdgeTTS)]
        LLM -->|Visual Prompts| IMG[Image Service (SDXL Flash)]
    end
    
    subgraph "Processing Layer"
        TTS -->|Audio| ASR[WhisperX Alignment]
        ASR -->|Word Timestamps| Sync[Synchronization Engine]
        IMG -->|Assets| Sync
    end
    
    subgraph "Rendering Layer"
        Sync -->|Composition| MoviePy[MoviePy Engine]
        MoviePy -->|Encoding| FFmpeg[FFmpeg Optimization]
    end
    
    FFmpeg -->|MP4 Video| Output[Final Delivery]
🚀 Key Engineering Features1. High-Performance InferenceLLM Engine: Utilizes Groq API with Llama-3-70B for sub-second script generation.Visuals: Implements SDXL-Flash via Hugging Face Inference Client for rapid image synthesis (steps < 8).2. Precise Audio-Visual SynchronizationInstead of static timing, the system uses WhisperX (Forced Alignment) to generate word-level timestamps from the generated audio.Subtitles are dynamically generated and burned into the video frames with millisecond precision.3. Production-Ready InfrastructureContainerization: Fully Dockerized environment handling complex OS-level dependencies (imagemagick, ghostscript, ffmpeg).Font & Asset Management: Automated asset verification and font loading to prevent rendering runtime errors in Linux environments.Fail-Safe Processing: Implements redundant image generation strategies (Pollinations.ai fallback).🛠️ Tech StackComponentTechnologyRationaleOrchestrationPython 3.10, GradioRapid UI prototyping and async capability.ScriptingGroq (Llama 3)Lowest latency LLM for real-time generation.AudioEdgeTTSNatural sounding neural voices with zero latency.AlignmentWhisperXState-of-the-art forced alignment for accurate subtitles.VisualsSDXL Flash / PollinationsHigh-speed diffusion models optimized for T4 GPUs.EditingMoviePy, FFmpegProgrammatic non-linear editing (NLE).💻 Local InstallationTo run this pipeline locally, you must have ffmpeg and imagemagick installed on your system.1. Clone the RepositoryBashgit clone [https://github.com/YourUsername/AutoStream.git](https://github.com/YourUsername/AutoStream.git)
cd AutoStream
2. System Dependencies (Ubuntu/Debian)Bashsudo apt-get update && sudo apt-get install ffmpeg imagemagick ghostscript
# Fix ImageMagick policy for text rendering
sudo sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml
3. Install Python DependenciesBash# Recommended to use a virtual environment
pip install -r requirements.txt
4. Environment ConfigurationCreate a .env file or export variables:Bashexport OPENAI_API_KEY="your_key"  # If using OpenAI fallback
export HF_TOKEN="your_hf_token"   # Required for SDXL Inference
export GROQ_API_KEY="your_groq_key"
5. Run the AppBashpython app.py
🐳 Docker DeploymentThe recommended way to run the application to ensure all system dependencies are met.Bash# Build the image
docker build -t autostream-app .

# Run the container (Map port 7860)
docker run -it -p 7860:7860 --env-file .env autostream-app
🔮 Future Roadmap[ ] Vector Database Integration: To allow RAG-based video generation from PDF documents.[ ] Asynchronous Queueing: Implementing Celery/Redis for handling concurrent user requests.[ ] Multi-Speaker Support: Diarization to assign different AI voices to different characters in the script.AuthorShubhankar Rawat AI Engineer & Researcher LinkedIn | Portfolio
