import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://smart-attendence-e701c-default-rtdb.firebaseio.com/"
})

ref=db.reference('students')

data={
    "0001":
        {
            "name":"shalini sirothiya",
            "major":"IT",
            "starting_year":2020,
            "total_attendance":0,
            "standing":"Good",
            "year":4,
            "last_attendence_time":"2022-12-11  02:53:48"
        },
    "0002":
        {
            "name":"Prashant mishra",
            "major":"IT",
            "starting_year":2020,
            "total_attendance":0,
            "standing":"Good",
            "year":4,
            "last_attendence_time":"2022-12-11  02:53:48"
        },
    "0003":
        {
            "name":"prani mishra",
            "major":"IT",
            "starting_year":2020,
            "total_attendance":0,
            "standing":"Good",
            "year":4,
            "last_attendence_time":"2022-12-11  02:53:48"
        },
}

for key,value in data.items():
    ref.child(key).set(value)