import datetime
import pytz

time_format = "%H:00"
date_format = "%-d-%-m-%Y"
tz = pytz.timezone('Asia/Kuala_Lumpur')
ctime = datetime.datetime.now(tz)
time = datetime.datetime.strftime(ctime, time_format)
date = datetime.datetime.strftime(ctime, date_format)

lebir = {
    'input_station': ['Gunung Gagau1', 'Kampung Aring', 'Kampung Laloh', 'Kampung Tualang'],
    'station_name': "Sg.Lebir di Tualang",
    'formula': "23.2*(math.pow(gagau,0.005584)*math.pow(Laloh, 0.001087)*math.pow(aring, 0.004091)*math_pow(tualang, 0.005534))",
    'time': time,
    'date': date,
}

kuala_krai = {
    'input_station': ['Dabong', 'Kampung Laloh', 'Kuala Krai'],
    'station_name': "Sg.Kelantan di Kuala Krai",
    'formula': "16.5*(math.pow(dabong, 0.0096)*math.pow(laloh, 0.000632)*math.pow(krai, 0.012563)",
    'time': time,
    'date': date,
}

kusial = {
    'input_station': ['Kuala Krai', ],
    'station_name': "Sg.Kelantan di Kusial",
    'formula': "8.13*(math.pow(krai, 0.03))",
    'time': time,
    'date': date,
}


