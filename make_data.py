import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import hvplot.pandas
import matplotlib.pyplot as plt
import numpy as np
import os

AXIS = ['C1', 'C2']
SHOTS = np.arange(4000, 4040)

np.random.seed(1)
SENSOR_SHOTS = {
    'C1': {
        'Sensor_1': np.random.choice(SHOTS, 19, replace=False),
        'Sensor_2': np.random.choice(SHOTS, 13, replace=False),
        'Sensor_3': np.random.choice(SHOTS, 9, replace=False),
        'Sensor_4': np.random.choice(SHOTS, 18, replace=False),
    },
    'C2': {
        'Sensor_1': np.random.choice(SHOTS, 13, replace=False),
        'Sensor_2': np.random.choice(SHOTS, 14, replace=False),
        'Sensor_3': np.random.choice(SHOTS, 18, replace=False),
        'Sensor_4': np.random.choice(SHOTS, 2, replace=False),
    }
}

class make_data():

    def __init__(self, path='./'):
        self.path = path
        self.axis = AXIS
        self.sensor_shots = SENSOR_SHOTS
        self._generate()
        self._generate_parquet()
    
    @staticmethod
    def b_paths(size):
        data = np.random.normal(0, 1, (100, size))
        data[0] *= 0
        data = data.cumsum(axis=0)
        return data
    
    def _generate(self):
        self.sensor_data = {}
        for k in self.sensor_shots.keys():
            self.sensor_data[k] = {}
            for sen, shot in self.sensor_shots[k].items():
                self.sensor_data[k][sen] = self.b_paths(shot.size)

    def _generate_parquet(self):
        for k in self.sensor_data.keys():
            to_path = os.path.join(self.path, k)
            os.makedirs(to_path)
            for sen, d in self.sensor_data[k].items():
                parq = pa.Table.from_pandas(
                    pd.DataFrame(
                        data=d,
                        columns=self.sensor_shots[k][sen]
                    )
                )
                pq.write_table(parq, os.path.join(to_path, f'{sen}.parquet'))

if __name__ == '__main__':
    inst = make_data(path='./data')


