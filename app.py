from flask import Flask, render_template, request, Response

from main import main

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/", methods=['POST'])
def generate():
    apiKeys = []
    for apiKey in request.form.values():
        apiKeys.append(apiKey)
    return Response(
        main(apiKeys),
        mimetype='application/json',
        headers={'Content-disposition': 'attachment; filename=customConfig.json'})

if __name__ == "__main__":
    app.run()
