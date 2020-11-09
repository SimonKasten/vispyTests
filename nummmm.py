import numpy as np

# pre allocate 1000 float values for X, Y

len_buff = 1000
daq_buf = np.empty((len_buff, 2), np.float32)


daq_buf[:401, 0] = np.linspace(0, 1000, 401)
daq_buf[:401, 1] = np.random.normal(0.0, 0.5, 401)

print(daq_buf[:, 0])  # X
print(daq_buf[:, 1])  # Y


daq_buf = np.append(daq_buf, np.empty((len_buff, 2), np.float32), axis=0)
daq_buf = np.append(daq_buf, np.empty((len_buff, 2), np.float32), axis=0)

print(daq_buf[:, 0])  # X
print(daq_buf[:, 1])  # Y
print(len(daq_buf))