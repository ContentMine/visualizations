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
from bokeh.client.session import pull_session, push_session

app = Flask('contentmine-demo')

bokeh_url = "http://localhost:5006"
applet_url = "http://localhost:5050"

# import factheatmap.interactive as fheat

@app.route('/')
def main():
    return redirect('/index')

@app.route("/index")
def applet():
    session = pull_session(url=bokeh_url, app_path="/interactive")
    # session.pull()
    # session.loop_until_closed()
    script = autoload_server(None, session_id=session.id, app_path="/interactive")
    return render_template(
        "simple.html",
        script = script,
        # div = div,
        # app_url = bokeh_url+"/interactive"
    )

if __name__ == '__main__':
    app.run(port=8000)
