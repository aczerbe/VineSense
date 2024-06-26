import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
import time

matplotlib.use('TkAgg')

plt.ion()
fig = plt.figure(figsize=(10.8,7.2))
ax = fig.add_subplot(111, projection='3d')

#ids = [20, 19, 18, 17, 16, 15, 13, 21, 10, 9, 8, 7, 6, 2]
ids = [13, 21, 10, 9, 8, 7, 6, 5, 2]
#ids = [10, 9, 8, 7, 6, 2]

orients = {}
therms = {}
accel = {}
sht31 = {}




filename = sys.argv[1]# 'data_23_10_2020_19_39_26.csv'
def main():
	limit = len(ids)
	scale = 7.62
	timeStart = 870.0 #430
	plotline = ax.plot(np.zeros(limit),np.zeros(limit),np.zeros(limit), 'o-')[0]
	ax.set_xlim([-scale*limit, scale*limit])
	ax.set_ylim([-scale*limit, scale*limit])
	ax.set_zlim([-scale*limit, scale*limit])
	ax.set_xlabel("X")
	ax.set_ylabel("Y")
	ax.set_zlabel("Z")
	#ax.set_aspect('equal')
	plt.title("Shape Reconstruction")
	fig.canvas.draw()
	plt.show(block=False)
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
			#therms[bandID] = [int(x) for x in data[8:12]]
			#accel[bandID] = float(data[5])
			#sht31[bandID] = [float(x) for x in data[6:8]]
			full = True
			for i in ids:
				if i not in orients:
					full = False
					print("not full " + str(time.time()))
			if full:
				
				positions = [[0, 0, 0]]
				k = 0
				for bandID in ids:
					k += 1
					positions.append([sum(x) for x in zip(positions[k-1], [7.62*orient for orient in orients[bandID]])])
				xs = [row[0] for row in positions]
				ys = [row[1] for row in positions]
				zs = [row[2] for row in positions]
				#temps = [sht31[x][0] for x in ids]
				#humids = [sht31[x][1] for x in ids]
				#accels = [accel[x] for x in ids]
				#thermtemps = [[therm_to_temp(t) for t in therms[x]] for x in ids]
				#thermtemps = [[therm_to_temp(therms[x][t]) for x in ids] for t in range(4)]
				#print("t =" + str(timeStart))
				#print(xs)
				#print(positions)
				#print(temps)
				#print(accel)
				#print(sht31)
				
				plotline.set_xdata(xs)
				plotline.set_ydata(ys)
				plotline.set_3d_properties(zs)
				
				
				#plt.draw()
				#plt.show(block=False) 
				#print(delay)
				#k1 = time.time()
				#plt.pause(0.00001)
				#fig.canvas.draw()
				#ax.draw_artist(ax.patch)
				ax.draw_artist(plotline)
				#fig.canvas.update()
				#fig.canvas.blit(ax.bbox)
				fig.canvas.flush_events()

				k2 = time.time() - k1
				#print("actual delay time: " + str(k2))
				print(timeStart)
				#delay = animationTime - (time.time() - startTime)
				#time.sleep(.25)
				timeStart += (time.time() - startTime)/1
				

def therm_to_temp(therm):
	r = 10* therm/ (1024 - therm) # convert to r in kOhms
	kelvin = 1/ (1/298.15 + 1/3418 * np.log(r/10))
	temp = kelvin - 273.15
	return temp


if __name__ == "__main__":
	main()