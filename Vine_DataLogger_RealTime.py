import serial
from scipy.spatial.transform import Rotation as R
import numpy as np
import time
from datetime import date, datetime
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

matplotlib.use('TkAgg')



orients = {}

def main():
    #idStart = 15
    #idEnd = 15
    counter = 0

    now = datetime.now()
    filename = now.strftime("data_%d_%m_%Y_%H_%M_%S.csv")
    

    print("Vine Data Logger V1")
    input("Please calibrate IMUs for each band (indicator LED should be fully off), orient all bands in X-axis line, and then hit enter: ")
    print("Gathering compensation data...")

    arduino = serial.Serial('/dev/tty.usbmodem82406201', 115200, timeout=.1)
    vector = [1, 0, 0]
    compensators = {}
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
    fig = plt.figure(figsize=plt.figaspect(1.0))
    ax = fig.add_subplot(111, projection='3d')
    plotline = ax.plot(np.zeros(len(ids)),np.zeros(len(ids)),np.zeros(len(ids)), 'o-')[0]
    #plotline2 = ax.plot(np.zeros(len(ids)),np.zeros(len(ids)),np.zeros(len(ids)), 'o-')[0]
    #plotline3 = ax.plot(np.zeros(len(ids)),np.zeros(len(ids)),np.zeros(len(ids)), 'o-')[0]
    limit = len(ids)
    ax.set_ylim([-limit, limit])
    ax.set_zlim([-limit, limit])
    ax.set_xlim([-limit, limit])
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    #ax.set_aspect('equal')
    #ax.auto_scale_xyz([-limit, limit], [-limit, limit], [-limit, limit])
    plt.title("Shape Reconstruction")
    fig.canvas.draw()
    plt.show(block=False)
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
        thiscomp = compensators[bandId]
        pos1 = thiscomp.apply(rot_q.apply(vector), inverse=True)
        pos = thiscomp.apply(rot_q.apply(thiscomp.apply(vector)), inverse=True)
        pos_no = rot_q.apply(vector)
        orients[bandID] = pos
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
        positions = [[0, 0, 0]]
        if full:
        	k = 0
        	for bandID in ids:
        		k += 1
        		positions.append([sum(x) for x in zip(positions[k-1], orients[bandID])])

        xs = [row[0] for row in positions]
        ys = [row[1] for row in positions]
        zs = [row[2] for row in positions]
        #print(positions)
        counter += 1
        if(counter % 50 == 0):
            plotline.set_xdata(xs)
            plotline.set_ydata(ys)
            plotline.set_3d_properties(zs)
            ax.draw_artist(plotline)
            fig.canvas.flush_events()
        #time.sleep(0.01)


def getQuat(data):
    quat = [float(data[2]),float(data[3]),float(data[4]),float(data[1])]
    return quat



if __name__ == "__main__":
    main()
