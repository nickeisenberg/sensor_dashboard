import panel as pn

upload =  pn.Row(
    pn.indicators.Number(value = 0),
    pn.widgets.FileInput(accept='json', multiple= False, name = 'x')
)

def process_data(*data, upload = upload):
    for datum in data:
        if hasattr(datum, 'name') and datum.name == 'value' and isinstance(datum.new, bytes):
            print('x')
            fmr = upload.pop(1)
            fmr.value = None
            upload.append(pn.widgets.FileInput(accept='json', multiple= False))
            upload[0].value = upload[0].value + 1
            upload[1].param.watch(process_data, ['value'])

upload[1].param.watch(process_data, 'value')

upload.show()
