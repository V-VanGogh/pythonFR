from pymongo import MongoClient
import base64
import os

KNOWN_FACES_DIR = 'known_faces'

# create a MongoClient connection
client = MongoClient('mongodb://localhost:27017/')
# declare your database
db = client['Girokomeio']
# declare the collection you need
collection = db['patients']

x = collection.find({}, {'_id': 0, 'Name': 0, 'Age': 0, 'Registered': 0, '__v': 0, })

y = collection.find({}, {'_id': 0, 'Surname': 1, 'Image': 1})

for data in x:
    mongoImage = data['Image']
    png_recovered = base64.b64encode(mongoImage).decode("utf-8")
    imgData = base64.b64decode(png_recovered)
    Surname = data['Surname']
    if not os.path.exists(f"{KNOWN_FACES_DIR}/{Surname}"):
        os.mkdir(f"{KNOWN_FACES_DIR}/{Surname}")
    fh = open('known_faces/' + Surname + '/' + Surname + '.jpg', 'wb')

    fh.write(imgData)
    fh.close()
