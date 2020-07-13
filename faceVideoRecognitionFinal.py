import face_recognition
import os
import cv2
import threading
import datetime
import json
from pymongo import MongoClient
import base64
import os

from mail.mail import send_mail

# create face recognition instances
KNOWN_FACES_DIR = 'known_faces'
TOLERANCE = 0.6
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = 'hog'  # 'hog' or 'cnn' - CUDA accelerated (if available) deep-learning pretrained model

# create a MongoClient connection
client = MongoClient('mongodb://localhost:27017/')
db = client['Girokomeio']
collection = db['patientsTimeLocations']
collection_notifications = db['notifications']

# set video input
video = cv2.VideoCapture(0)

# Returns (R, G, B) from name
def name_to_color(name):
    # Take 3 first letters, tolower()
    # lowercased character ord() value rage is 97 to 122, substract 97, multiply by 8
    color = [(ord(c.lower()) - 97) * 8 for c in name[:3]]
    return color


# folder with images update function
def fill_image_folder():
    collection_patients = db['patients']
    fetch_image_data = collection_patients.find({}, {'_id': 0, 'Name': 0, 'Age': 0, 'Registered': 0, '__v': 0, })
    for data in fetch_image_data:
        mongo_image = data['Image']
        png_recovered = base64.b64encode(mongo_image).decode("utf-8")
        img_data = base64.b64decode(png_recovered)
        surname = data['Surname']

        if not os.path.exists(f"{KNOWN_FACES_DIR}/{surname}"):
            os.mkdir(f"{KNOWN_FACES_DIR}/{surname}")
        fh = open('known_faces/' + surname + '/' + surname + '.jpg', 'wb')
        fh.write(img_data)
        fh.close()


def notifications():
    fetch_time_data = collection.find({}, {'_id': 0})
    for data in fetch_time_data:

        if not collection_notifications.find_one({"Notification": 'Restricted_time'}):
            notification = {"Notification": 'Restricted_time'}
            x = collection_notifications.insert_one(notification)


def getRules():
    collectionRules = db['securityrules']
    fetch_rules = collectionRules.find({}, {'_id': 0, '__v': 0})
    print('edw')
    s_time_f = fetch_rules[0]['sTime']
    e_time_f = fetch_rules[0]['eTime']
    status_f = fetch_rules[0]['status']
    rules = {"status": status_f, "sTime": s_time_f, "eTime": e_time_f}
    return rules


fill_image_folder()
getRules()
s_time = getRules()['sTime']
e_time = getRules()['eTime']
status = getRules()['status']
notifications()
print('Loading known faces...')
known_faces = []
known_names = []

for name in os.listdir(KNOWN_FACES_DIR):

    for filename in os.listdir(f'{KNOWN_FACES_DIR}/{name}'):
        image = face_recognition.load_image_file(f'{KNOWN_FACES_DIR}/{name}/{filename}')
        encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(encoding)
        known_names.append(name)

print('Processing unknown faces...')
night_found = datetime.datetime.now().hour - 1
print(night_found)

while True:
    ret, frame = video.read()
    image = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    locations = face_recognition.face_locations(image, model=MODEL)
    encodings = face_recognition.face_encodings(image, locations)

    for face_encoding, face_location in zip(encodings, locations):
        results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
        match = None
        if True in results:  # If at least one is true, get a name of first of found labels
            match = known_names[results.index(True)]
            dateTimeObj = datetime.datetime.now()
            if (0 < datetime.datetime.now().second < 2) or (12 < datetime.datetime.now().second < 14) or (
                    24 < datetime.datetime.now().second < 26) or (
                    36 < datetime.datetime.now().second < 38) or (
                    48 < datetime.datetime.now().second < 50):

                # dateTimeObj = datetime.datetime.now()
                print(f' - {match} from {results} at {dateTimeObj}')
                if collection.find_one({"Surname": match}):
                    x = collection.update({"Surname": match},
                                          {"$push": {"Events.[]": {"Time": dateTimeObj, "Camera": 1}}})
                else:
                    patientTimeLocationDict = {"Surname": match}
                    x = collection.insert_one(patientTimeLocationDict)

            if status:
                if s_time > e_time:
                    if (int(s_time) <= datetime.datetime.now().hour or datetime.datetime.now().hour <= int(
                            e_time)) :
                        # send_mail(match, str(datetime.datetime.now()))
                        night_found = datetime.datetime.now().hour
                        z = collection_notifications.update({"Notification": 'Restricted_time'},
                                              {"$push": {"Events.[]": {"Surname": match,"Time": dateTimeObj, "Camera": 1}}})

                else:
                    if (int(s_time) <= datetime.datetime.now().hour <= int(
                            e_time)) :
                        # send_mail(match, str(datetime.datetime.now()))
                        night_found = datetime.datetime.now().hour
                        z = collection_notifications.update({"Notification": 'Restricted_time'},
                                              {"$push": {"Events.[]": {"Surname": match, "Time": dateTimeObj, "Camera": 1}}})

            top_left = (face_location[3], face_location[0])
            bottom_right = (face_location[1], face_location[2])
            color = name_to_color(match)
            cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)

            top_left = (face_location[3], face_location[2])
            bottom_right = (face_location[1], face_location[2] + 22)
            cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
            cv2.putText(image, match, (face_location[3] + 10, face_location[2] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (200, 200, 200), FONT_THICKNESS)
    cv2.imshow('camera', image)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        cv2.destroyWindow('camera')
        break
    # cv2.waitKey(0)
