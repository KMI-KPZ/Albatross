from bokeh.palettes import PuBu
from bokeh.io import show
from bokeh.models import ColumnDataSource, ranges, LabelSet
from bokeh.plotting import figure, output_file


tmp_data = {}
tmp_data['value'] = [1, 2, 4, 5]
tmp_data['NUTS_ID'] = ['De', 'AU', 'DS', 'ää']
testdata_source = ColumnDataSource(tmp_data)
x_label = "test"
y_label = "moretest"
title = "Visme"
p2 = figure(plot_width=600, plot_height=300, tools="save",
x_axis_label = x_label,
y_axis_label = y_label,
title=title,
x_minor_ticks=2,
x_range = testdata_source.data["NUTS_ID"],
y_range= ranges.Range1d(start=min(testdata_source.data['value']),end=max(testdata_source.data['value'])))


labels = LabelSet(x='NUTS_ID', y='value', text='value', level='glyph',
x_offset=-13.5, y_offset=0, source=testdata_source, render_mode='canvas')
p2.vbar(source=testdata_source,x='NUTS_ID',top='value',bottom=0,width=0.3,color=PuBu[7][2])
        
        
output_file('histogram.html', title="histogram.py example")
show(p2)
