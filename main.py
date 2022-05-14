import shutil
import os
import sqlite3
import cv2
import numpy as np
import face_recognition

def listUsers():
    conn = sqlite3.connect('facedb.db')

    tab1 = "NIK"
    tab2 = "NAMA"
    print(f"{str(tab1):10s} | {tab2:10s}")

    cursor = conn.execute("select * from users")
    for row in cursor:
        print(f"{str(row[0]):10s} | {row[1]:10s}")

    conn.close()

def tambahUser():
    try:
        conn = sqlite3.connect('facedb.db')

        nik = input("NIK : ")
        nama = input("NAMA : ")
        path_file = input("FULL PATH FILE : ")

        data = conn.cursor()
        data = conn.execute("SELECT count(*) as jml from users where nik = '" + nik + "';")
        record = data.fetchone()

        if int(record[0]) > 0:
            print("Gunakan NIK lain")
        else:
            # cek apakah dia nama filenya kembar
            nama_file = os.path.basename(path_file)
            dest_file = os.path.abspath(os.getcwd()) + "\\images\\" + nama_file
            file_exists = os.path.exists(dest_file)
            if file_exists:
                print("Rename nama file anda")
            else:
                shutil.copyfile(path_file, dest_file)

                # insert into database
                cur = conn.cursor()
                cur.execute("insert into users values ('" + nik + "', '" + nama + "', '" + dest_file + "')")
                conn.commit()
                print("Upload success")

        cur.close()

    except:
        print("An exception occurred")

def deleteData():
    try:
        conn = sqlite3.connect('facedb.db')

        kode = input("NIK : ")

        data = conn.cursor()
        data = conn.execute("SELECT path from users where nik = '" + kode + "';")
        record = data.fetchone()

        file_exists = os.path.exists(record[0])
        if file_exists:
            os.remove(record[0])

        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE nik = '" + kode + "';")
        conn.commit()
        cur.close()

    except:
        print("An exception occurred")

def showFile():
    try:
        conn = sqlite3.connect('facedb.db')

        kode = input("NIK : ")

        data = conn.cursor()
        data = conn.execute("SELECT nik, nama, path from users where nik = '" + kode + "';")
        record = data.fetchone()

        file_exists = os.path.exists(record[2])
        if file_exists:
            img = cv2.imread(record[2], cv2.IMREAD_COLOR)
            cv2.imshow(record[0] + "-" + record[1], img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        else:
            print("File not exist")

    except:
        print("An exception occurred")

def menu1():
    kondisi_menu1 = True
    while kondisi_menu1:
        print("======== SUBMENU ========")
        print("1. List Users")
        print("2. Add Users")
        print("3. Show File")
        print("4. Delete Users")
        print("5. Exit sub menu")
        print("-------------------------")
        print("Choose menu [1,2,3,4,5]")
        sub_pilih_1 = int(input("Menu : "))
        if sub_pilih_1 == 1:
            listUsers()

        elif sub_pilih_1 == 2:
            tambahUser()

        elif sub_pilih_1 == 3:
            showFile()

        elif sub_pilih_1 == 4:
            deleteData()

        elif sub_pilih_1 == 5:
            kondisi_menu1 = False
        else:
            print("Pilih menu 1 / 2 / 3 / 4 / 5")

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

def menu2():

    images = []
    classNames = []

    conn = sqlite3.connect('facedb.db')

    cursor = conn.execute("select * from users")
    for row in cursor:
        curImg = cv2.imread(f'{row[2]}')
        images.append(curImg)
        classNames.append(row[1])

    conn.close()

    encodeListKnown = findEncodings(images)
    print("Encoding Complete")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
            else:
                name = "Unknown"

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow('Webcam', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release();
            cv2.destroyAllWindows();
            break;

kondisi = True
while kondisi:
    print("======== MENU ========")
    print("1. Training Data")
    print("2. Face Identification")
    print("3. Exit")
    print("----------------------")
    print("Choose menu [1,2,3]")
    pilih = int(input("Menu : "))
    if pilih == 1:
        menu1()

    elif pilih == 2:
        menu2()

    elif pilih == 3:
        kondisi = False

    else:
        print("Pilih menu 1 / 2 / 3")
