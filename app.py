import os
from flask import Flask, render_template, send_from_directory, jsonify
from config import Config
from routes.api import api_bp

def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )
    app.config.from_object(Config)

    # Register API Blueprint
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, "static", "assets"),
            "favicon.svg",
            mimetype="image/svg+xml"
        )

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    print("\n=======================================================")
    print(">> CodeVerse AI - C++ Programming Mentor Server")
    print(f">> Serving on http://127.0.0.1:{Config.PORT}")
    print(f">> AI Provider Mode: {Config.AI_PROVIDER}")
    print(f">> C++ Local Compiler: {Config.CPP_COMPILER_PATH or 'Not detected (Execution status reported cleanly)'}")
    print("=======================================================\n")
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
