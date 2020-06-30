from pymongo import MongoClient


def mongo():
    # create a MongoClient connection
    client = MongoClient('mongodb://localhost:27017/')
    # declare your database
    db = client['Girokomeio']
    # declare the collection you need
    collection = db['patientsTimeLocations']
