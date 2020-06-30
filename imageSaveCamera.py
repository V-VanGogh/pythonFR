import requests


img_path = './path/to/img'
url = 'http://localhost:5000/patient/patientAddPhoto'
files = {'file': ('image.jpg', open(img_path, 'rb'), 'image/jpeg')}
r = requests.post(url, files=files)
print(r.text)