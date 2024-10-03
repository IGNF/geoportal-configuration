from flask import Flask, render_template, request, Response

from main import main

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/", methods=['POST'])
def generate():
    apiKeys = []
    referer = ""
    i = 0;
    for param in request.form.values():
        if (i == 0):
            referer = param
        else :
            apiKeys.append(param)
        i += 1
    return Response(
        main(apiKeys, referer),
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
