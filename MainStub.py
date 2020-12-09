import flask
import requests
import json
from waitress import serve
import os
from flask import Flask, render_template, request, jsonify, json
from flask import request, url_for, current_app
from datetime import date
from datetime import datetime
from datetime import timedelta
import re
import sys
import pymysql
import pymysql.cursors
from datetime import date
from flask_cors import CORS, cross_origin
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import ft2font
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

pymysql.install_as_MySQLdb()

# Creates Flask with  our project name as argument
app = Flask(__name__)

# CORS to allow permission and give access to api request from Angular(front End)
CORS(app)


# Function to form connection
def GetDbConnectionDetails():
    conn = pymysql.connect(host="aptitudebuddydb1.cda1nryde4k9.us-east-2.rds.amazonaws.com",
                           user="admin",
                           passwd="AptitudeBuddyDBpass",
                           db="aptitudebuddy_db")
    cursor = conn.cursor()
    return cursor


# Decorator wraps our function given in it and calls it when the web server receives request that matches the request
@app.route('/')
# To enable cross origin
@cross_origin()
def TestFunction():
    return jsonify({'Answer': "Hello"}), 200


# LOGIN FUNCTIONALITY
@app.route('/login', methods=['POST'])
@cross_origin()
def LoginFunction():
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    email = json_data["email"]
    Password = json_data["password"]

    # Calling Get connection details to get cursor Object
    cursorVal = GetDbConnectionDetails()
    print(email)

    # Executing Query
    Query = "select password from UserDetails where EmailId =%s"
    cursorVal.execute(Query, email)

    # Loop Between Rows Using Tuple and validate
    rows = cursorVal.fetchall()
    for row in rows:
        print(row[0])
        if row[0] == Password:
            Resp = "Login Successful"
        else:
            Resp = "Login Failed"

    if cursorVal.rowcount == 0:
        Resp = "Login Failed"

    # close connection
    cursorVal.close()

    return jsonify({'LoginResponse': Resp}), 200


# REGISTER TO WEBSITE FUNCTIONALITY
@app.route('/register', methods=['POST'])
@cross_origin()
def Register():
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    userName = json_data["userName"]
    EmailId = json_data["emailId"]
    Password = json_data["password"]

    # Establishing connection and executing query
    conn = pymysql.connect(host="aptitudebuddydb1.cda1nryde4k9.us-east-2.rds.amazonaws.com", user="admin",
                           passwd="AptitudeBuddyDBpass", db="aptitudebuddy_db")
    cursorVal = conn.cursor()
    Query = "INSERT INTO `UserDetails` (`emailId`,`password`,`userName`) VALUES (%s,%s,%s)"
    cursorVal.execute(Query, (EmailId, Password, userName))

    # commit changes and close connection
    conn.commit()
    cursorVal.close()

    return jsonify({'Response': "Registered Successfully"}), 200


# CHAT BOT FUNCTIONALITY
@app.route('/chatbot/chat', methods=['POST'])
@cross_origin()
def Dictionary():
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    Question = json_data["question"]
    Question = Question.lower()

    # Default Answer if Nothing matches
    Response = "Sorry I can't Understand you"

    # ChatBot Dictionary File to Pick Response
    ChatDic = {
        "hi": "Hello",
        "hello": "Hi there",
        "what causes breast cancer?": "Studies have identified numerous risk factors for breast cancer in women, "
                                      "including hormonal, lifestyle and environmental factors that may increase the "
                                      "risk of the disease.",
        "what is inflammatory breast cancer?": "Considered a rare disease, inflammatory breast cancer (IBC) "
                                               "typically forms in the soft tissues, blocking lymph vessels in the "
                                               "breast skin. That's why the breast often becomes firm, tender, "
                                               "itchy, red and warm, from the increase in blood flow and a build-up "
                                               "of white blood cells. IBC differs from other forms of breast cancer, "
                                               "especially in symptoms, prognosis and treatment.",
        "when should I begin screening for breast cancer?": "Mammograms every two years for women 55 and older, "
                                                            "unless they choose to stick with yearly screenings",
        "what type of doctor should I see if I think I have breast cancer?": "If you think you have breast cancer, "
                                                                             "you should talk to your primary care "
                                                                             "physician or OB/GYN.",

        "what is your name": "My Name is Pink Bot",
        "breast cancer": "Breast cancer can occur in women and rarely in men.Symptoms of breast cancer include a lump in the breast, bloody discharge from the nipple, and changes in the shape or texture of the nipple or breast.",
        "breast cancer treatment": "Treatment depends on the stage of cancer. It may consist of chemotherapy, radiation, and surgery.",
        "Can breast cancer kill you?": "More than 41,000 women are expected to die from the disease.",
        "types of breast cancer": "Types of breast cancer include ductal carcinoma in situ, invasive ductal carcinoma, inflammatory breast cancer, and metastatic breast cancer."

    }

    # Looping in Dictionary to Find Match
    for x in ChatDic:
        print(x, file=sys.stderr)
        if x == Question:
            Response = ChatDic.get(x)
            print(Response, file=sys.stderr)
            break

    return jsonify({'Answer': Response}), 200


@app.route('/chatBot/appointment', methods=['POST'])
@cross_origin()
def fixAppointment():
    json_data = flask.request.json
    emailId = json_data["emailId"]

    # Calling Get connection details to get cursor Object
    conn = pymysql.connect(host="aptitudebuddydb1.cda1nryde4k9.us-east-2.rds.amazonaws.com",
                           user="admin",
                           passwd="AptitudeBuddyDBpass",
                           db="aptitudebuddy_db")
    cursorVal = conn.cursor()
    Query = "select userName from  `UserDetails` where emailId= %s"
    userName = cursorVal.execute(Query, emailId)

    CurrentDate = date.today() + timedelta(days=1)
    CurrentDate1 = str(CurrentDate)
    Response = "An appointment is Fixed with the Doctor on " + CurrentDate1 + " at 10 AM "

    Query1 = "UPDATE UserDetails SET appointment = %s WHERE emailId=%s"
    cursorVal.execute(Query1, (CurrentDate1, emailId))
    conn.commit()
    conn.close()

    return jsonify({'Answer': Response}), 200


# PROFILE DATA FUNCTIONALITY API CALL 1 TO CHECK
@app.route('/profiledatacheck', methods=['POST'])
@cross_origin()
def fetch_profile_data_function():
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    EmailId = json_data["emailId"]

    # Calling Get connection details to get cursor Object
    cursorVal = GetDbConnectionDetails()
    print(cursorVal)

    # Executing Query and store in count to check user EmailId present in db or not
    Query = "Select userCluster from UserDetails where EmailId=%s"
    Count = cursorVal.execute(Query, EmailId)

    # Creating an empty dictionary to send response
    RespDict = {}

    if Count == 0:
        RespDict["Response"] = "UserData not present"
    else:
        RespDict["Response"] = "UserData Present Sending Cluster Back"
        # Fetch Record from CursorVal
        record = cursorVal.fetchall()
        print(record)
        # Loop to add data into dictionary
        for row in record:
            RespDict["UserCluster"] = row[0]

    fetchClusterDetailsQuery = "select clusterData from clusterData"
    cursorVal.execute(fetchClusterDetailsQuery)
    record1 = cursorVal.fetchall()
    for row in record1:
        RespDict["ClusterData"] = row[0]

    # close connection
    cursorVal.close()

    return jsonify(RespDict)


# PROFILE DATA FUNCTIONALITY API CALL 2 TO UPDATE DATA, IDENTIFY CLUSTER USING MACHINE LEARNING, FIND PROBABILITY
@app.route('/quickcheckup', methods=['POST'])
@cross_origin()
def ClusterIdentificationAndProbabilty():
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    EmailId = json_data["emailId"]
    Age = json_data["age"]
    FoodHabit = json_data["foodHabit"]
    FamilyHistoryOfCancer = json_data["familyHistoryOfCancer"]
    PersonaHistoryOfCancer = json_data["personaHistoryOfCancer"]
    FirstMenstrualAge = json_data["firstMenstrualAge"]
    ExposureToRadiation = json_data["exposureToRadiation"]
    BreastFeeding = json_data["breastFeeding"]
    OccupationInvolvesPhysicalActivity = json_data["occupationInvolvesPhysicalActivity"]
    Menopause = json_data["menopause"]
    Postmenopausal = json_data["postmenopausal"]
    Pregnant = json_data["pregnant"]
    AgeOfFirstPregnancy = json_data["ageOfFirstPregnancy"]
    DiagnosticResultNegative = json_data["diagnosticResultNegative"]
    WhichDiagnosticTest = json_data["whichDiagnosticTest"]
    Ethnicity = json_data["ethnicity"]
    Height = json_data["height"]
    DiagnosticTest = json_data["diagnosticTest"]
    HarmonalUse = json_data["harmonalUse"]
    Weight = json_data["weight"]
    Symptoms = json_data["symptoms"]
    Gender = json_data["gender"]
    userName = json_data["userName"]

    # Changing to 1 or 0 based on input
    if FamilyHistoryOfCancer == "Yes":
        FamilyHistoryOfCancer = 1
    else:
        FamilyHistoryOfCancer = 0

    if PersonaHistoryOfCancer == "Yes":
        PersonaHistoryOfCancer = 1
    else:
        PersonaHistoryOfCancer = 0

    if ExposureToRadiation == "Yes":
        ExposureToRadiation = 1
    else:
        ExposureToRadiation = 0

    if BreastFeeding == "Yes":
        BreastFeeding = 1
    else:
        BreastFeeding = 0

    if Menopause == "Yes":
        Menopause = 1
    else:
        Menopause = 0

    if Pregnant == "Yes":
        Pregnant = 1
    else:
        Pregnant = 0

    if OccupationInvolvesPhysicalActivity == "Yes":
        OccupationInvolvesPhysicalActivity = 1
    else:
        OccupationInvolvesPhysicalActivity = 0

    if Postmenopausal == "Yes":
        Postmenopausal = 0
    else:
        Postmenopausal = 1

    if FoodHabit == "veg":
        FoodHabit = 0
    else:
        FoodHabit = 1

    if DiagnosticResultNegative == "Yes":
        DiagnosticResultNegative = 0
    else:
        DiagnosticResultNegative = 1
    print(Age, PersonaHistoryOfCancer, FamilyHistoryOfCancer, ExposureToRadiation, FirstMenstrualAge,
          AgeOfFirstPregnancy)

    # CLUSTERING USER BASED ON THE INPUTS PROVIDED
    dataset = pd.read_csv(f'C:\\Users\\vijay.jeyakumar\\Desktop\\Breast_Cancer_Symptom.csv')
    X = dataset.iloc[:, :-1].values
    y = dataset.iloc[:, -1].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    classifier = KNeighborsClassifier(n_neighbors=5, metric='minkowski', p=2)
    classifier.fit(X_train, y_train)
    UserCluster = classifier.predict(
        sc.transform([[DiagnosticResultNegative, FoodHabit, Postmenopausal, ExposureToRadiation, BreastFeeding,
                       Menopause, Pregnant,
                       OccupationInvolvesPhysicalActivity, Age,
                       FirstMenstrualAge, FamilyHistoryOfCancer, PersonaHistoryOfCancer, FamilyHistoryOfCancer,
                       AgeOfFirstPregnancy, 1, 1]]))

    UserCluster = int(UserCluster[0])
    print(UserCluster)

    # CALCULATE PROBABILITY USING  Age	Personal history	Family history	Gene mutation	Age at first menstrual	Age at first child
    Age = int(Age)
    FirstMenstrualAge = int(FirstMenstrualAge)
    AgeOfFirstPregnancy = int(AgeOfFirstPregnancy)

    dataset = pd.read_csv(f'C:\\Users\\vijay.jeyakumar\\Desktop\\PredictionDataset.csv')
    X = dataset.iloc[:, :-2].values
    y = dataset.iloc[:, -1].values
    ct = ColumnTransformer(transformers=[('encoder', OneHotEncoder(), [6])], remainder='passthrough')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)
    # give input in the form of 2d array
    y_pred = regressor.predict([[Age, PersonaHistoryOfCancer, FamilyHistoryOfCancer, ExposureToRadiation,
                                 FirstMenstrualAge, AgeOfFirstPregnancy]])
    BC_probability = y_pred

    BC_probability = int(BC_probability[0])
    print(BC_probability)

    # Input cluster and Probability of cancer into database for future reference
    # Establishing connection and executing query
    conn = pymysql.connect(host="aptitudebuddydb1.cda1nryde4k9.us-east-2.rds.amazonaws.com", user="admin",
                           passwd="AptitudeBuddyDBpass", db="aptitudebuddy_db")
    cursorVal = conn.cursor()
    Query = "UPDATE UserDetails SET probability = %s, userCluster = %s where emailId= %s"
    cursorVal.execute(Query, (BC_probability, UserCluster, EmailId))
    # commit changes and close connection
    conn.commit()
    cursorVal.close()

    # Fetch Clusterdata to form graph
    conn = pymysql.connect(host="aptitudebuddydb1.cda1nryde4k9.us-east-2.rds.amazonaws.com", user="admin",
                           passwd="AptitudeBuddyDBpass", db="aptitudebuddy_db")
    cursorVal = conn.cursor()
    Query1 = "select clusterData from clusterData"
    cursorVal.execute(Query1)
    record1 = cursorVal.fetchall()
    for row in record1:
        ClusterData = row[0]
    # commit changes and close connection
    cursorVal.close()

    return jsonify({'userCluster': UserCluster, 'probability': BC_probability, 'clusterData': ClusterData}), 200


# EXERCISE DATA FUNCTIONALITY API CALL 1 TO CHECK PREVIOUS EXERCISE DATA AND GAP
@app.route('/exercisedatacheck', methods=['POST'])
@cross_origin()
def ExerciseDataCheck():
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    emailId = json_data["emailId"]

    # Calling Get connection details to get cursor Object
    cursorVal = GetDbConnectionDetails()
    print(cursorVal)

    # Executing Query and store in count to check user EmailId present in db or not
    Query = "Select * from UserExcerciseData where emailId=%s"
    Count = cursorVal.execute(Query, emailId)

    # Creating an empty dictionary to send response
    RespDict = {}

    if Count == 0:
        RespDict["Response"] = "UserData Not Present "
    else:
        RespDict["Response"] = "UserData Present Sending Day count and Gap"
        # Fetch Record from CursorVal
        record = cursorVal.fetchall()
        print(record)
        # Loop to add data into dictionary
        for row in record:
            RespDict["DayCount"] = row[1]
            RespDict["Gap"] = row[2]
        print(RespDict)

    # close connection
    cursorVal.close()

    return jsonify(RespDict)


# EXERCISE DATA FUNCTIONALITY API CALL 2 TO CHECK PREVIOUS EXERCISE DATA AND USE IT TO UPDATE DAY COUNT AND GAP
@app.route('/exercisedataupdate', methods=['POST'])
@cross_origin()
def ExerciseDataUpdate():
    datetimeFormat = '%Y-%m-%d'
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    emailId = json_data["emailId"]
    ExerciseDone = json_data["exerciseDone"]

    # initialing
    LatestTimeStamp = date.today()
    print(LatestTimeStamp)
    CurrentDayCount = 0
    TimeStamp = ""
    # Set count as 0 initially
    TodayCount = 0

    if ExerciseDone == "Yes":
        TodayCount = 1
        CurrentDate = date.today()
        CurrentDateString = str(CurrentDate)
    print("today's date", CurrentDate)

    # Establishing connection
    conn = pymysql.connect(host="aptitudebuddydb1.cda1nryde4k9.us-east-2.rds.amazonaws.com", user="admin",
                           passwd="AptitudeBuddyDBpass", db="aptitudebuddy_db")
    cursorVal = conn.cursor()
    # Executing Query and store in count to check user EmailId present in db or not
    Query = "Select * from UserExcerciseData where emailId=%s"
    Count = cursorVal.execute(Query, emailId)

    # Find Day count and Gap for new user and old one ...When a new user just starts
    if Count == 0:
        FinalDayCount = 1
        CurrentGap = 0
        Query1 = "INSERT INTO `UserExcerciseData` (`excerciseDayCount`,`gap`,`lastExerciseTimeStamp`,`emailId`) VALUES (%s,%s,%s,%s)"
        cursorVal.execute(Query1, (FinalDayCount, CurrentGap, LatestTimeStamp, emailId))
    else:
        # Fetch Record from CursorVal
        record = cursorVal.fetchall()
        print(record)
        # Loop to add data into dictionary
        for row in record:
            TimeStamp = row[1]
            CurrentDayCount = row[2]
            CurrentGap = row[3]

    # Calculate gap and Total Days Done and Update it in Database
    print(CurrentDayCount)
    print(TimeStamp)

    if Count != 0:
        FinalDayCount = int(CurrentDayCount) + TodayCount
        CurrentGap = datetime.strptime(CurrentDateString, datetimeFormat) - datetime.strptime(TimeStamp, datetimeFormat)
        print("FinalDayCount", FinalDayCount)
        print("New Gap", CurrentGap)
        CurrentGap = str(CurrentGap)
        CurrentGap = CurrentGap[0:1]
        print(CurrentGap)

    # Update the Latest Values in Database and send Response
    Query = "UPDATE UserExcerciseData SET excerciseDayCount = %s, gap = %s , lastExerciseTimeStamp= %s where emailId=%s"
    cursorVal.execute(Query, (FinalDayCount, CurrentGap, LatestTimeStamp, emailId))
    conn.commit()
    cursorVal.close()

    return jsonify({'DaysExercised': FinalDayCount, 'Gap': CurrentGap}), 200


# Main Function that specifies port,host etc
if __name__ == '__main__':
    app.run(host=None, port=5000, debug=True)
# Required to server from server
# serve(app, host='0.0.0.0', port=8080, threads=1)  # WAITRESS!
