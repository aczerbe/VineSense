import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
import time

matplotlib.use('TkAgg')

plt.ion()
#fig = plt.figure(figsize=(10.8,7.2))
#ax = fig.add_subplot(111, projection='3d')

ids = [20, 19, 18, 17, 16, 15, 13, 21, 10, 9, 8, 7, 6, 5, 2]
#ids = [13, 21, 10, 9, 8, 7, 6, 5, 2]
#ids = [10, 9, 8, 7, 6, 2]

orients = {}
therms = {}
accel = {}
sht31 = {}




filename = sys.argv[1]# 'data_23_10_2020_19_39_26.csv'
def main():
	limit = len(ids)
	timeStart = 0.0 #430
	fig, (ax1, ax2) = plt.subplots(2, 1,figsize=(10.9,3.2))
	fig.subplots_adjust(hspace=0.05)
	fig.canvas.draw()
	thermtemps = np.zeros((4,len(ids)))
	im = ax1.imshow(thermtemps, cmap="hot", aspect="auto",interpolation="none")
	print(thermtemps)
	
	ax1.set_ylim(-0.5,3.5)
	hmd = ax2.scatter([ids.index(id) for id in ids], np.zeros(limit))
	ax2.set_ylim(0,100)
	ax1.set_xticks([])
	ax1.set_yticks([0,1,2,3])
	ax1.set_xlim(-0.5,14.5)
	ax2.set_xlim(-0.5,14.5)
	ax2.set_xlabel("Band #",labelpad=0)
	#x1.set_xlabel("Band #")
	ax1.set_ylabel("Thermistor #",labelpad=18)
	ax1.set_title("Pipe Leak Measurement")
	ax2.set_ylabel("Humidity (%)")
	plt.show()
	with open(filename) as file:
		for line in file:
			#ax.cla()
			startTime = time.time()
			k1 = startTime
			data = line.strip().split()
			if float(data[0]) < timeStart: # what we really mean by "at a time" is "closest after that time with all data"
				continue
			bandID = int(data[1])
			orients[bandID] = [float(x) for x in data[2:5]] # match ID and pos (assumption: IDs in order)
			therms[bandID] = [int(x) for x in data[8:12]]
			
			#accel[bandID] = float(data[5])
			sht31[bandID] = [float(x) for x in data[6:8]]
			full = True
			for i in ids:
				if i not in orients:
					full = False
					print("not full " + str(time.time()))
			if full:
				thermtemps = [[therm_to_temp(therms[x][t]) for x in ids] for t in range(4)]
				print('full')
				hmd.set_offsets([[ids.index(id), sht31[id][1]] for id in ids])
				im = ax1.imshow(thermtemps, cmap="hot", aspect="auto",interpolation="none")
				#print(thermtemps)
				fig.canvas.flush_events()
				timeStart += (time.time() - startTime)/3
				

def therm_to_temp(therm):
	r = 10* therm/ (1024 - therm) # convert to r in kOhms
	kelvin = 1/ (1/298.15 + 1/3418 * np.log(r/10))
	temp = kelvin - 273.15
	return therm


if __name__ == "__main__":
	main()