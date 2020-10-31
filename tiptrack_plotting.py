import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

data = []

VELOCITY = 0.003

with open('data_08_07_2020_18_08_16.csv') as file:
	for line in file:
		data.append([float(k) for k in line.strip().split()])

path = [[0,0,0]]

for i in range(1, len(data)+1):
	disp = [a*VELOCITY for a in data[i-1]]
	path.append([sum(x) for x in zip(path[i-1], disp)])

xs = [a[0] for a in path]
ys = [a[1] for a in path]
zs = [a[2] for a in path]

ax.set_autoscale_on(False)
ax.plot3D(xs,ys,zs)
plt.show()
Axes3D.plot()
