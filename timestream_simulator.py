import so3g
from spt3g import core
import numpy as np
import matplotlib.pyplot as plt
import time
import os

class Simulated_Timestream:
    """Class that simulates a timestream according to configs.
       Use this class rather than make_data_frame if want to simulate long timestreams
       that have realistic drifts
       
       Use generate_frames as a generator to slice timestream data into individual data frames
    """


    def __init__(self, length, n_chs, board_id='r1c1', samp_rate=1.0/488.0, start_time=time.time()) -> None:
        self.length = length
        self.n_chs = n_chs
        self.samp_rate = samp_rate
        self.cursor = 0
        self.frame_num = 0
        self.board_id = board_id

        self.times = start_time + samp_rate * np.arange(length / samp_rate)
        self.timestream = np.zeros(shape=(2*n_chs, len(self.times)))
        

        self.generate_timestream()

    
    def generate_timestream(self):
        '''function will be called during initialization to generate data
           If called again, will regenerate the data
        '''

        # Simulate channels one by one
        for chn in range(len(self.timestream)):
            self.timestream[chn] = np.random.normal(loc=1e6, scale=2000, 
                                                    size=len(self.times)).astype('float64')
            

    def generate_frames(self, agg_time, frame_start_num=0, dtype='float32', quanta=0.01):
        '''
           The length of the timestream in aggregated into a single frame is set by agg_time, and the 
           number of points is set by the time between each sample (t_samp = 1/f_samp where f_samp is
           set to 488 Hz by the RFSoC).

           start_time indicates what the first timestamp for the timestream should be in Unix time.
        
           Data type stored inside g3 files are specified by parameter dtype. Possible dtypes are int32
           float 32.

           Quanta sets the data precision that will be saved for the float data under compression.
           See so3g docs (https://so3g.readthedocs.io/en/latest/cpp_objects.html#how-to-work-with-float-arrays) for more info.  

        '''

        for num in range(int(self.length // agg_time)):
            ch_names = ["ch"+str(i).zfill(3) for i in range(1, self.n_chs+1)]
            endings = ["_I","_Q"]
            chs = [ch_name+ending for ch_name in ch_names for ending in endings]

            ts = so3g.G3SuperTimestream()
            ts.names = chs
            
            time_slice = self.times[self.cursor : self.cursor+ int(agg_time//self.samp_rate)]
            ts.times = core.G3VectorTime(time_slice * core.G3Units.s)

            if dtype == 'float32':
                ts.quanta = quanta * np.ones(len(chs)) # this is related to the data level to keep for the float under compression
            
            start_slice = int(self.cursor)
            end_slice = int(self.cursor+int(agg_time//self.samp_rate))


            dat = self.timestream[: , self.cursor : self.cursor+int(agg_time//self.samp_rate)]
            ts.data = dat
            
            frame = core.G3Frame(core.G3FrameType.Scan)
            frame['time'] = core.G3Time((self.times[self.cursor]+agg_time) * core.G3Units.s).time
            frame['board_id'] = core.G3String(self.board_id)
            frame['data'] = ts
            frame['num_samples'] = core.G3Int(len(ts.times))
            frame['timing_paradigm'] = core.G3String("Low Precision")
            frame['frame_num'] = core.G3Int(frame_start_num+num)

            self.cursor += int(agg_time//self.samp_rate)
            yield frame
