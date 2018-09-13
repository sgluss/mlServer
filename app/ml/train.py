import os, sys, re, pickle

import pandas as pd
import numpy as np

from sklearn import preprocessing

# import classifier
from sklearn import neighbors

# project dependencies
PATH_TO_HERE = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'

PATH_TO_DATA = PATH_TO_HERE + '../../datasets/'
PATH_TO_ARTIFACTS = PATH_TO_HERE + 'artifacts/'

# strip non-essential chars from the target string (in this case, whitespace and a period)
def cleanTarget(str):
    return re.sub('\.', '', str.strip())

def loadDataSet(filePath, skipRows=None):
    data = pd.read_csv(filePath, skiprows=skipRows)

    vars = data.iloc[:, :-1]
    target = data.iloc[:, -1].apply(cleanTarget)

    return vars, target

def generateEncoderAndTransform(vars, col):
    # 'unknown' element in case model sees a category not in the training set
    classes = np.append(vars.iloc[:, col].unique(), ["<unknown>"])
    encoder = preprocessing.LabelEncoder().fit(classes)

    vars.iloc[:, col] = encoder.transform(vars.iloc[:,col])
    return encoder

def generateEncoderAndTransformForTarget(target):
    # 'unknown' element in case model sees a category not in the training set
    classes = np.append(target.unique(), ["<unknown>"])
    encoder = preprocessing.LabelEncoder().fit(classes)

    target.iloc[:] = encoder.transform(target)
    return encoder

def generateEncodersAndTransform(xTrain, yTrain):
    encoders = {}

    encoders['workClass'] = generateEncoderAndTransform(xTrain, 1)
    encoders['education'] = generateEncoderAndTransform(xTrain, 3)
    encoders['marital'] = generateEncoderAndTransform(xTrain, 5)
    encoders['occupation'] = generateEncoderAndTransform(xTrain, 6)
    encoders['relationship'] = generateEncoderAndTransform(xTrain, 7)
    encoders['race'] = generateEncoderAndTransform(xTrain, 8)
    encoders['sex'] = generateEncoderAndTransform(xTrain, 9)
    encoders['country'] = generateEncoderAndTransform(xTrain, 13)

    encoders['target'] = generateEncoderAndTransformForTarget(yTrain)

    return encoders

def transformVarsByEncoders(inputVars, target, encoders):
    inputVars.iloc[:, 1] = encoders['workClass'].transform(inputVars.iloc[:, 1])
    inputVars.iloc[:, 3] = encoders['education'].transform(inputVars.iloc[:, 3])
    inputVars.iloc[:, 5] = encoders['marital'].transform(inputVars.iloc[:, 5])
    inputVars.iloc[:, 6] = encoders['occupation'].transform(inputVars.iloc[:, 6])
    inputVars.iloc[:, 7] = encoders['relationship'].transform(inputVars.iloc[:, 7])
    inputVars.iloc[:, 8] = encoders['race'].transform(inputVars.iloc[:, 8])
    inputVars.iloc[:, 9] = encoders['sex'].transform(inputVars.iloc[:, 9])
    inputVars.iloc[:, 13] = encoders['country'].transform(inputVars.iloc[:, 13])

    target.iloc[:] = encoders['target'].transform(target)

def dumpModelAndEncoders(model, encoders):
    with open(f"{PATH_TO_ARTIFACTS}model.pkl", 'wb') as out:
        pickle.dump(model, out)

    # Dump encoders to disk
    with open(f"{PATH_TO_ARTIFACTS}encoders.pkl", 'wb') as out:
        pickle.dump(encoders, out)

def evaluate(model, xTest, yTest):
    result = model.predict(xTest)

    if len(result) != len(yTest):
        # This should not happen. Please Freakout
        raise Exception("list lengths do not match")

    misses = 0
    for i in range(0, len(result)):
        if result[i] != yTest[i]:
            misses += 1

    accuracy = (len(result) - misses) / len(result)

    print(f"Classification accuracy: {accuracy * 100}%")
    print(f"Classified {len(result) - misses} correctly out of {len(result)}")

    return accuracy, misses

def trainModel():
    # load dataset into dataframe
    print("Loading datasets")
    xTrain, yTrain = loadDataSet(PATH_TO_DATA + 'adultData')
    xTest, yTest = loadDataSet(PATH_TO_DATA + 'adultTest', [0])

    # Encode data, needed because model can't understand strings
    # TODO: one-hot encoding
    print("Building and applying encoders")
    encoders = generateEncodersAndTransform(xTrain, yTrain)
    transformVarsByEncoders(xTest, yTest, encoders)

    # Train model
    print("Training model")
    n_neighbors = 10
    clf = neighbors.KNeighborsClassifier(n_neighbors, weights='uniform')
    clf.fit(xTrain, yTrain)

    # Evaluate model performance
    print("Generating batch predictions")
    accuracy, misses = evaluate(clf, xTest, yTest)

    # dump artifacts
    print("Dumping artifacts to disk")
    dumpModelAndEncoders(clf, encoders)

if __name__ == '__main__':
    trainModel()
