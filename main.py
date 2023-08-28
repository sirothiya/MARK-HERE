
import os
import pickle

import cv2
import face_recognition
import numpy as np
import cvzone

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://smart-attendence-e701c-default-rtdb.firebaseio.com/",
    'storageBucket':"smart-attendence-e701c.appspot.com"
})

bucket = storage.bucket()


cap=cv2.VideoCapture(0)

#// if you have second camera you can set first parameter as 1
cap.set(3,640)
cap.set(4,480)
if not (cap.isOpened()):
    print("Could not open video device")
''''
imagebackground=cv2.imread('Resources/background.png')
#importing mode images into a list
mode='Resources/Modes'
modepath=os.listdir(mode)
imgmodes=[]
for path in modepath:
    imgmodes.append(cv2.imread(os.path.join(mode,path)))


#load the encoding file
#print("loading encoded file.....")
file=open('Encodefile.p','rb')
encodelistknownwithids= pickle.load(file)
file.close()
encodelistknown,studentsids =encodelistknownwithids
#print(studentsids)
#print("encoded file loaded")

modeType=0
counter=0
id=-1
imgstudent=[]
while True:
    sucess,frame= cap.read()

    # now taking encoding and checking any of the faces matching with any of the encoding or not

    imgsmall=cv2.resize(frame,(0,0),None,0.25,0.25)
    imgsmall=cv2.cvtColor(imgsmall,cv2.COLOR_BGR2RGB)
    facecurrframe=face_recognition.face_locations(imgsmall)

    #when we have loactions of our images we have to find their encodings .so we have the previous encoding of
    #our faces  images and we have to find the new ones and then we have to compare them

    encodecurrframe=face_recognition.face_encodings(imgsmall,facecurrframe)


    imagebackground[162:162+480,55:55+640]=frame
    imagebackground[44:44+633,808:808+414] = imgmodes[modeType]

    #cv2.imshow("Live",frame)
    if facecurrframe:
        for encodeFace, facLock in zip(encodecurrframe, facecurrframe):
            matches = face_recognition.compare_faces(encodelistknown, encodeFace)
            facedistance = face_recognition.face_distance(encodelistknown, encodeFace)
            # print("matches", matches)
            # print("facedis",facedistance)
            # lower the face distance better the matches

            matchIndex = np.argmin(facedistance)
            # print("match index",matchIndex)
            if matches[matchIndex]:
                # print("known face detected")
                # print(studentsids[matchIndex])
                # now we are showing the face and id beside the webcame
                # in this we can use cv.rectangle() or cvzone.cornerRect()

                # bounding box inform from image itself
                y1, x2, y2, x1 = facLock
                # as we reduced the size by 1/4 then we have to multiply by 4 to get back to its original size
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imagebackground = cvzone.cornerRect(imagebackground, bbox, rt=0)
                id = studentsids[matchIndex]
                #print(id)
                if counter == 0:
                    cvzone.putTextRect(imagebackground,"Loading",(274,400))
                    cv2.imshow("Smart attendance", imagebackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1
        if counter != 0:

            if counter == 1:
                # get the data
                studentinfo = db.reference(f'students/{id}').get()
                print(studentinfo)
                # get the image from the storage
                blob = bucket.get_blob(f'images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgstudent = cv2.imdecode(array, cv2.COLOR_BGR2RGB)

                # update data of attendence
                datetimeobject = datetime.strptime(studentinfo['last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondelapse = (datetime.now() - datetimeobject).total_seconds()
                print(secondelapse)
                if secondelapse > 30:
                    ref = db.reference(f'students/{id}')
                    studentinfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentinfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    imagebackground[44:44 + 633, 808:808 + 414] = imgmodes[modeType]
                    counter = 0
                if modeType != 3:
                    # checking that do we need to update

                    if 10 < counter < 20:
                        modeType = 2
                    imagebackground[44:44 + 633, 808:808 + 414] = imgmodes[modeType]

                    if counter <= 10:
                        cv2.putText(imagebackground, str(studentinfo['total_attendance']), (861, 125),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

                        cv2.putText(imagebackground, str(studentinfo['major']), (1006, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imagebackground, str(id), (1006, 493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imagebackground, str(studentinfo['standing']), (910, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imagebackground, str(studentinfo['year']), (1025, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imagebackground, str(studentinfo['starting_year']), (1125, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        (w, h), _ = cv2.getTextSize(studentinfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(imagebackground, str(studentinfo['name']), (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                        imagebackground[175:175 + 216, 909:909 + 216] = imgstudent

                    counter += 1

                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        studentinfo = []
                        imgstudent = []
                        imagebackground[44:44 + 633, 808:808 + 414] = imgmodes[modeType]

    else:
            modeType=0
            counter=0

    cv2.imshow("Smart attendance", imagebackground)
    cv2.waitKey(1)
    '''

imgBackground = cv2.imread('Resources/background.png')

# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Match Index", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # Get the Data
                studentInfo = db.reference(f'students/{id}').get()
                print(studentInfo)
                # Get the Image from the storage
                blob = bucket.get_blob(f'images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # Update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:
                    ref = db.reference(f'students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
