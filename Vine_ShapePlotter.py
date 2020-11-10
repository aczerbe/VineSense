import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys

#plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

idStart = 2
idEnd = 2

timeStart = 40

ids = [*range(idStart, idEnd+1)]

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

	for bandID in range(idStart, idEnd + 1):
		positions.append([sum(x) for x in zip(positions[bandID-idStart], orients[bandID])])
	xs = [row[0] for row in positions]
	ys = [row[1] for row in positions]
	zs = [row[2] for row in positions]
	temps = [sht31[x][0] for x in ids]
	humids = [sht31[x][1] for x in ids]
	accels = [accel[x] for x in ids]
	#thermtemps = [[therm_to_temp(t) for t in therms[x]] for x in ids]
	thermtemps = [[therm_to_temp(therms[x][t]) for x in ids] for t in range(4)]
	print(xs)
	print(positions)
	print(temps)
	print(accel)
	print(sht31)
	ax.plot(xs,ys,zs, 'o-')
	plt.title("shape")
	ax.set_xlim([-limit, limit])
	ax.set_ylim([-limit, limit])
	ax.set_zlim([-limit, limit])
	ax.set_xlabel("X")
	ax.set_ylabel("Y")
	ax.set_zlabel("Z")
	plt.figure()
	plt.scatter(ids,accels)
	plt.title("Jerk")
	plt.figure()
	plt.scatter(ids,temps, label="digital")
	plt.scatter(ids, thermtemps[0], label="therm0")
	plt.scatter(ids, thermtemps[1], label="therm1")
	plt.scatter(ids, thermtemps[2], label="therm2")
	plt.scatter(ids, thermtemps[3], label="therm3")
	plt.title("temperatures")
	plt.legend()
	plt.figure()
	plt.scatter(ids, humids)
	plt.title("humidity")
	plt.show()

def therm_to_temp(therm):
	r = 10* therm/ (1024 - therm) # convert to r in kOhms
	kelvin = 1/ (1/298.15 + 1/3380 * np.log(r/10))
	temp = kelvin - 273.15
	return temp


if __name__ == "__main__":
    main()