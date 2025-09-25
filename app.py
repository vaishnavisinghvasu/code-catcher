import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/download")
def download_game():
    # serve the zip file from root folder
    return send_from_directory(directory=os.getcwd(), filename="Code-Catcher-Game.zip", as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
