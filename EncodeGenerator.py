import os
import cv2
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://smart-attendence-e701c-default-rtdb.firebaseio.com/",
    'storageBucket':"smart-attendence-e701c.appspot.com"
})


#importing student images into a list
mode='images'
pathlist=os.listdir(mode)
imglist=[]
studentsids=[]
for path in pathlist:
    imglist.append(cv2.imread(os.path.join(mode,path)))
    #print(os.path.splitext(path)[0])
    studentsids.append(os.path.splitext(path)[0])

    #uploading images to the database of firebase
    filename  = f'{mode}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)


def findencoding(imageslist):
    encodelist=[]
    for img in imageslist:
       #changing colour of images as both open cv and face recognation uses different colours
       # open cv uses bgr and face recognation uses rgb

       img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
       encode=face_recognition.face_encodings(img)[0]
       encodelist.append(encode)
    return encodelist
print("encoding started")
encodelistknown=findencoding(imglist)
encodelistknownwithids=[encodelistknown,studentsids]
print("encoding compeleted")

file =open("Encodefile.p",'wb')
pickle.dump(encodelistknownwithids,file)
file.close()
