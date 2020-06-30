import face_recognition
import os
import cv2
import pickle
import time

KNOWN_FACES_DIR = 'known_faces'
UNKNOWN_FACES_DIR = 'unknown_faces'
TOLERANCE = 0.6
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = 'hog'  # 'hog' or 'cnn' - CUDA accelerated (if available) deep-learning pretrained model

video = cv2.VideoCapture(0)


# Returns (R, G, B) from name
# def name_to_color(name):
#     # Take 3 first letters, tolower()
#     # lowercased character ord() value rage is 97 to 122, substract 97, multiply by 8
#     color = [(ord(c.lower()) - 97) * 8 for c in name[:3]]
#     return color


print('Loading known faces...')
known_faces = []
known_names = []

for name in os.listdir(KNOWN_FACES_DIR):

    for filename in os.listdir(f'{KNOWN_FACES_DIR}/{name}'):
        print(f'{name}/{filename}')
        encoding = pickle.load(open(f'{KNOWN_FACES_DIR}/{name}/{filename}', 'rb'))
        known_faces.append(encoding)
        known_names.append(int(name))

if len(known_names) > 0:
    next_id = max(known_names) + 1
else:
    next_id = 0

print('Processing unknown faces...')
while True:
    ret, image = video.read()
    locations = face_recognition.face_locations(image, model=MODEL)
    encodings = face_recognition.face_encodings(image, locations)
    # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    for face_encoding, face_location in zip(encodings, locations):
        results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
        match = None
        if True in results:  # If at least one is true, get a name of first of found labels
            match = known_names[results.index(True)]
            print(f' - {match} from {results}')
        else:
            match = str(next_id)
            next_id += 1
            known_names.append(match)
            known_faces.append(face_encoding)
            os.mkdir(f"{KNOWN_FACES_DIR}/{match}")
            pickle.dump(face_encoding, open(f"{KNOWN_FACES_DIR}/{match}/{match}-{int(time.time())}", "wb"))

        top_left = (face_location[3], face_location[0])
        bottom_right = (face_location[1], face_location[2])
        color = [0, 255, 0]
        cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)

        top_left = (face_location[3], face_location[2])
        bottom_right = (face_location[1], face_location[2] + 22)
        cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
        cv2.putText(image, match, (face_location[3] + 10, face_location[2] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (200, 200, 200), FONT_THICKNESS)
    cv2.imshow("", image)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    # cv2.waitKey(0)
    # cv2.destroyWindow(filename)
