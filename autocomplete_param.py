import panel as pn
import param

class CustomExample(param.Parameterized):
    """An example Parameterized class"""
    select_string = param.Selector(objects=["red", "yellow", "green"])

 class X(pn.viewable.Viewer):

    CC = CustomExample()
    
    ran = param.Range(default=(0, 10), bounds=(0, 10))
    
    ran2 = pn.widgets.IntRangeSlider(value=(0, 10), start=0, end=10, step=1)
 
    text = pn.widgets.StaticText()
 
    def __panel__(self):
        return self._layout
 
    def __init__(self):
 
        super().__init__() #**params)

        self.cc = pn.Param(
            self.CC.param,
            widgets={
                'select_string': pn.widgets.AutocompleteInput
            }
        )
 
        self.main = pn.Param(
            self.param, parameters=['ran'],
            sizing_mode='stretch_width', max_width=300, show_name=False,
        )
 
        self._layout = pn.Column(
            pn.Row(
                self.main,
                #self.ran2,
                self.cc,
                sizing_mode='stretch_width'
            ),
            self.text,
            sizing_mode='stretch_both'
        )
 
        self._toggle_main()
        self._toggle_main3()
 
    @param.depends('ran', watch=True)
    def _toggle_main(self):
        self.text.value = f"{self.ran}"
    
    # @pn.depends(ran2, watch=True)
    # def _toggle_main2(self):
    #     self.text.value = f"{self.ran2.value}"

    @param.depends('CC', watch=True)
    def _toggle_main3(self):
        self.text.value = f"{self.CC}"
 
X().show()

X().param.values()
