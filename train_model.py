from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import pickle
import os
def train_model(companyname):

    dirName = f"Clients/{companyname}"

    if not os.path.exists(dirName):
        return False

    EMBEDDINGS = dirName + "/embeddings.pickle"
    RECOGNIZER = dirName + "/recognizer.pickle"
    LE = dirName + "/le.pickle"


    # load the face embeddings
    print("[INFO] loading face embeddings...")
    data = pickle.loads(open(EMBEDDINGS, "rb").read())

    # encode the labels
    print("[INFO] encoding labels...")
    le = LabelEncoder()
    labels = le.fit_transform(data["names"])

    # train the model used to accept the 128-d embeddings of the face and
    # then produce the actual face recognition
    print("[INFO] training model...")
    recognizer = SVC(C=1.0, kernel="linear", probability=True)
    recognizer.fit(data["embeddings"], labels)

    # write the actual face recognition model to disk
    f = open(RECOGNIZER, "wb")
    f.write(pickle.dumps(recognizer))
    f.close()
    print("[INFO] recognition model dumped to file")

    # write the label encoder to disk
    f = open(LE, "wb")
    f.write(pickle.dumps(le))
    f.close()
    print("[INFO] label encoder dumped to file")

    return True