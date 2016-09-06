
import config
import preprocessing.preprocessing as pp

from bokeh.layouts import column, row
from bokeh.plotting import Figure, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, HBox, VBox
from bokeh.models.widgets import Slider, Select, TextInput, RadioGroup, Paragraph, Div
from bokeh.io import curdoc, save
from bokeh.charts import HeatMap, bins, output_file, vplot, TimeSeries, Line
from bokeh.models import FixedTicker, SingleIntervalTicker, ColumnDataSource, DataRange1d
from bokeh.layouts import widgetbox
from bokeh.layouts import gridplot
import bokeh.palettes as palettes
from bokeh.resources import INLINE, CDN

from flask import Flask, render_template, request, redirect

# import distributions.interactive as dist
# import trending.interactive as trend
# import factexplorer.interactive as factex
import factheatmap.interactive as fheat

# layout1 = dist.layout
# layout2 = trend.layout
# layout3 = factex.layout
layout4 = fheat.layout

script, div = components(layout4)


app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('simple.html', script=script, div=div)

if __name__ == '__main__':
    app.run(port=33507)
