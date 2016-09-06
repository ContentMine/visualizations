web: gunicorn app:app
worker: bokeh serve factheatmap/interactive.py --port=5006 --host=contentmine-demo.herokuapp.com --host=localhost:5006 --host=127.0.0.1 --host=* --address=0.0.0.0 --use-xheaders --allow-websocket-origin=contentmine-demo.herokuapp.com --log-level=debug
