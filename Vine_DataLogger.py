import serial
from scipy.spatial.transform import Rotation as R
import time
from datetime import date, datetime

def main():
	idStart = 15
	idEnd = 15


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
	zero = time.time()
	while True:
		data = arduino.readline()[:-2].decode("utf-8")	# Read serial data
		data = data.split()

		quat = getQuat(data)
		rot_q = R.from_quat(quat)
		bandId = int(data[0])
		thiscomp = compensators[bandId]
		pos = thiscomp.apply(rot_q.apply(vector), inverse=True)
		pos_str = ""
		for i in range(0,len(pos)):
			pos_str += "{:.7f}".format(pos[i]) + " "
		full_str = "{:.4f}".format(time.time() - zero) + " " + str(bandId) + " " + pos_str + " "
		for i in range(5,len(data)):
			full_str += data[i] + " "
		file.write(full_str + "\n")
		print(full_str)
		time.sleep(0.01)


def getQuat(data):
	quat = [float(data[2]),float(data[3]),float(data[4]),float(data[1])]
	return quat



if __name__ == "__main__":
    main()