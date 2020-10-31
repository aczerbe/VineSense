import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


data = []

with open('data_01_07_2020_11_14_38.csv') as file:
	for line in file:
		data.append([float(k) for k in line.strip().split()])

for vec in data:
	ax.set_xlim([-1, 1])
	ax.set_ylim([-1, 1])
	ax.set_zlim([-1, 1])
	ax.quiver([0], [0], [0], vec[0], vec[1], vec[2])
	plt.draw()
	plt.pause(0.001)
	ax.cla()
