"""
This file demonstrates embedding a bokeh applet into a flask
application. See the README.md file in this dirrectory for
instructions on running.
"""
from __future__ import print_function

import logging
logging.basicConfig(level=logging.INFO)

from flask import Flask, render_template, request, redirect
from bokeh.embed import components, autoload_server

app = Flask('contentmine-demo')

bokeh_url = "http://localhost:5006/interactive"
applet_url = "http://localhost:5050"

# import factheatmap.interactive as fheat

@app.route('/')
def main():
    return redirect('/index')

@app.route("/index")
def applet():
    # script, div = components(fheat.layout)
    script = autoload_server(None, app_path="/interactive")
    return render_template(
        "simple.html",
        script = script,
        # div = div,
        # app_url = bokeh_url,
        app_tag = "CM Factexplorer"
    )

if __name__ == '__main__':
    app.run(port=8000)
