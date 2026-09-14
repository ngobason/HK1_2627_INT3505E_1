#Ex1
from flask import Flask
app = Flask(__name__)
@app.route("/")
def index():
  return {
    "name": "son",
    "class": "SOA"
  }
if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=True)