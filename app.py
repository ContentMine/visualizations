"""
This file demonstrates embedding a bokeh applet into a flask
application. See the README.md file in this dirrectory for
instructions on running.
"""
from __future__ import print_function

import sys
import socket
import logging
logging.basicConfig(level=logging.INFO)

from flask import Flask, render_template, request, redirect
from bokeh.embed import components, autoload_server
from bokeh.client.session import pull_session, push_session

app = Flask('contentmine-demo')

## set up logging
logger = logging.getLogger("applogger")
sh_out = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
sh_out.setFormatter(formatter)
logger.addHandler(sh_out)

bokeh_url = "http://localhost:5006"
applet_url = "http://localhost:5050"

# import factheatmap.interactive as fheat

logger.info('socket: {0}'.format(socket.gethostbyname(socket.gethostname())))

@app.route('/')
def main():
    return redirect('/index')

@app.route("/index")
def applet():
    session = pull_session(url=bokeh_url, app_path="/interactive")
    logger.info('session id: {0}'.format(session.id))
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
    app.run(port=33507)
