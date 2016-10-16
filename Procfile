web: gunicorn app:app
bokeh: bokeh serve cooccurrences/cooccurrences.py trending/trending.py factexplorer/factexplorer.py dictionaries/dictionaries.py --port=5006 --use-xheaders --host=0.0.0.0:5006 --host=host=contentmine-demo-staging.herokuapp.com:5006 --allow-websocket-origin=0.0.0.0:5006 --allow-websocket-origin=0.0.0.0:5000 --address=0.0.0.0
