from flask import Flask, render_template, send_file
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/download")
def download_game():
    zip_path = os.path.join(app.root_path, "Code-Catcher-Game.zip")
    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
