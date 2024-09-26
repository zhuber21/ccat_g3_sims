import g3_simulator as sim
import so3g
from spt3g import core
import time
import numpy as np
import matplotlib.pyplot as plt
from timestream_simulator import Simulated_Timestream



board_id = 'r1c1'          # simulating rfsoc 1 channel 1
timestream_length = 60     # simulating 60 second timestream
agg_time = 2.0             # 2 seconds per frame
n_chs = 576                # simulating 576 channels of I and Q data

save_dir = "./sim_data/"
file_name = 'timestream.g3'

output_fname = save_dir+file_name
n_frames = int(timestream_length / agg_time)

TS = Simulated_Timestream(length=timestream_length, n_chs = n_chs)

writer = core.G3Writer(filename=output_fname,append=True)
writer(sim.make_obs_frame(frame_num=0,start=True,board_id=board_id))

for frame in TS.generate_frames(agg_time=agg_time,frame_start_num=1):
    
    writer(frame)


writer(sim.make_obs_frame(frame_num=n_frames+1,start=False,board_id=board_id))
writer(core.G3Frame(core.G3FrameType.EndProcessing))
writer = None
 
ts = sim.load_timestream_from_sim_g3(f'./sim_data/{file_name}')

data = np.array(ts[2])
res_num = 0

plt.figure()
times = (ts[0] - ts[0][0]) /  core.G3Units.s
plt.plot(times, data[0][:], label='D1 I')
plt.plot(times, data[1][:], label='D1 Q')

plt.savefig('./plots/IQ_view')




