"""
    Example script go use the g3_simulator.py library to make a simulated CCAT g3 file.
    Written 9/10/24, ZBH
"""
import g3_simulator as sim
import so3g
from spt3g import core
import time
import numpy as np
import matplotlib.pyplot as plt

board_id = 'r1c1'          # simulating rfsoc 1 channel 1
timestream_length = 60     # simulating 60 second timestream
agg_time = 2.0             # 2 seconds per frame
n_chs = 576                # simulating 576 channels of I and Q data

save_dir = "./sim_data/"
n_frames = int(timestream_length / agg_time)

output_fname = save_dir+"newtimestamp.g3"

writer = core.G3Writer(filename=output_fname,append=True)
writer(sim.make_obs_frame(frame_num=0,start=True,board_id=board_id))
t_now = time.time()
for i in range(1, n_frames+1):
    writer(sim.make_data_frame(i,board_id,n_chs=n_chs,quanta=0.01, start_time=t_now))
    t_now += agg_time
writer(sim.make_obs_frame(frame_num=n_frames+1,start=False,board_id=board_id))
writer(core.G3Frame(core.G3FrameType.EndProcessing))
writer = None
 
ts = sim.load_timestream_from_sim_g3('./sim_data/newtimestamp.g3')
data = np.array(ts[2])

res_num = 0
plt.plot(ts[0]-ts[0][0], ts[2][res_num*2][:], label=f'{ts[1][res_num]} I')
plt.plot(ts[0]-ts[0][0], ts[2][res_num*2+1][:], label=f'{ts[1][res_num]} Q')

plt.savefig('./plots/IQ_view')
print(data.shape)
print(np.diff(ts[0]))