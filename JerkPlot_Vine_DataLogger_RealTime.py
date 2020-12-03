import serial
from scipy.spatial.transform import Rotation as R
import numpy as np
import time
from datetime import date, datetime
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math

matplotlib.use('TkAgg')


orients = {}
therms = {}
accel = {}
sht31 = {}

def main():
    #idStart = 15
    #idEnd = 15
    counter = 0

    now = datetime.now()
    filename = now.strftime("data_%d_%m_%Y_%H_%M_%S.csv")
    

    print("Vine Data Logger V1")
    input("Please calibrate IMUs for each band (indicator LED should be fully off), orient all bands in X-axis line, and then hit enter: ")
    print("Gathering compensation data...")

    arduino = serial.Serial('/dev/tty.usbmodem82406201', 115200, timeout=.1) #3901
    vector = [1, 0, 0]
    compensators = {}
    #ids = [21, 20, 19, 18, 17, 16, 15, 13, 12, 10, 9, 8, 7, 6, 5, 2]
    ids = [15]

    compensated = False

    while not compensated:
        rawdata = arduino.readline()[:-2].decode("utf-8")    # Read serial data
        data = rawdata.split()
        if len(data) != 12: # Bad serial read, skip to next line
            continue
        print(rawdata)
        bandId = int(data[0])
        quat = getQuat(data)
        rotation_compensator = R.from_quat(quat)
        compensators[bandId] = rotation_compensator
        compensated = True
        for i in ids:
            if i not in compensators:
                compensated = False

    print("Compensation data gathered.")
    input("hit enter to start logging:")
    print("Starting logging, t=0")
    file = open(filename, "w+")
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot()
    #ax.set_aspect('equal')
    #ax.auto_scale_xyz([-limit, limit], [-limit, limit], [-limit, limit])
    
    fig.canvas.draw()
    plt.show(block=False)
    jerk = ax.scatter(ids, [0.1]*len(ids))
    ax.set_title("Jerk values")
    #plt.yscale('log')
    ax.set_ylim(0,50)
    ax.set_xlim(-1,len(ids))

    #plt.title("Temp sensor data, t=0", loc='center')
    zero = time.time()

    while True:

        try:
            data = arduino.readline()[:-2].decode("utf-8")    # Read serial data
        except:
            print("bad packet")
            continue

        data = data.split()
        if len(data) != 12: # Bad serial read, skip to next line
            try:
                print("incomplete packet from id :" + str(data[0]))
            except:
                print("empty packet")
            continue

        quat = getQuat(data)
        rot_q = R.from_quat(quat)
        bandID = int(data[0])
        thiscomp = compensators[bandID]
        pos = thiscomp.apply(rot_q.apply(vector), inverse=True)
        orients[bandID] = pos
        therms[bandID] = [int(x) for x in data[8:12]]
        accel[bandID] = accel_to_jerk(float(data[5]))
        sht31[bandID] = [float(x) for x in data[6:8]]
        pos_str = ""
        for i in range(0,len(pos)):
            pos_str += "{:.7f}".format(pos[i]) + " "
        full_str = "{:.4f}".format(time.time() - zero) + " " + str(bandID) + " " + pos_str + " "
        for i in range(5,len(data)):
            full_str += data[i] + " "
        file.write(full_str + "\n")
        #print(full_str)
        full = True
        for i in ids:
            if i not in orients:
                full = False
        counter += 1
        if full:
            if(counter % 10 == 0):
                jerk.set_offsets([[ids.index(id),accel_to_jerk(accel[id])] for id in ids])
                fig.suptitle("Jerk data, t=" + "{:.4f}".format(time.time() - zero))
                fig.canvas.flush_events()
                counter = 0
                print(accel[15])


def getQuat(data):
    quat = [float(data[2]),float(data[3]),float(data[4]),float(data[1])]
    return quat

def therm_to_temp(therm):
    r = 10* therm/ (1024 - therm) # convert to r in kOhms
    kelvin = 1/ (1/298.15 + 1/3418 * np.log(r/10))
    temp = kelvin - 273.15
    return temp

def accel_to_jerk(accel):
    return math.pow(accel/.5,1.5)

if __name__ == "__main__":
    main()
