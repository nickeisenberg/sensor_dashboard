import panel as pn
from panel.viewable import Viewer
import param
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import numpy as np
from hvplot.ui import Controls
import hvplot.pandas
from make_data import SENSOR_SHOTS, AXIS
import os
import time


class homepage(Viewer):
    text = pn.pane.Markdown(
        '''
        # Dashboard
        Here are some instructions
        ### Instructios
        * first
        * second
        * ...
        ### Contact
        * Make an issue on the gitlab to suggest a feature or point out a bug
        ''',
        width = 500
    )
    def __panel__(self):
        return self._layout
    def __init__(self):
        super().__init__()
        self._layout = pn.Row(
            self.text
        )

class fileupload(Viewer):
    
    Flup = pn.widgets.FileInput(accept='.csv')
    instructions = pn.widgets.StaticText(
        value='Enter the axis, sensor and shot number.'
    )
    sl_axis = pn.widgets.Select(
        name='axis',
        options=[*SENSOR_SHOTS.keys()]
    )
    sl_sensor = pn.widgets.Select(
        name='sensor',
        options=[*SENSOR_SHOTS['C1'].keys()]
    )
    sl_shot = pn.widgets.IntInput(name='shot_number', start=0, end=10000, step=1)
    upload = pn.widgets.Button(name='Upload the file')
    notify = pn.widgets.StaticText(
        name='Upload Status', value=''
    )

    def __panel__(self):
        return self._layout

    def __init__(self):
        super().__init__()
        # self.flup = pn.Row(pn.widgets.FileInput(accept='.csv'))
        self.flup = pn.Row(self.Flup)
        self._layout = pn.Column(
            self.flup,
            self.instructions,
            self.sl_axis,
            self.sl_sensor,
            self.sl_shot,
            self.upload,
            self.notify
        )
   
    # This feature only partially works. I need to work on it some more.
    # @pn.depends(Flup, watch=True)
    # def update_notify(self):
    #     try:
    #         self.notify.value = 'File not yet uploaded'
    #     except:
    #         _ = ''

    @pn.depends(upload, watch=True)
    def save_file(self):
        try:
            self.flup[0].save('__temp__.csv')
            parq = pa.Table.from_pandas(
                pd.read_csv('__temp__.csv', index_col=0).set_axis(
                    [self.sl_shot.value], axis=1, inplace=False
                )
            )
            pq.write_table(
                parq,
                os.path.join(
                    'data_multi',
                    self.sl_axis.value,
                    self.sl_sensor.value,
                    f'{self.sl_shot.value}.parquet'
                ) 
            )
            os.remove('__temp__.csv')
            self.notify.value = 'Uploading in 3'
            now = time.time()
            while time.time() - now < 3: 
                if time.time() - now == 1:
                    self.notify.value = 'Uploading in 2'
                if time.time() - now == 2:
                    self.notify.value = 'Uploading in 1'
            fmr = self.flup.pop(0)
            fmr.value = None
            self.Flup = None
            self.Flup = pn.widgets.FileInput(accept='.csv')
            # self.flup.append(pn.widgets.FileInput(accept='.csv'))
            self.flup.append(self.Flup)
            self.notify.value = ''
        except:
            _ = ''

class timeseries(Viewer):
    
    # tab 1 classes
    axis = param.Selector()
    sensor = param.Selector()
    shot = param.Selector()
    refresh = pn.widgets.Button(name='Refresh the available shots')

    # tab 2 classes
    xlim = param.Range()
    
    # tab 3 classes
    notes = pn.widgets.TextEditor()

    def __panel__(self):
        return self._layout

    def __init__(self): #, **params):
        
        self._populate_main()

        super().__init__() #**params)

        #-Set the controls for the tabs--------------------
        # Tab 1
        self._main_controls = pn.Param(
            self.param, parameters=['axis', 'sensor', 'shot'],
            sizing_mode='stretch_width', max_width=400, show_name=False,
        )
        
        # Tab 2
        self._axes_controls = pn.Param(
            self.param, parameters=['xlim'],
            sizing_mode='stretch_width', max_width=400, show_name=False,
        )

        self._tabs = pn.Tabs(
            tabs_location='left', width=400
        )

        self._layout = pn.Column(
            pn.Row(
                self._tabs,
                pn.layout.HSpacer(),
                sizing_mode='stretch_width',
            ),
            pn.layout.HSpacer(),
            sizing_mode='stretch_both'
        )
        
        self._update_main1()
        self._update_main2()
        self._toggle_main()
        self._retrieve_parquet()
        self._update_axes()
        self._plot()

    def _populate_main(self):
        self.param['axis'].objects = AXIS
        self.param['axis'].default = 'C1'
        self.param['sensor'].objects = [*SENSOR_SHOTS['C1'].keys()]
        self.param['sensor'].default = 'Sensor_1'
        self.param['shot'].objects = [*SENSOR_SHOTS['C1']['Sensor_1']]
        self.param['shot'].default = [*SENSOR_SHOTS['C1']['Sensor_1']][0]
        self.param['xlim'].bounds = [0, 100]
        self.param['xlim'].step = 1

    @param.depends('axis', 'sensor', 'shot', watch=True)
    def _update_main1(self):
        # shots = SENSOR_SHOTS[self.axis][self.sensor]
        shots = [
            int(fn.split('.')[0]) for fn in os.listdir(
                os.path.join(
                    '.', 'data_multi', self.axis, self.sensor
                )
            ) if fn.endswith('.parquet')
        ]
        self.param['shot'].objects = shots
        if self.shot not in shots:
            self.shot = shots[0]

    @pn.depends(refresh, watch=True)
    def _update_main2(self):
        try:
            shots = [
                int(fn.split('.')[0]) for fn in os.listdir(
                    os.path.join(
                        '.', 'data_multi', self.axis, self.sensor
                    )
                ) if fn.endswith('.parquet')
            ]
            self.param['shot'].objects = shots
            if self.shot not in shots:
                self.shot = shots[0]
        except:
            _ = ''
    
    @param.depends('axis', 'sensor', 'shot', watch=True)
    def _toggle_main(self):
        # parameters = ['axis', 'sensor', 'shot']
        # self._main_controls.parameters = parameters
        # Control other tabs
        try:
            tabs = [
                ('Fields', self._main_controls),
                ('Axes', self._axes_controls),
                ('Notes', self.notes),
            ]
            self._tabs[:] = tabs
        except:
            _ = ''
    
    @param.depends('axis', 'sensor', 'shot', watch=True)
    def _retrieve_parquet(self):
        self._parquet = pq.read_table(
            # f'./data_single/{self.axis}/{self.sensor}.parquet'
            # f'./data_multi/{self.axis}/{self.sensor}/{self.shot}.parquet'
            os.path.join(
                '.', 'data_multi', self.axis, self.sensor, f'{self.shot}.parquet'
            )
        )
        self._parq_df = self._parquet.to_pandas()

    @param.depends('axis', 'sensor', 'shot', watch=True)
    def _update_axes(self):
        domain = self._parq_df[self.shot].index.values
        self.param['xlim'].bounds = [domain[0], domain[-1]]
        if self.xlim is None:
            self.xlim = (domain[0], domain[-1])
        self.param['xlim'].step = 1

    @param.depends('axis', 'sensor', 'shot', 'xlim', watch=True)
    def _plot(self):
        try:
            df = self._parq_df.iloc[int(self.xlim[0]): int(self.xlim[-1])]
            self._hvplot = df.hvplot.line(y=str(self.shot))
            self._hvpane = pn.pane.HoloViews(
                self._hvplot,
                sizing_mode='stretch_width',
                margin=(0, 20, 0, 20)
            )
            self._layout[0][1] = self._hvpane
        except:
            print(self.shot)

class App(Viewer):
    home = homepage().__panel__()
    ts = timeseries().__panel__()
    flup = fileupload().__panel__()
    def __panel__(self):
        return self._layout
    def __init__(self):
        super().__init__()
        self._tabs = pn.Tabs(
            tabs_location='above', width=1000
        )
        self._populate()
        self._layout = pn.Row(
            self._tabs,
            sizing_mode='stretch_both'
        )
    def _populate(self):
        tabs = [
            ('HomePage', self.home),
            ('TimeSeries', self.ts),
            ('FileUpload', self.flup),
        ]
        self._tabs[:] = tabs

if __name__ == '__main__':
    app = App()
    app.show()



