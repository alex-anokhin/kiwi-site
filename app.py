from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def greet_json():
	return jsonify({"Hello": "World!"})

if __name__ == "__main__":
	app.run(debug=True)
