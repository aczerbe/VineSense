import serial
from scipy.spatial.transform import Rotation as R
import numpy as np
import time
from datetime import date, datetime
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

matplotlib.use('qt4Agg')


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

    arduino = serial.Serial('/dev/tty.usbmodem82403901', 115200, timeout=.1)
    vector = [1, 0, 0]
    compensators = {}
    ids = [21, 20, 19, 18, 17, 16, 15, 13, 12, 10, 9, 8, 7, 6, 5, 2]
    ids = [22, 20, 19, 18, 17, 16, 13, 21, 10, 9, 8, 7, 6, 5, 2]

    compensated = False

    while not compensated:
        rawdata = arduino.readline()[:-2].decode("utf-8")    # Read serial data
        data = rawdata.split()
        if len(data) != 12: # Bad serial read, skip to next line
            continue
        print(rawdata)
        bandID = int(data[0])
        quat = getQuat(data)
        rotation_compensator = R.from_quat(quat)
        compensators[bandID] = rotation_compensator
        compensated = True
        for i in ids:
            if i not in compensators:
                compensated = False

    print("Compensation data gathered.")
    input("hit enter to start logging:")
    print("Starting logging, t=0")
    file = open(filename, "w+")
    
    fig, (ax1, ax2) = plt.subplots(2, 1)
    plt.ion()
    ax3 = ax2.twinx()
    #ax.set_aspect('equal')
    #ax.auto_scale_xyz([-limit, limit], [-limit, limit], [-limit, limit])
    
    fig.canvas.draw()
    plt.show(block=False)
    t0 = ax1.scatter(ids, [0]*len(ids), label="therm0")
    t1 = ax1.scatter(ids, [0]*len(ids), label="therm1")
    t2 = ax1.scatter(ids, [0]*len(ids), label="therm2")
    t3 = ax1.scatter(ids, [0]*len(ids), label="therm3")
    ax1.set_title("Thermistor values")
    ax1.legend()
    ax1.set_ylim(400,600)
    ax1.set_xlim(-1,len(ids))
    ax1.set_ylabel("Thermistor counts (0-1024)")
    tmp = ax2.scatter(ids, [0]*len(ids), c='b')
    hmd = ax3.scatter(ids, [0]*len(ids), c='r')
    ax2.set_ylabel("Temp (c)", color='b')
    ax2.set_ylim(0,60)
    ax2.set_title("Temp/humidity")
    ax3.set_ylabel("humidity (%)", color='r')
    ax3.set_ylim(0,100)
    ax3.set_xlim(-1,len(ids))
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
        accel[bandID] = float(data[5])
        sht31[bandID] = [float(x) for x in data[6:8]]
        pos_str = ""
        for i in range(0,len(pos)):
            pos_str += "{:.7f}".format(pos[i]) + " "
        full_str = "{:.4f}".format(time.time() - zero) + " " + str(bandID) + " " + pos_str + " "
        for i in range(5,len(data)):
            full_str += data[i] + " "
        file.write(full_str + "\n")
        #print(full_str)
        counter += 1
        if(counter % 20 == 0):
            t0.set_offsets([[ids.index(id),therms[id][0]] for id in ids])
            t1.set_offsets([[ids.index(id),therms[id][1]] for id in ids])
            t2.set_offsets([[ids.index(id),therms[id][2]] for id in ids])
            t3.set_offsets([[ids.index(id),therms[id][3]] for id in ids])
            tmp.set_offsets([[ids.index(id), sht31[id][0]] for id in ids])
            hmd.set_offsets([[ids.index(id), sht31[id][1]] for id in ids])
            fig.suptitle("Heat data, t=" + "{:.4f}".format(time.time() - zero))
            fig.canvas.flush_events()


def getQuat(data):
    quat = [float(data[2]),float(data[3]),float(data[4]),float(data[1])]
    return quat

def therm_to_temp(therm):
    r = 10* therm/ (1024 - therm) # convert to r in kOhms
    kelvin = 1/ (1/298.15 + 1/3418 * np.log(r/10))
    temp = kelvin - 273.15
    return temp

if __name__ == "__main__":
    main()
