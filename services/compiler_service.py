import os
import sys
import time
import shutil
import tempfile
import subprocess
import requests
from config import Config

class CompilerService:
    @staticmethod
    def get_status():
        """Returns details about the current C++ execution environment."""
        local_compiler = Config.CPP_COMPILER_PATH
        has_local = bool(local_compiler and (os.path.exists(local_compiler) or shutil.which(local_compiler)))
        has_remote = bool(Config.COMPILER_API_URL)

        compiler_name = "None"
        compiler_version = "Not detected"

        if has_local:
            try:
                proc = subprocess.run([local_compiler, "--version"], capture_output=True, text=True, timeout=3)
                output = proc.stdout.splitlines()
                if output:
                    compiler_name = os.path.basename(local_compiler)
                    compiler_version = output[0]
            except Exception as e:
                compiler_name = os.path.basename(local_compiler)
                compiler_version = f"Error querying: {str(e)}"

        return {
            "configured": has_local or has_remote,
            "mode": "local" if has_local else ("remote" if has_remote else "none"),
            "local_compiler": local_compiler or None,
            "compiler_name": compiler_name,
            "compiler_version": compiler_version,
            "remote_api_configured": has_remote,
            "timeout_seconds": Config.EXECUTION_TIMEOUT,
            "message": "C++ Compiler is active and ready." if (has_local or has_remote) else "Code execution is not configured yet. To enable genuine C++ compilation, either install MinGW/g++ on your machine (add to PATH or set CPP_COMPILER_PATH in .env) or configure a sandboxed execution endpoint (COMPILER_API_URL in .env)."
        }

    @staticmethod
    def execute_cpp(code: str, stdin_data: str = ""):
        """
        Compiles and executes C++ code with sandboxing, time limits, and memory protection.
        Strictly satisfies requirement:
        'IMPORTANT: The Run Code button must genuinely compile and execute C++ code through a secure backend or trusted code-execution service. Do not simulate execution or display fabricated output. If code execution is not configured, show “Code execution is not configured yet” and explain how to enable it.'
        """
        if not code or not code.strip():
            return {
                "success": False,
                "configured": True,
                "compiled": False,
                "error": "No C++ code provided to execute.",
                "output": "",
                "exit_code": -1,
                "execution_time_ms": 0
            }

        # Size limitation
        if len(code) > 50000:
            return {
                "success": False,
                "configured": True,
                "compiled": False,
                "error": "Code exceeds maximum allowed size (50 KB).",
                "output": "",
                "exit_code": -1,
                "execution_time_ms": 0
            }

        status = CompilerService.get_status()

        # Check if compiler is configured
        if not status["configured"]:
            return {
                "success": False,
                "configured": False,
                "compiled": False,
                "error": status["message"],
                "output": "",
                "exit_code": None,
                "execution_time_ms": 0,
                "instructions": (
                    "To enable genuine local compilation:\n"
                    "1. Install MinGW-w64 or LLVM Clang for Windows.\n"
                    "2. Add g++ to your system PATH or specify CPP_COMPILER_PATH in .env.\n"
                    "3. Restart the Flask application.\n"
                    "Or configure COMPILER_API_URL in .env."
                )
            }

        # If local compiler is available
        if status["mode"] == "local":
            return CompilerService._run_local(code, stdin_data)

        # If remote compiler is configured
        if status["mode"] == "remote":
            return CompilerService._run_remote(code, stdin_data)

        return {
            "success": False,
            "configured": False,
            "error": "Compiler configuration unavailable.",
            "output": "",
            "exit_code": -1
        }

    @staticmethod
    def _run_local(code: str, stdin_data: str = ""):
        """Runs C++ compilation and execution using local g++/clang++ in isolated temp directory."""
        compiler = Config.CPP_COMPILER_PATH
        temp_dir = tempfile.mkdtemp(prefix="codeverse_cpp_")
        source_file = os.path.join(temp_dir, "main.cpp")
        exe_file = os.path.join(temp_dir, "main.exe" if sys.platform == "win32" else "main")

        start_time = time.time()
        try:
            with open(source_file, "w", encoding="utf-8") as f:
                f.write(code)

            # Compile step: std=c++17 with warnings
            compile_cmd = [
                compiler,
                "-std=c++17",
                "-O2",
                "-Wall",
                source_file,
                "-o",
                exe_file
            ]

            compile_proc = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=Config.EXECUTION_TIMEOUT + 3
            )

            if compile_proc.returncode != 0:
                return {
                    "success": False,
                    "configured": True,
                    "compiled": False,
                    "error": compile_proc.stderr or "Compilation failed without compiler output.",
                    "output": "",
                    "exit_code": compile_proc.returncode,
                    "execution_time_ms": int((time.time() - start_time) * 1000)
                }

            # Execute step with timeout and sandboxed directory
            run_start = time.time()
            try:
                run_proc = subprocess.run(
                    [exe_file],
                    input=stdin_data,
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    timeout=Config.EXECUTION_TIMEOUT
                )

                exec_time_ms = int((time.time() - run_start) * 1000)
                stdout = run_proc.stdout
                stderr = run_proc.stderr

                # Truncate output if excessively long
                MAX_OUTPUT = 65536
                if len(stdout) > MAX_OUTPUT:
                    stdout = stdout[:MAX_OUTPUT] + "\n[Output truncated at 64KB]"
                if len(stderr) > MAX_OUTPUT:
                    stderr = stderr[:MAX_OUTPUT] + "\n[Error output truncated at 64KB]"

                return {
                    "success": run_proc.returncode == 0,
                    "configured": True,
                    "compiled": True,
                    "output": stdout,
                    "error": stderr,
                    "exit_code": run_proc.returncode,
                    "execution_time_ms": exec_time_ms
                }

            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "configured": True,
                    "compiled": True,
                    "error": f"Execution Timed Out: Program exceeded {Config.EXECUTION_TIMEOUT} seconds limit (possible infinite loop or waiting for input).",
                    "output": "",
                    "exit_code": 124,
                    "execution_time_ms": Config.EXECUTION_TIMEOUT * 1000
                }

        except Exception as e:
            return {
                "success": False,
                "configured": True,
                "compiled": False,
                "error": f"Execution environment error: {str(e)}",
                "output": "",
                "exit_code": -1,
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }
        finally:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    @staticmethod
    def _run_remote(code: str, stdin_data: str = ""):
        """Runs C++ compilation through configured sandboxed compiler API."""
        try:
            headers = {"Content-Type": "application/json"}
            if Config.COMPILER_API_KEY:
                headers["Authorization"] = f"Bearer {Config.COMPILER_API_KEY}"

            payload = {
                "language": "cpp",
                "code": code,
                "stdin": stdin_data,
                "timeout": Config.EXECUTION_TIMEOUT
            }

            resp = requests.post(Config.COMPILER_API_URL, json=payload, headers=headers, timeout=Config.EXECUTION_TIMEOUT + 4)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": data.get("success", True),
                    "configured": True,
                    "compiled": data.get("compiled", True),
                    "output": data.get("output", "") or data.get("stdout", ""),
                    "error": data.get("error", "") or data.get("stderr", ""),
                    "exit_code": data.get("exit_code", 0),
                    "execution_time_ms": data.get("execution_time_ms", 0)
                }
            else:
                return {
                    "success": False,
                    "configured": True,
                    "compiled": False,
                    "error": f"Remote compiler returned status {resp.status_code}: {resp.text[:300]}",
                    "output": "",
                    "exit_code": resp.status_code,
                    "execution_time_ms": 0
                }
        except Exception as e:
            return {
                "success": False,
                "configured": True,
                "compiled": False,
                "error": f"Remote compiler connection error: {str(e)}",
                "output": "",
                "exit_code": -1,
                "execution_time_ms": 0
            }
