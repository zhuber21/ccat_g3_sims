import so3g
from spt3g import core
import numpy as np
import matplotlib.pyplot as plt
import time
import os

def make_obs_frame(frame_num,start,board_id):
    """Makes observation frame for beginning and end of g3 file."""
    frame = core.G3Frame(core.G3FrameType.Observation)
    frame['time'] = core.G3Time(time.time() * core.G3Units.s).time    
    frame['frame_num'] = core.G3Int(frame_num)
    frame['board_id'] = core.G3String(board_id)
    if start:
        frame['stream_placement'] = core.G3String("start")
    else:
        frame['stream_placement'] = core.G3String("stop")
    return frame

def make_data_frame(frame_num, board_id, agg_time=2.0, t_samp=1.0/488.0, n_chs=2, dtype='float32', quanta=0.001, start_time=time.time()):
    """Makes a scan frame to hold timestream in the G3SuperTimestream object from so3g.
       Takes in an integer for the frame number, a board identifer string, and an integer for the
       number of resonator channels (n_chs).

       The length of the timestream in aggregated into a single frame is set by agg_time, and the 
       number of points is set by the time between each sample (t_samp = 1/f_samp where f_samp is
       set to 488 Hz by the RFSoC).

       start_time indicates what the first timestamp for the timestream should be in Unix time.
       
       Data type stored inside g3 files are specified by parameter dtype. Possible dtypes are int32
       float 32.

       Quanta sets the data precision that will be saved for the float data under compression.
       See so3g docs (https://so3g.readthedocs.io/en/latest/cpp_objects.html#how-to-work-with-float-arrays) for more info.  
       
    """
    times = start_time + t_samp * np.arange(agg_time / t_samp)
    ch_names = ["ch"+str(i).zfill(3) for i in range(1,n_chs+1)]
    endings = ["_I","_Q"]
    chs = [ch_name+ending for ch_name in ch_names for ending in endings]

    data = (np.random.normal(size=(len(chs),len(times))) * 100).astype(dtype)
    
    ts = so3g.G3SuperTimestream()
    ts.names = chs
    ts.times = core.G3VectorTime(times * core.G3Units.s)

    if dtype == 'float32':
        ts.quanta = quanta * np.ones(len(chs)) # this is related to the data level to keep for the float under compression
    
    ts.data = data
    
    frame = core.G3Frame(core.G3FrameType.Scan)
    frame['time'] = core.G3Time((start_time+agg_time) * core.G3Units.s).time
    frame['board_id'] = core.G3String(board_id)
    frame['data'] = ts
    frame['num_samples'] = core.G3Int(len(ts.times))
    frame['timing_paradigm'] = core.G3String("Low Precision")
    frame['frame_num'] = core.G3Int(frame_num)
    
    return frame

def load_timestream_from_sim_g3(fname):
    """A quick homemade function for stiching a full timestream back together from
       across frames in one of my simulated g3 files.
       
       Takes in path to g3 file (fname) and returns times,names,data for the full file.
       Assumes names are the same for each frame in file."""
    frames = []
    for frame in core.G3File(fname):
        frames.append(frame)
    to_store = []
    for i in range(len(frames)):
        if(frames[i].type==core.G3FrameType.Scan):
            to_store.append(frames[i]['data'])

    combined_times = np.hstack(list(to_store[i].times for i in range(len(to_store))))
    combined_data = np.hstack(list(to_store[i].data for i in range(len(to_store))))
    
    return combined_times,frames[1]['data'].names,combined_data