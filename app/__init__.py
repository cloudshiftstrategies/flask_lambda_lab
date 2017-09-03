from flask import Flask
from flask import render_template
app = Flask(__name__)

app.config.from_object('config')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/loadgen")
def loadgen():
    from time import time
    iterations = 300000
    i = 0
    x = 2
    start = time()
    while i < iterations:
        x = x * 2
        i += 1
    end = time()
    seconds = end - start
    return render_template('loadgen.html', iters=iterations,
            duration = seconds)
