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

pymysql.install_as_MySQLdb()

# Creates Flask with  our project name as argument
app = Flask(__name__)

# CORS to allow permission and give access to api request from Angular(front End)
CORS(app)


# Function to form connection
def GetDbConnectionDetails():
    conn = pymysql.connect(host="bcsdatabase.checsubgcuu9.ap-south-1.rds.amazonaws.com",
                           user="admin",
                           passwd="hackforpinkdb",
                           db="backend_bcs")
    cursor = conn.cursor()
    return cursor


# Decorator wraps our function given in it and calls it when the web server receives request that matches the request
@app.route('/')
# To enable cross origin
@cross_origin()
def BaseFunction():
    return jsonify({'Answer': "Hello"}), 200


# LOGIN FUNCTIONALITY
@app.route('/Login', methods=['POST'])
@cross_origin()
def LoginFunction():
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    UserName = json_data["UserName"]
    Password = json_data["Password"]

    # Calling Get connection details to get cursor Object
    cursorVal = GetDbConnectionDetails()
    print(UserName)

    # Executing Query
    Query = "select * from UserDetails where EmailId =%s"
    cursorVal.execute(Query, UserName)

    # Print Row count
    print("Total number of rows in Laptop is: ", cursorVal.rowcount)

    # Loop Between Rows Using Tuple and validate
    rows = cursorVal.fetchall()
    for row in rows:
        print(row[1], row[2])
        if cursorVal.rowcount != 0 & row[1] == row[2]:
            Resp = "Login Successful"
        else:
            Resp = "Login Failed"

    # close connection
    cursorVal.close()

    return jsonify({'LoginResponse': Resp}), 200


# REGISTER TO WEBSITE FUNCTIONALITY
@app.route('/Register', methods=['POST'])
@cross_origin()
def Register():
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    EmailId = json_data["EmailId"]
    Password = json_data["EmailId"]
    # Establishing connection
    conn = pymysql.connect(host="bcsdatabase.checsubgcuu9.ap-south-1.rds.amazonaws.com",
                           user="admin",
                           passwd="hackforpinkdb",
                           db="backend_bcs")
    cursorVal = conn.cursor()

    # Executing Query
    Query = "INSERT INTO `UserDetails` (`EmailId`,`Password`) VALUES (%s,%s)"
    cursorVal.execute(Query, (EmailId, Password))

    # Print Cursor Object
    print("Cursor Object: ", cursorVal)

    # commit changes
    conn.commit()

    # close connection
    cursorVal.close()

    return jsonify({'Response': "Registered Successfully"}), 200


# CHAT BOT FUNCTIONALITY
@app.route('/ChatBot/chat', methods=['POST'])
@cross_origin()
def Dictionary():
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    Question = json_data["Question"]
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

        "what is your name ": "My Name is Pink Bot",
        "Fix an appointment with doctor": "An appointment is Fixed with the Doctor tomorrow "

    }
    # Looping in Dictionary to Find Match
    for x in ChatDic:
        print(x, file=sys.stderr)
        if x == Question:
            Response = ChatDic.get(x)
            print(Response, file=sys.stderr)
            break
    if re.search(Question, "Fix an appointment with doctor"):
        CurrentDate = date.today() + timedelta(days=1)
        CurrentDate1 = str(CurrentDate)
        Response = "An appointment is Fixed with the Doctor on " + CurrentDate1 + " at 10 AM "

    return jsonify({'Answer': Response}), 200


# PROFILE DATA FUNCTIONALITY API CALL 1 TO CHECK
@app.route('/ProfileDataCheck', methods=['POST'])
@cross_origin()
def FetchProfileDataFunction():
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    EmailId = json_data["EmailId"]

    # Calling Get connection details to get cursor Object
    cursorVal = GetDbConnectionDetails()
    print(cursorVal)

    # Executing Query and store in count to check user EmailId present in db or not
    Query = "Select CLUSTERDATA, USERSCLUSTER from UserDetails where EmailId=%s"
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
            RespDict["ClusterData"] = row[0]
            RespDict["UserCluster"] = row[1]

    # close connection
    cursorVal.close()

    return jsonify(RespDict)


# PROFILE DATA FUNCTIONALITY API CALL 2 TO UPDATE DATA, IDENTIFY CLUSTER USING MACHINE LEARNING, FIND PROBABILITY
@app.route('/ProfileDataSubmission', methods=['POST'])
@cross_origin()
def ClusterIdentificationAndProbabilty():
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    EmailId = json_data["EmailId"]
    FirstName = json_data["UserName"]
    Age = json_data["Age"]
    Weight = json_data["Weight"]
    Symptoms = json_data["Symptoms"]
    Gender = json_data["Gender"]
    FoodHabit = json_data["FoodHabit"]
    FamilyHistoryOfCancer = json_data["FamilyHistoryOfCancer"]
    PersonaHistoryOfCancer = json_data["PersonaHistoryOfCancer"]
    AlcoholConsumption = json_data["AlcoholConsumption"]
    ExposureToRadiation = json_data["ExposureToRadiation"]
    BreastFeeding = json_data["BreastFeeding"]
    OccupationInvolvesPhysicalActivity = json_data["OccupationInvolvesPhysicalActivity"]
    Menopause = json_data["Menopause"]
    HarmonalUse = json_data["HarmonalUse"]
    Postmenopausal = json_data["Postmenopausal"]
    Pregnant = json_data["Pregnant"]
    Ethnicity = json_data["Ethnicity"]
    Height = json_data["Height"]
    DiagnosticTest = json_data["DiagnosticTest"]
    AgeOfFirstPregnancy = json_data["AgeOfFirstPregnancy"]
    WhichDiagnosticTest = json_data["WhichDiagnosticTest"]
    DiagnosticResultNegative = json_data["DiagnosticResultNegative"]

    # Changing to 1 or 0 based on input
    if FamilyHistoryOfCancer == "Yes":
        FamilyHistoryOfCancer = 1
    else:
        FamilyHistoryOfCancer = 0

    if PersonaHistoryOfCancer == "Yes":
        PersonaHistoryOfCancer = 1
    else:
        PersonaHistoryOfCancer = 0

    if AlcoholConsumption == "Yes":
        AlcoholConsumption = 1
    else:
        AlcoholConsumption = 0

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

    if DiagnosticResultNegative == "Yes":
        DiagnosticResultNegative = 0
    else:
        DiagnosticResultNegative = 1

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
        sc.transform([[Age, AlcoholConsumption, ExposureToRadiation, BreastFeeding, Menopause, Pregnant, OccupationInvolvesPhysicalActivity, 500, DiagnosticResultNegative, 1, 8, FamilyHistoryOfCancer, PersonaHistoryOfCancer, 0, AgeOfFirstPregnancy, 1]]))

    print(UserCluster)

    return jsonify({'UserCluster': "UserCluster"}), 200


# EXERCISE DATA FUNCTIONALITY API CALL 1 TO CHECK PREVIOUS EXERCISE DATA AND GAP
@app.route('/ExerciseDataCheck', methods=['POST'])
@cross_origin()
def ExerciseDataCheck():
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    EmailId = json_data["EmailId"]

    # Calling Get connection details to get cursor Object
    cursorVal = GetDbConnectionDetails()
    print(cursorVal)

    # Executing Query and store in count to check user EmailId present in db or not
    Query = "Select * from UserExcerciseData where EmailId=%s"
    Count = cursorVal.execute(Query, EmailId)

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
@app.route('/ExerciseDataUpdate', methods=['POST'])
@cross_origin()
def ExerciseDataUpdate():
    datetimeFormat = '%Y-%m-%d'
    LatestTimeStamp = date.today()
    # Fetching Json Request From FrontEnd
    json_data = flask.request.json
    EmailId = json_data["EmailId"]
    ExerciseDone = json_data["ExerciseDone"]
    CurrentDayCount = 0
    TimeStamp = ""

    # Set count as 0 initially
    TodayCount = 0

    if ExerciseDone == "Yes":
        TodayCount = 1
        CurrentDate = date.today()
        CurrentDateString = str(CurrentDate)

    # Establishing connection
    conn = pymysql.connect(host="bcsdatabase.checsubgcuu9.ap-south-1.rds.amazonaws.com",
                           user="admin",
                           passwd="hackforpinkdb",
                           db="backend_bcs")
    cursorVal = conn.cursor()

    # Executing Query and store in count to check user EmailId present in db or not
    Query = "Select * from UserExcerciseData where EmailId=%s"
    Count = cursorVal.execute(Query, EmailId)
    print(Count)

    # Find Day count and Gap for new user and old one
    if Count == 0:
        FinalDayCount = 1
        CurrentGap = 0
        Flag = 1

    else:
        # Fetch Record from CursorVal
        record = cursorVal.fetchall()
        print(record)
        # Loop to add data into dictionary
        for row in record:
            CurrentDayCount = row[1]
            CurrentGap = row[2]
            TimeStamp = row[3]

    # Calculate gap and Total Days Done and Update it in Database
    FinalDayCount = int(CurrentDayCount) + TodayCount
    CurrentGap = datetime.strptime(CurrentDateString, datetimeFormat) - datetime.strptime(TimeStamp, datetimeFormat)
    LatestTimeStamp = date.today()
    print("FinalDayCount", FinalDayCount)
    print("New Gap", CurrentGap)
    CurrentGap = str(CurrentGap)
    CurrentGap = CurrentGap[0:1]
    print(CurrentGap)

    # Update the Latest Values in Database and send Response
    Query = "UPDATE UserExcerciseData SET ExcerciseDayCount = %s, Gap = %s , TimeStamp= %s where EmailId=%s"

    Count = cursorVal.execute(Query, (FinalDayCount, CurrentGap, LatestTimeStamp, EmailId))

    # commit changes
    conn.commit()

    # close connection
    cursorVal.close()

    return jsonify({'DaysExercised': FinalDayCount, 'Gap': CurrentGap}), 200


# Main Function that specifies port,host etc
if __name__ == '__main__':
    app.run(host=None, port=5000, debug=True)
# Required to server from server
# serve(app, host='0.0.0.0', port=8080, threads=1)  # WAITRESS!

