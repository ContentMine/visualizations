"""
This file demonstrates embedding a bokeh applet into a flask
application. See the README.md file in this dirrectory for
instructions on running.
"""
from __future__ import print_function

import sys
import socket
import subprocess
import logging
logging.basicConfig(level=logging.INFO)

from flask import Flask, render_template, request, redirect
from bokeh.embed import components, autoload_server
from bokeh.client.session import pull_session, push_session, ClientSession

from preprocessing import preprocessing as pp

# bokeh serve cooccurrences/cooccurrences.py trending/trending.py factexplorer/factexplorer.py dictionaries/dictionaries.py --port=$PORT --host=contentmine-demo.herokuapp.com --host=localhost:5006  --address=0.0.0.0 --use-xheaders --allow-websocket-origin=contentmine-demo.herokuapp.com --host=localhost:5100 --host=localhost:5000 --allow-websocket-origin=127.0.0.1:5000 --allow-websocket-origin=0.0.0.0:5000 --host=127.0.0.1
bokeh_process = subprocess.Popen(
                ['bokeh', 'serve',
                'cooccurrences/cooccurrences.py', 'trending/trending.py', 'factexplorer/factexplorer.py', 'dictionaries/dictionaries.py',
                    '--port=5006', '--host=contentmine-demo.herokuapp.com', '--host=localhost:5006', '--address=0.0.0.0',
                    '--host=localhost',
                    '--use-xheaders', '--allow-websocket-origin=contentmine-demo.herokuapp.com', '--host=localhost:5100',
                    '--host=localhost:5000', '--allow-websocket-origin=127.0.0.1:5000', '--allow-websocket-origin=0.0.0.0:5000', '--host=127.0.0.1'],
                stdout=subprocess.PIPE)

app = Flask('contentmine-demo')

## set up logging
logger = logging.getLogger("applogger")
sh_out = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
sh_out.setFormatter(formatter)
logger.addHandler(sh_out)

month_map = {1: "January", 2: "February", 3: "March", 4: "April",
             5: "May", 6: "June", 7: "July", 8: "August",
             9: "September", 10: "October", 11: "November", 12: "December"}

num_facts, num_papers, y_earliest, m_earliest, y_latest, m_latest = pp.get_overview_statistics("data")
num_facts = str(num_facts)
num_papers = str(num_papers)
earliest = " ".join([month_map[m_earliest], str(y_earliest)])
latest = " ".join([month_map[m_latest], str(y_latest)])
summary = {"num_facts":num_facts, "num_papers":num_papers,
            "earliest":earliest, "latest":latest}

@app.route('/')
def main():
    return redirect('/index')

@app.route("/index")
def index():
    return render_template(
        "description.html",
        title = "Overview",
        summary = summary
    )

@app.route("/cooccurrences")
def cooccurrences():
    # session = pull_session(url="http://localhost:5006/cooccurrences")
    script = autoload_server(model=None, app_path="/cooccurrences", url="http://localhost:5006")
    return render_template(
        "description.html",
        script = script,
        title = "Exploring co-occurrences of facts",
        summary = summary, description = "The plot shows the count of co-occurrences of facts with other facts of their dictionary, in a range of top 5 to top 25. Co-occurrence between two facts is defined as appearing together in the same publication."
    )

@app.route("/trending")
def trending():
    # session = pull_session(url="http://localhost:5006/trending")
    script = autoload_server(model=None, app_path="/trending", url="http://localhost:5006")
    return render_template(
        "description.html",
        script = script,
        title = "Exploring most frequent and uptrending facts",
        summary = summary, description = "The left column shows the top 10 facts, determined by absolute counts over the whole period. The right column shows the top 10 uptrending facts, determined by the sum of percentage changes of daily counts."
    )

@app.route("/dictionaries")
def dictionaries():
    # session = pull_session(url="http://localhost:5006/dictionaries")
    script = autoload_server(model=None, app_path="/dictionaries", url="http://localhost:5006")
    return render_template(
        "description.html",
        script = script,
        title = "Exploring aggregated counts of facts over dictionaries",
        summary = summary, description = "The upper time series shows the absolute counts of facts, aggregated by their source dictionary. The lower time series shows the relative share of facts per dictionary, as a fraction of the daily total count."
    )

@app.route("/factexplorer")
def factexplorer():
    # session = pull_session(url="http://localhost:5006/factexplorer")
    script = autoload_server(model=None, app_path="/factexplorer", url="http://localhost:5006")
    return render_template(
        "description.html",
        script = script,
        title = "Exploring timeseries of selected facts",
        summary = summary, description = "The facts can be selected by user input. If no fact can be found, the graph will not change."
    )

if __name__ == '__main__':
    app.run(port=33507)
