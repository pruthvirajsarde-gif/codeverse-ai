import os
import json
import time
import requests
from typing import Generator, Dict, Any, List
from config import Config
from services.offline_engine import OfflineEngine, OUT_OF_SCOPE_REFUSAL

SYSTEM_INSTRUCTION = """
You are CodeVerse AI, an elite, professional, and friendly C++ programming mentor built exclusively for computer engineering students and developers.

STRICT TOPIC ENFORCEMENT - C++ ONLY:
You must answer questions ONLY related to C++ programming, computer science concepts implemented in C++, syntax, algorithms, data structures, object-oriented programming (OOP), standard library (STL), modern C++ (C++11, 14, 17, 20, 23), debugging, and viva/oral exam questions.

IF OUT-OF-SCOPE:
If the user asks about ANYTHING outside C++ (e.g. cricket, politics, weather, recipes, movies, personal advice, or other programming languages like Python, Java, JavaScript, Rust UNLESS specifically comparing a C++ feature to them), you MUST POLITELY REFUSE and redirect them with the following response:
"I’m CodeVerse AI, your dedicated C++ programming assistant! 💻 I can help you with C++ concepts, programs, debugging, algorithms, and output prediction. Please ask me a C++-related question, and let’s code together!"

CRITICAL PEDAGOGICAL INSTRUCTION — STRICTLY BALANCING THEORY AND CODE:
1. NEVER GENERATE ONLY RAW CODE WITHOUT THEORY:
   - Unless the user explicitly says "only code no explanation", NEVER just output raw code without theoretical explanations.
   - Every program must be grounded with clear conceptual explanations, memory models (stack vs heap), and design principles.

2. WHEN USER SAYS "GIVE THEORY", "EXPLAIN THEORY", "THEORY OF...", OR ASKS FOR CONCEPTUAL EXPLANATION:
   - Prioritize in-depth, academic, high-yield **THEORY**:
     a. 💡 Formal Academic Definition & Core Concept
     b. 🧠 In-Depth Theoretical Background (Under-the-hood memory model, stack vs heap, hardware architecture, CPU registers, vtables, pointer mechanics)
     c. ⚙️ Working Principles & Mechanism (Step-by-step logic, lifecycle of objects, control flow)
     d. 📊 Structural Diagram or ASCII/Markdown Representation (Memory layout, pointer indirection, inheritance tree)
     e. ⚖️ Advantages, Disadvantages & Engineering Trade-offs
     f. ⚠️ Important Notes, Pitfalls & Common Mistakes (Undefined behavior, memory leaks, dangling pointers)
     g. 🎓 Viva / Technical Interview Questions related to this theory
     h. Short, compact illustrative C++ code snippet (only to support the theoretical explanation).

3. WHEN USER SAYS "GIVE CODE", "GENERATE CODE", "WRITE PROGRAM", "CODE FOR...", OR ASKS FOR IMPLEMENTATION:
   - Provide a complete, production-ready, compilable **C++ CODE SOLUTION**:
     a. 💻 Full, Standard-Compliant C++ Program (includes `#include` headers, namespace, detailed comments)
     b. 🖥️ Expected Output
     c. 🔍 Step-by-Step Code Walkthrough (explaining critical lines and logic)
     d. ⏱️ Time and Space Complexity Analysis (Big-O notation)
     e. 🛠️ Compilation Command (e.g., `g++ -std=c++17 -O2 main.cpp`)

4. WHEN USER ASKS GENERAL OR MIXED QUESTIONS (e.g., "Pointers in C++", "What is Polymorphism?"):
   - Provide a balanced masterclass: Start with rich, comprehensive **Theory & Conceptual Breakdown**, followed by the **Compilable Modern C++ Code Example**, **Expected Output**, **Line-by-Line Explanation**, **Common Pitfalls**, and **Practice Challenge**.
""".strip()

class AIService:
    @staticmethod
    def get_provider_status() -> Dict[str, Any]:
        """Returns details about the configured AI provider."""
        provider = Config.AI_PROVIDER
        has_gemini = bool(Config.GEMINI_API_KEY)
        has_openai = bool(Config.OPENAI_API_KEY)

        return {
            "provider": provider,
            "has_gemini": has_gemini,
            "has_openai": has_openai,
            "is_live_api": provider in ("gemini", "openai"),
            "model": Config.GEMINI_MODEL if provider == "gemini" else (Config.OPENAI_MODEL if provider == "openai" else "CodeVerse Offline C++ Intelligence Engine"),
            "demo_mode": provider == "offline_demo",
            "message": "Live AI API Active" if provider in ("gemini", "openai") else "Running in Smart Offline C++ Mode (Enter API Key in .env for live Gemini/OpenAI models)"
        }

    @staticmethod
    def stream_chat(messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Streams AI response token-by-token using Server-Sent Events (SSE).
        Yields JSON strings: {"chunk": "...", "done": false} and finally {"done": true}.
        """
        if not messages:
            yield json.dumps({"chunk": "No message provided.", "done": True}) + "\n\n"
            return

        latest_user_message = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                latest_user_message = m.get("content", "")
                break

        # Fast server-side guard for out-of-scope queries
        if OfflineEngine.is_out_of_scope(latest_user_message):
            for token in OUT_OF_SCOPE_REFUSAL.split(" "):
                yield json.dumps({"chunk": token + " ", "done": False}) + "\n\n"
                time.sleep(0.02)
            yield json.dumps({"done": True, "provider": "guard"}) + "\n\n"
            return

        provider = Config.AI_PROVIDER

        # 1. Google Gemini Streaming
        if provider == "gemini" and Config.GEMINI_API_KEY:
            try:
                yield from AIService._stream_gemini(messages)
                return
            except Exception as e:
                # If Gemini fails (e.g. invalid key or network error), yield a graceful warning and fallback
                yield json.dumps({
                    "chunk": f"\n\n> ⚠️ *Live Gemini API notice: {str(e)[:150]}. Falling back to CodeVerse Offline C++ Engine.*\n\n",
                    "done": False
                }) + "\n\n"
                yield from AIService._stream_offline(latest_user_message)
                return

        # 2. OpenAI Streaming
        if provider == "openai" and Config.OPENAI_API_KEY:
            try:
                yield from AIService._stream_openai(messages)
                return
            except Exception as e:
                yield json.dumps({
                    "chunk": f"\n\n> ⚠️ *Live OpenAI API notice: {str(e)[:150]}. Falling back to CodeVerse Offline C++ Engine.*\n\n",
                    "done": False
                }) + "\n\n"
                yield from AIService._stream_offline(latest_user_message)
                return

        # 3. Default: High Quality Offline Engine
        yield from AIService._stream_offline(latest_user_message)

    @staticmethod
    def _stream_gemini(messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Streams response from Google Gemini API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{Config.GEMINI_MODEL}:streamGenerateContent?key={Config.GEMINI_API_KEY}&alt=sse"

        # Format contents for Gemini
        contents = []
        for msg in messages:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}]
            })

        payload = {
            "systemInstruction": {
                "parts": [{"text": SYSTEM_INSTRUCTION}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 3000
            }
        }

        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=30
        )

        if response.status_code != 200:
            raise RuntimeError(f"Gemini API error ({response.status_code}): {response.text[:200]}")

        for line in response.iter_lines(decode_unicode=True):
            if line:
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for part in parts:
                                text = part.get("text", "")
                                if text:
                                    yield json.dumps({"chunk": text, "done": False}) + "\n\n"
                    except Exception:
                        pass

        yield json.dumps({"done": True, "provider": "gemini"}) + "\n\n"

    @staticmethod
    def _stream_openai(messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Streams response from OpenAI or OpenAI-compatible endpoint."""
        url = f"{Config.OPENAI_BASE_URL.rstrip('/')}/chat/completions"

        formatted_messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
        for msg in messages:
            formatted_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.OPENAI_API_KEY}"
        }

        payload = {
            "model": Config.OPENAI_MODEL,
            "messages": formatted_messages,
            "stream": True,
            "temperature": 0.3
        }

        response = requests.post(url, json=payload, headers=headers, stream=True, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"OpenAI API error ({response.status_code}): {response.text[:200]}")

        for line in response.iter_lines(decode_unicode=True):
            if line:
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        choices = data.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield json.dumps({"chunk": content, "done": False}) + "\n\n"
                    except Exception:
                        pass

        yield json.dumps({"done": True, "provider": "openai"}) + "\n\n"

    @staticmethod
    def _stream_offline(query: str) -> Generator[str, None, None]:
        """Streams response from the offline C++ engine chunk by chunk."""
        full_text = OfflineEngine.generate_response(query)

        # Break text into realistic tokens/words to simulate genuine typing streaming
        tokens = full_text.split(" ")
        for i, token in enumerate(tokens):
            chunk = token + (" " if i < len(tokens) - 1 else "")
            yield json.dumps({"chunk": chunk, "done": False}) + "\n\n"
            # Micro delay for typing effect
            if len(chunk) > 1:
                time.sleep(0.015)

        yield json.dumps({"done": True, "provider": "offline_engine"}) + "\n\n"
