from flask import Flask
from flask import request
from flask_cors import CORS
from api import getReply

app = Flask(__name__)
CORS(app)

OK = 200

@app.route("/")
def home():
    return "Invalid path"


@app.route("/query")
def query():
    try:
        query = request.args.get('text', -1, type=str)
        if query != -1:
            response = [getReply("857443443", query)]
        else:
            response = "Please input a query."
    except Exception as error:
        response = "Error"
    print("Returning response",response)
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5601)