import os
import shutil
from dotenv import load_dotenv

load_dotenv()

class Config:
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    SECRET_KEY = os.getenv("SECRET_KEY", "codeverse-ai-secret-key-2026-cpp-mentor")

    # AI API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()

    # Determine Provider
    # Priority: GEMINI > OPENAI > OFFLINE_DEMO
    if GEMINI_API_KEY:
        AI_PROVIDER = "gemini"
    elif OPENAI_API_KEY:
        AI_PROVIDER = "openai"
    else:
        AI_PROVIDER = "offline_demo"

    # C++ Compiler & Code Execution Settings
    # Path to local g++, clang++, or cl.exe
    CPP_COMPILER_PATH = os.getenv("CPP_COMPILER_PATH", "").strip()
    if not CPP_COMPILER_PATH:
        # Auto-discover local compiler in PATH
        for compiler in ["g++", "clang++", "cl"]:
            found = shutil.which(compiler)
            if found:
                CPP_COMPILER_PATH = found
                break

    EXECUTION_TIMEOUT = int(os.getenv("EXECUTION_TIMEOUT", 5)) # seconds
    COMPILER_API_URL = os.getenv("COMPILER_API_URL", "").strip()
    COMPILER_API_KEY = os.getenv("COMPILER_API_KEY", "").strip()

    # Chat & Security settings
    MAX_PROMPT_LENGTH = 4000
    SYSTEM_NAME = "CodeVerse AI"
    TAGLINE = "Explore C++. Think Like a Programmer."
