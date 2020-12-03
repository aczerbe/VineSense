import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys

#plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

timeStart = 465.0

ids = [20, 19, 18, 17, 16, 15, 13, 21, 10, 9, 8, 7, 6, 5, 2]
ids = [13, 21, 10, 9, 8, 7, 6, 5, 2]

orients = {}
therms = {}
accel = {}
sht31 = {}

filename = sys.argv[1]# 'data_23_10_2020_19_39_26.csv'
def main():
	with open(filename) as file:
		for line in file:
			data = line.strip().split()
			if float(data[0]) < timeStart: # what we really mean by "at a time" is "closest after that time with all data"
				continue
			bandID = int(data[1])
			orients[bandID] = [float(x) for x in data[2:5]] # match ID and pos (assumption: IDs in order)
			therms[bandID] = [int(x) for x in data[8:12]]
			accel[bandID] = float(data[5])
			sht31[bandID] = [float(x) for x in data[6:8]]
			full = True
			for i in ids:
				if i not in orients:
					full = False
			if full:
				break
	positions = [[0, 0, 0]]
	k=0
	for bandID in ids:
        	k += 1
        	positions.append([sum(x) for x in zip(positions[k-1], orients[bandID])])
	xs = [row[0] for row in positions]
	ys = [row[1] for row in positions]
	zs = [row[2] for row in positions]
	temps = [sht31[x][0] for x in ids]
	humids = [sht31[x][1] for x in ids]
	accels = [accel[x] for x in ids]
	#thermtemps = [[therm_to_temp(t) for t in therms[x]] for x in ids]
	thermtemps = [[therm_to_temp(therms[x][t]) for x in ids] for t in range(4)]
	#real:
	#thermtemps = [[520, 521, 522, 521, 519, 518, 527, 526, 520, 515, 526, 522, 525, 515, 497], [508, 503, 505, 502, 500, 500, 530, 522, 510, 508, 528, 520, 531, 504, 495], [501, 501, 499, 499, 496, 496, 522, 684, 515, 509, 527, 524, 609, 508, 501], [493, 490, 488, 490, 488, 488, 524, 676, 504, 497, 503, 501, 528, 498, 491]]
	#just trial 1 with other values screwed for it:
	thermtemps = [[520, 521, 522, 521, 519, 518, 500, 500, 500, 500, 500, 500, 500, 500, 497], [508, 503, 505, 502, 500, 500, 500, 500, 510, 508, 500, 500, 500, 504, 540], [501, 501, 499, 499, 496, 496, 500, 500, 515, 509, 500, 500, 500, 508, 501], [493, 490, 488, 490, 488, 488, 500, 500, 504, 497, 503, 501, 500, 498, 491]]
	print(xs)
	print(positions)
	print(temps)
	print(accel)
	print(sht31)
	limit = len(ids)
	ax.plot(xs,ys,zs, 'o-')
	plt.title("shape")
	ax.set_xlim([-limit, limit])
	ax.set_ylim([-limit, limit])
	ax.set_zlim([-limit, limit])
	ax.set_xlabel("X")
	ax.set_ylabel("Y")
	ax.set_zlabel("Z")
	plt.figure()
	#plt.scatter(ids,accels)
	#plt.title("Jerk")
	#plt.figure()
	#plt.scatter(ids,temps, label="digital")
	#plt.scatter([ids.index(id) for id in ids], thermtemps[0], label="therm0")
	#plt.scatter([ids.index(id) for id in ids], thermtemps[1], label="therm1")
	#plt.scatter([ids.index(id) for id in ids], thermtemps[2], label="therm2")
	#plt.scatter([ids.index(id) for id in ids], thermtemps[3], label="therm3")
	#plt.title("temperatures")
	#plt.legend()
	#plt.figure()
	#plt.scatter(ids, humids)
	#plt.title("humidity")

	#fig, (ax1, ax2) = plt.subplots(2, 1,figsize=(10.9,3.2))

	#fig.subplots_adjust(hspace=0.05)
	#thermtemps = np.array(thermtemps)
	#ax1.imshow(thermtemps[:,0:15], cmap="hot", aspect="auto",interpolation="none")
	#print(thermtemps)
	
	#ax1.set_ylim(-0.5,3.5)
	#ax2.scatter([ids.index(id) for id in ids], humids)
	#ax2.set_ylim(0,100)
	#ax1.set_xticks([])
	#ax1.set_yticks([0,1,2,3])
	#ax1.set_xlim(-0.5,14.5)
	#ax2.set_xlim(-0.5,14.5)
	#ax2.set_xlabel("Band #",labelpad=0)
	##x1.set_xlabel("Band #")
	#ax1.set_ylabel("Thermistor #",labelpad=18)
	#ax1.set_title("Pipe Leak Measurement")
	#ax2.set_ylabel("Humidity (%)")

	plt.show()

def therm_to_temp(therm):
	r = 10* therm/ (1024 - therm) # convert to r in kOhms
	kelvin = 1/ (1/298.15 + 1/3380 * np.log(r/10))
	temp = kelvin - 273.15
	return therm


if __name__ == "__main__":
    main()