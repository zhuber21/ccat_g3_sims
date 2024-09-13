"""
    Example script go use the g3_simulator.py library to make a simulated CCAT g3 file.
    Written 9/10/24, ZBH
"""
import g3_simulator as sim
from spt3g import core

board_id = 'r1c1'          # simulating rfsoc 1 channel 1
timestream_length = 1.0   # simulating 60 second timestream
agg_time = 2.0             # 2 seconds per frame
n_chs = 576                # simulating 576 channels of I and Q data

save_dir = "/home/pc/Documents/g3_files/"
n_frames = int(timestream_length / agg_time)

output_fname = save_dir+"one_second_576_chs_smaller_quanta_test.g3"

writer = core.G3Writer(filename=output_fname,append=True)
writer(sim.make_obs_frame(frame_num=0,start=True,board_id=board_id))
for i in range(1, n_frames+1):
    writer(sim.make_data_frame(i,board_id,n_chs=n_chs,quanta=0.01))
    time.sleep(agg_time)
writer(sim.make_obs_frame(frame_num=n_frames+1,start=False,board_id=board_id))
writer(core.G3Frame(core.G3FrameType.EndProcessing))
writer = None
