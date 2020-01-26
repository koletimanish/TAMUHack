import numpy as np
import mysql.connector
from twilio.rest import Client


def pull_data():
    lats = []
    longs = []
    brights = []
    cons = []

    mydb = mysql.connector.connect(
        host="35.224.55.199",
        user="root",
        passwd="tamuhack",
        database="bushfire"
    )

    mycursor = mydb.cursor()

    # mycursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'naemergen'")
    # myresult_emergency = mycursor.fetchall()
    # print(myresult_emergency)
    # AUSTRALIA

    mycursor.execute("SELECT Latitude, Longitude, bright_ti4, confidence FROM ausfire24")
    myresult_aus = mycursor.fetchall()

    for x in myresult_aus:
        lats.append(x[0])
        longs.append(x[1])
        brights.append(x[2])
        cons.append(x[3])

    # NORTH AMERICA
    mycursor.execute("SELECT Latitude, Longitude, bright_ti4, confidence FROM nafire24")
    myresult_na = mycursor.fetchall()
    for x in myresult_na:
        lats.append(x[0])
        longs.append(x[1])
        brights.append(x[2])
        cons.append(x[3])

    # SOUTH AMERICA
    mycursor.execute("SELECT Latitude, Longitude, bright_ti4, confidence FROM safire24")
    myresult_sa = mycursor.fetchall()
    for x in myresult_sa:
        lats.append(x[0])
        longs.append(x[1])
        brights.append(x[2])
        cons.append(x[3])

    mycursor.execute("SELECT name, phone, longitude, latitude FROM ausemergency")
    myresult_emaus = mycursor.fetchall()
    names = []
    comps = []
    phones = []
    em_longs = []
    em_lats = []
    for x in myresult_emaus:
        names.append(x[0])
        phones.append(x[1])
        em_longs.append(x[2])
        em_lats.append(x[3])

    mycursor.execute("SELECT Owner, Name, latitude, longitude FROM naemergen")
    myresult_emaus = mycursor.fetchall()
    for x in myresult_emaus:
        names.append(x[0])
        phones.append(x[1])
        em_longs.append(x[2])
        em_lats.append(x[3])

    return lats, longs, brights, names, comps, phones, em_longs, em_lats


def find_fires(user_lat, user_long, rad, lats, longs, brights):
    c_earth = 24901.
    lats = np.array(lats)
    longs = np.array(longs)
    brights = np.array(brights)

    res_theta = (rad / c_earth) * 360.
    dlat = lats - user_lat
    dlong = longs - user_long
    dist = np.square(dlat) + np.square(dlong)
    indx = np.where(dist <= (res_theta ** 2))
    indx = indx[0]
    if len(indx) > 0:
        res_brights = brights[indx]
        intense_count = len(np.where(res_brights > 320)[0])
        fire_count = len(res_brights)
    else:
        fire_count = 0
        intense_count = 0
    return fire_count, intense_count


def nearest_emergency(user_lat, user_long, rad, names, comps, phones, em_longs, em_lats):
    lats = np.array(em_lats)
    longs = np.array(em_longs)
    names = np.array(names)
    phones = np.array(phones)

    dlat = lats - user_lat
    dlong = longs - user_long
    dist = np.sqrt(np.square(dlat * 69) + np.square(dlong * 69))
    indx = np.where(dist == np.min(dist))
    indx = np.max(indx)

    return dist[indx], phones[indx]


### add input
mylat = 30.6188
mylong = -96.3365

myrad = 10.0
data = pull_data()

numfires, numintense = find_fires(mylat, mylong, myrad, data[0], data[1], data[2])
[em_dist, em_phone] = nearest_emergency(mylat, mylong, myrad, data[3], data[4], data[5], data[6], data[7])


print(f"There are {numfires} fires near you. There are {numintense} ones. Closest emergency center "
      f"is {round(em_dist)}km away and their number is {em_phone}")


account_sid = 'ACaf4573efc8eab921505cdb82cb258006'
auth_token = '2e8394f33ad52a0c5b98722b1d82583e'
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body=f"There are {numfires} fires near you ({numintense} intense ones)."
                          f"Closest emergency center is {round(em_dist)}km away and their number is {em_phone}",
                     from_='+12018907595',
                     to='+13188346207'
                 )
