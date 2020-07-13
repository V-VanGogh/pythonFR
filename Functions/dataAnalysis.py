from pymongo import MongoClient
import time
import threading

# connect to database
client = MongoClient('mongodb://localhost:27017/')
db = client['Girokomeio']
collection = db['patientsTimeLocations']
collection_corrected = db['patientsTimeLocationsCorrected']
collection_camera_preferance = db['patientcameraprefs']
collection_time_diagrams = db['patientimediagrams']
collection_notifications = db['notifications']
collection_notifications_corrected = db['notificationscorrected']


def data_normalization():
    fetch_time_data = collection.find({}, {'_id': 0})
    time = 0

    for data in fetch_time_data:

        if collection_corrected.find_one({"Surname": data['Surname']}):
            i: int = 0
            for j in data['Events']['[]']:
                timeMongo = data['Events']['[]'][i]['Time']
                time_minute = timeMongo.minute
                if time_minute == time:
                    time = time_minute
                else:
                    if collection_corrected.find_one({"Surname": data['Surname'], "Events.[].Time": timeMongo}):
                        print('found')
                    else:
                        print('not found')
                        x = collection_corrected.update({"Surname": data['Surname']},
                                                        {"$push": {"Events.[]": {"Time": timeMongo,
                                                                                 "Camera": data['Events']['[]'][i][
                                                                                     'Camera']}}})
                    time = time_minute
                print(time_minute)
                print(data['Events']['[]'][i]['Time'])
                # print(data['Events']['[]'][i]['Camera'])
                i = i + 1
        else:
            patientTimeLocationDict = {"Surname": data['Surname']}
            x = collection_corrected.insert_one(patientTimeLocationDict)
    threading.Timer(60.0, data_normalization).start()


def notification_data_normalization():
    fetch_notif_data = collection_notifications.find({}, {'_id': 0})
    time = 0

    for data in fetch_notif_data:

        if collection_notifications_corrected.find_one({"Notification": 'Restricted_time'}):
            i: int = 0
            for j in data['Events']['[]']:
                notif_surname_mongo = data['Events']['[]'][i]['Surname']
                notif_time_mongo = data['Events']['[]'][i]['Time']
                time_minute = notif_time_mongo.minute
                if time_minute == time:
                    time = time_minute
                else:
                    if collection_notifications_corrected.find_one(
                            {"Notification": 'Restricted_time', "Events.[].Surname": notif_surname_mongo,
                             "Events.[].Time": notif_time_mongo}):
                        print('found')
                    else:
                        print('not found')
                        x = collection_notifications_corrected.update({"Notification": 'Restricted_time'},
                                                        {"$push": {"Events.[]": {"Surname": notif_surname_mongo,
                                                                                 "Time": notif_time_mongo,
                                                                                 "Camera": data['Events']['[]'][i][
                                                                                     'Camera']}}})
                    time = time_minute
                print(time_minute)
                print(data['Events']['[]'][i]['Time'])
                # print(data['Events']['[]'][i]['Camera'])
                i = i + 1
        else:
            notificationcorrected = {"Notification": 'Restricted_time'}
            x = collection_notifications_corrected.insert_one(notificationcorrected)
    threading.Timer(60.0, data_normalization).start()


def patient_camera_preferance():
    fetch_patient_preferences = collection_corrected.find({}, {'_id': 0})

    for data in fetch_patient_preferences:
        camera_count0 = 0
        camera_count1 = 0
        if collection_camera_preferance.find_one({"Surname": data['Surname']}):
            i: int = 0
            for data_camera in data['Events']['[]']:
                cameraMongo = data['Events']['[]'][i]['Camera']
                if cameraMongo == 0:
                    camera_count0 = camera_count0 + 1
                else:
                    camera_count1 = camera_count1 + 1
                i = i + 1
            x = collection_camera_preferance.update({"Surname": data['Surname']},
                                                    {"$set": {"Camera0": str(camera_count0),
                                                              "Camera1": str(camera_count1)}})

        else:
            patient = {"Surname": data['Surname']}
            x = collection_camera_preferance.insert_one(patient)
    threading.Timer(60.0, patient_camera_preferance).start()


def patient_time_diagrams():
    fetch_patient_time_cameras = collection_corrected.find({}, {'_id': 0})
    for data in fetch_patient_time_cameras:
        if collection_time_diagrams.find_one({"Surname": data['Surname']}):
            i: int = 0
            for data_camera in data['Events']['[]']:
                cameraMongo = data['Events']['[]'][i]['Camera']
                dateMongo = data['Events']['[]'][i]['Time']
                # timestamp = time.mktime(dateMongo.timetuple())
                # inttimestamp = int(timestamp)
                # strtimestamp = str(inttimestamp)

                # my_dict[strtimestamp] = cameraMongo
                if collection_time_diagrams.find_one({"Surname": data['Surname'], "Events.Time": dateMongo}):
                    print('found')
                else:
                    print('not found')
                    x = collection_time_diagrams.update({"Surname": data['Surname']},
                                                        {"$push": {
                                                            "Events": {"Time": dateMongo, "Camera": cameraMongo}}})

                i = i + 1

        else:
            patient = {"Surname": data['Surname']}
            x = collection_time_diagrams.insert_one(patient)
    threading.Timer(60.0, patient_time_diagrams).start()


data_normalization()
data_normalization()
patient_camera_preferance()
patient_camera_preferance()
patient_time_diagrams()
patient_time_diagrams()
patient_time_diagrams()
notification_data_normalization()
notification_data_normalization()
