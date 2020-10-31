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
	idStart = 15
	idEnd = 15
	counter = 0

	now = datetime.now()
	filename = now.strftime("data_%d_%m_%Y_%H_%M_%S.csv")
	file = open(filename, "w+")

	print("Vine Data Logger V1")
	input("Please calibrate IMUs for each band (indicator LED should be fully off), orient all bands in X-axis line, and then hit enter: ")
	print("Gathering compensation data.")

	arduino = serial.Serial('/dev/tty.usbmodem82406201', 115200, timeout=.1)
	vector = [1, 0, 0]
	compensators = {}
	ids = [*range(idStart, idEnd+1)]

	compensated = False

	while not compensated:
		data = arduino.readline()[:-2].decode("utf-8")	# Read serial data
		print(data)
		data = data.split()
		if len(data) != 12: # Bad serial read, skip to next line
			continue
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
	plt.ion()
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	plotline = ax.plot(np.zeros(idEnd-idStart + 1),np.zeros(idEnd-idStart + 1),np.zeros(idEnd-idStart + 1), 'o-')[0]
	ax.set_xlim([-1, 1])
	ax.set_ylim([-1, 1])
	ax.set_zlim([-1, 1])
	ax.set_xlabel("X")
	ax.set_ylabel("Y")
	ax.set_zlabel("Z")
	
	plt.title("Shape Reconstruction")
	fig.canvas.draw()
	plt.show(block=False)
	zero = time.time()
	while True:
		try:
			data = arduino.readline()[:-2].decode("utf-8")	# Read serial data
		except:
			continue

		data = data.split()

		quat = getQuat(data)
		rot_q = R.from_quat(quat)
		bandID = int(data[0])
		thiscomp = compensators[bandId]
		pos = thiscomp.apply(rot_q.apply(vector), inverse=True)
		orients[bandID] = pos
		pos_str = ""
		for i in range(0,len(pos)):
			pos_str += "{:.7f}".format(pos[i]) + " "
		full_str = "{:.4f}".format(time.time() - zero) + " " + str(bandID) + " " + pos_str + " "
		for i in range(5,len(data)):
			full_str += data[i] + " "
		file.write(full_str + "\n")
		print(full_str)

		positions = [[0, 0, 0]]
		for bandID in range(idStart, idEnd + 1):
			positions.append([sum(x) for x in zip(positions[bandID-idStart], orients[bandID])])
		xs = [row[0] for row in positions]
		ys = [row[1] for row in positions]
		zs = [row[2] for row in positions]
		counter += 1
		if(counter % 10 == 0):
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