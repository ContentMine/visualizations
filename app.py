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
from bokeh.client.session import pull_session, push_session, ClientSession

import subprocess
import atexit

app = Flask('contentmine-demo')

## set up logging
logger = logging.getLogger("applogger")
sh_out = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
sh_out.setFormatter(formatter)
logger.addHandler(sh_out)


bokeh_process = subprocess.Popen(
    ['bokeh', 'serve','--allow-websocket-origin=localhost:5000', '--allow-websocket-origin=0.0.0.0:5000', '--port=5100',
            'cooccurrences/cooccurrences.py', 'trending/trending.py', 'factexplorer/factexplorer.py', 'dictionaries/dictionaries.py'], stdout=subprocess.PIPE)

# worker: bokeh serve cooccurrences/cooccurrences.py trending/trending.py factexplorer/factexplorer.py dictionaries/dictionaries.py --port=5100 --host=contentmine-demo.herokuapp.com --host=localhost:5006  --address=0.0.0.0 --use-xheaders --allow-websocket-origin=contentmine-demo.herokuapp.com --host=localhost:5100 --host=localhost:5000 --allow-websocket-origin=127.0.0.1:5000 --allow-websocket-origin=0.0.0.0:5000 --host=127.0.0.1

@atexit.register
def kill_server():
    bokeh_process.kill()

@app.route('/')
def main():
    return redirect('/trending')

@app.route("/cooccurrences")
def cooccurrences():
    session = pull_session(url="http://0.0.0.0:5100/cooccurrences")
    script = autoload_server(None, session_id=session.id, app_path="/cooccurrences", url="http://0.0.0.0:5100")
    return render_template(
        "simple.html",
        script = script,
        app_tag = "cooccurrences"
    )
@app.route("/trending")
def trending():
    session = pull_session(url="http://0.0.0.0:5100/trending")
    script = autoload_server(None, session_id=session.id, app_path="/trending", url="http://0.0.0.0:5100")
    return render_template(
        "simple.html",
        script = script,
        app_tag = "trending"
    )

@app.route("/dictionaries")
def dictionaries():
    session = pull_session(url="http://0.0.0.0:5100/dictionaries")
    script = autoload_server(None, session_id=session.id, app_path="/dictionaries", url="http://0.0.0.0:5100")
    return render_template(
        "simple.html",
        script = script,
        app_tag = "dictionaries"
    )

@app.route("/factexplorer")
def factexplorer():
    session = pull_session(url="http://0.0.0.0:5100/factexplorer")
    script = autoload_server(None, session_id=session.id, app_path="/factexplorer", url="http://0.0.0.0:5100")
    return render_template(
        "simple.html",
        script = script,
        app_tag = "factexplorer"
    )

if __name__ == '__main__':
    app.run(port=33507)
