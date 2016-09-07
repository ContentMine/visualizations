web: gunicorn app:app
web: bokeh serve cooccurrences/cooccurrences.py trending/trending.py factexplorer/factexplorer.py dictionaries/dictionaries.py --port=$PORT --host=contentmine-demo.herokuapp.com --host=localhost:5006  --address=0.0.0.0 --use-xheaders --allow-websocket-origin=contentmine-demo.herokuapp.com --host=localhost:5000
