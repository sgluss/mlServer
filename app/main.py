import flask
from io import StringIO

import pandas as pd

from ml.train import trainModel
from ml import predict

app = flask.Flask(__name__)
app.debug = True

def getClassifier():
    # init the classifier as needed
    if predict.classifier == None:
        predict.classifier = predict.ModelService()

@app.route("/hello", methods=['GET'])
def hello():
    return "<h1 style='color:red'>Hello World!</h1>"

@app.route("/train", methods=['GET'])
def train():
    print("Received command to train model")
    accuracy, elapsed = trainModel()
    return f"""<h1 style='color:green'>Training Complete!</h1>
           <h2 style='color:green'>Accuracy: {'%.3f'%(accuracy * 100)}%</h2>
           <h2 style='color:green'>Elapsed Time: {'%.3f'%(elapsed * 1000)} ms</h2>"""

@app.route("/predict", methods=['POST'])
def invoke():
    getClassifier()

    # Convert from CSV to pandas
    if flask.request.content_type == 'text/csv':
        data = flask.request.data.decode('utf-8')
        s = StringIO(data)
        data = pd.read_csv(s, header=None)
        print(data)
    else:
        return flask.Response(response='This predictor only supports CSV data', status=415, mimetype='text/plain')

    prediction = predict.classifier.predict(data)

    out = StringIO()
    pd.DataFrame(prediction).to_csv(out, header=False, index=False)
    result = out.getvalue()

    return flask.Response(response=result, status=200, mimetype='text/csv')
