import serial
from scipy.spatial.transform import Rotation as R
import math
import numpy as np
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import date, datetime

now = datetime.now()
filename = "data_" + now.strftime("%d_%m_%Y_%H_%M_%S.csv")
file = open(filename, "w+")

loop = False
iterator = 0

arduino = serial.Serial('/dev/cu.usbmodem14201', 115200, timeout=.1)
vector = [0, 1, 0]
rotation_compensator = R.from_matrix([[1,0,0],[0,1,0],[0,0,1]])
while True:
	data = arduino.readline()[:-2].decode("utf-8")	# Read serial data
	data = data.split()
	if len(data) != 6: # Startup messages
		continue
	if(int(data[0]) < 3 or int(data[1]) < 2):	# Not calibrated
		print("gyro: " + data[0] + " mag: " + data[1])
		# iterator = 0
		# loop = False
		continue
	quat = [float(data[i]) for i in range(2,6)]
	if sum(quat) == 0:	# No actual data yet
		continue
	if iterator < 300:
		print("waiting to compensate... " + str(iterator))
		iterator += 1
		continue
	rot_q = R.from_quat(quat)
	if not loop:
		rotation_compensator = rot_q
		loop = True
		continue
	# pos = rot_q.apply(rotation_compensator.apply(vector, inverse=True))
	pos = rotation_compensator.apply(rot_q.apply(vector), inverse=True)
	pos_str = "{:.7f}".format(pos[0]) + " " + "{:.7f}".format(pos[1]) + " " + "{:.7f}".format(pos[2])
	file.write(pos_str + "\n")
	print(pos_str)
	time.sleep(0.01)

	# v = [25.55,0,0]		 dist from center of sphere to tip of rod

def rotation_matrix_from_vectors(vec1, vec2):
    """ Find the rotation matrix that aligns vec1 to vec2
    :param vec1: A 3d "source" vector
    :param vec2: A 3d "destination" vector
    :return mat: A transform matrix (3x3) which when applied to vec1, aligns it with vec2.
    """
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))