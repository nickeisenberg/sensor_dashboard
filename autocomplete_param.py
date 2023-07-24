'using panel depends within a class and supressing the error'

import panel as pn
import param

class X(pn.viewable.Viewer):
    ran = param.Range(default=(0, 10), bounds=(0, 10))
    ran2 = pn.widgets.IntRangeSlider(value=(0, 10), start=0, end=10, step=1)
    text = pn.widgets.StaticText()
    def __panel__(self):
        return self._layout
    def __init__(self):
        super().__init__() #**params)
        self.main = pn.Param(
            self.param, parameters=['ran'],
            sizing_mode='stretch_width', max_width=300, show_name=False,
        )
        self._layout = pn.Column(
            pn.Row(
                self.main,
                self.ran2,
                # self.cc,
                sizing_mode='stretch_width'
            ),
            self.text,
            sizing_mode='stretch_both'
        )
    @param.depends('ran', watch=True)
    def _toggle_main(self):
        self.text.value = self.ran
    @pn.depends(ran2, watch=True)
    def _toggle_main2(self):
        '''
            This try/except  seems to supress the error while still
            maintaining correct functionality.
        '''
        try:
            self.text.value = f"{self.ran2.value}"
        except:
            _ = ''
    

X().show()

X().param.values()
