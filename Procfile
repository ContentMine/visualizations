web: gunicorn app:app
bokeh: bokeh serve cooccurrences/cooccurrences.py trending/trending.py factexplorer/factexplorer.py dictionaries/dictionaries.py --port=5006 --host=127.0.0.1:5006 --address=127.0.0.1 --allow-websocket-origin=127.0.0.1:5006 --allow-websocket-origin=0.0.0.0:5000 --host=localhost:5006 --log-level=debug
