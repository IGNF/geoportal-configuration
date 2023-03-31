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

@app.route("/api", methods=['GET'])
def generateAPI():
    try:
        apiKeys = request.args.get("keys").split(",")
        return Response(
            main(apiKeys),
            mimetype='application/json')
    except AttributeError:
        return "Provide API keys separated with comas under the `keys` GET parameter"

if __name__ == "__main__":
    app.run()
