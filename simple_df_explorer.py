import panel as pn
from panel.viewable import Viewer
import param
import pyarrow.parquet as pq
import numpy as np
from hvplot.ui import Controls
import hvplot.pandas
from make_data import SENSOR_SHOTS, AXIS

class df_exp(Viewer):
    
    # tab 1 classes
    axis = param.Selector()
    sensor = param.Selector()
    shot = param.Selector()
    
    # tab 2 classes
    xlim = param.Range()

    def __panel__(self):
        return self._layout

    def __init__(self, **params):
        
        self._populate_main()
        self._retrieve_parquet()

        super().__init__(**params)

        #-Set the controls for the tabs--------------------
        # Tab 1
        self._main_controls = pn.Param(
            self.param, parameters=['axis', 'sensor', 'shot'],
            sizing_mode='stretch_width', max_width=300, show_name=False,
        )
        
        # Tab 2
        self._axes_controls = pn.Param(
            self.param, parameters=['xlim'],
            sizing_mode='stretch_width', max_width=300, show_name=False,
        )
        #--------------------------------------------------

        self._tabs = pn.Tabs(
            tabs_location='left', width=400
        )

        self._layout = pn.Column(
            pn.Row(
                self._tabs,
                pn.layout.HSpacer(),
                sizing_mode='stretch_width'
            ),
            pn.layout.HSpacer(),
            sizing_mode='stretch_both'
        )
        
        self._toggle_main()
        self._update_main()
        self._update_axes()
        self._plot()
    
    def _populate_main(self):
        self.param['axis'].objects = AXIS
        self.param['axis'].default = 'C1'
        self.param['sensor'].objects = [*SENSOR_SHOTS['C1'].keys()]
        self.param['sensor'].default = 'Sensor_1'
        self.param['shot'].objects = [*SENSOR_SHOTS['C1']['Sensor_1']]
        self.param['xlim'].bounds = [0, 100]
        self.param['xlim'].step = 1

    @param.depends('axis', 'sensor', watch=True)
    def _retrieve_parquet(self):
        self._parquet = pq.read_table(
            f'./data/{self.axis}/{self.sensor}.parquet'
        )
        self._parq_df = self._parquet.to_pandas()

    @param.depends('axis', 'sensor', 'shot', watch=True)
    def _toggle_main(self):
        parameters = ['axis', 'sensor', 'shot']
        self._main_controls.parameters = parameters

        # Control other tabs
        tabs = [
            ('Fields', self._main_controls),
            ('Axes', self._axes_controls)
        ]
        self._tabs[:] = tabs

    @param.depends('axis', 'sensor', watch=True)
    def _update_main(self):
        shots = SENSOR_SHOTS[self.axis][self.sensor]
        self.param['shot'].objects = shots
        if self.shot not in shots:
            self.shot = shots[0]

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

inst = df_exp()

inst.show()

