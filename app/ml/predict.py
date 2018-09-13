import os, sys, pickle, traceback

PATH_TO_HERE = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'
sys.path.append(PATH_TO_HERE + '../')

PATH_TO_ARTIFACTS = PATH_TO_HERE + 'artifacts/'

class ModelService():
    def __init__(self):
        self.model, self.encoders = self.getModelAndEncodersFromFile()

    def getModelAndEncodersFromFile(self):
        try:
            filePath = os.path.join(PATH_TO_ARTIFACTS, 'model.pkl')
            with open(filePath, 'rb') as inp:
                print("Loading model, filesize: " + str(os.path.getsize(filePath)))
                model = pickle.load(inp)

            filePath = os.path.join(PATH_TO_ARTIFACTS, 'encoders.pkl')
            with open(filePath, 'rb') as inp:
                print("Loading Encoders, filesize: " + str(os.path.getsize(filePath)))
                encoders = pickle.load(inp)

            return model, encoders

        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as e:
            print("Unexpected exception: ", traceback.format_exc(e))
        except:
            print("Unexpected error: ", sys.exc_info())

    def predict(self, input):
        inputVars = input

        # Apply encoders
        # series is a Pandas series
        def resetNovelValuesAndTransform(series, encoder):
            for i, value in series.iteritems():
                if value not in encoder.classes_:
                    series[i] = "<unknown>"
            return encoder.transform(series)

        # catch novel values
        inputVars.iloc[:, 1] = resetNovelValuesAndTransform(inputVars.iloc[:, 1], self.encoders['workClass'])
        inputVars.iloc[:, 3] = resetNovelValuesAndTransform(inputVars.iloc[:, 3], self.encoders['education'])
        inputVars.iloc[:, 5] = resetNovelValuesAndTransform(inputVars.iloc[:, 5], self.encoders['marital'])
        inputVars.iloc[:, 6] = resetNovelValuesAndTransform(inputVars.iloc[:, 6], self.encoders['occupation'])
        inputVars.iloc[:, 7] = resetNovelValuesAndTransform(inputVars.iloc[:, 7], self.encoders['relationship'])
        inputVars.iloc[:, 8] = resetNovelValuesAndTransform(inputVars.iloc[:, 8], self.encoders['race'])
        inputVars.iloc[:, 9] = resetNovelValuesAndTransform(inputVars.iloc[:, 9], self.encoders['sex'])
        inputVars.iloc[:, 13] = resetNovelValuesAndTransform(inputVars.iloc[:, 13], self.encoders['country'])

        return self.model.predict(inputVars)
