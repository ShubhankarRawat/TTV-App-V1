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

The pipeline follows a modular micro-service architecture wrapped in a containerized environment. It decouples the generative logic from the video rendering engine to ensure scalability.

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
