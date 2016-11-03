# visualizations

Create and publish interactive visualizations of ContentMine-facts. We use the [Bokeh library](http://bokeh.pydata.org/en/latest/) for creating interactive visualization applets that can be run locally or deployed on a server.

## Installation and Requirements

The easiest setup is by using [Anaconda](https://www.continuum.io/downloads) for Python 3, opening the Anaconda Prompt and creating a new virtual environment.

```
conda create -n contentmine3 python=3.5.2 anaconda
```

After that activate the virtual environment and install the packages with pip:

```
source activate contentmine3
pip install pandas bokeh
```


* Other useful packages:
  * [pandas](http://pandas.pydata.org/)
  * [bokeh](http://bokeh.pydata.org/en/latest/)
  * [jupyter](http://jupyter.org/)
  * [pycproject](https://github.com/ContentMine/pyCProject/)


## Configuration

At the moment very basic, three options have to be set in `config.py`:
* `rawdatapath` = where the raw data in form of `facts.json` and `metadata.json` is expected
* `cacheddatapath` = where the intermediary dataframes can be stored for reuse
* `resultspath` = where the output-htmls and plots are expected


## Running an interactive visualization

Fork, clone or download this repo.

### Get some play data

* Download the facts and metadata json-files from [Zenodo](https://zenodo.org/record/58839#.V7L6wO1MdhF), and place them into the `rawdatapath`.
* rename the files into `facts.json` and `metadata.json`
* Run preprocessing from `visualizations`-folder:
```
python3 preprocessing/preprocessing.py --raw /PATH/TO/RAWDATA --cache /PATH/TO/CACHEDDATA
```

### Setting up local environments

* Active virtualenv with `source activate contentmine3`
* Change paths in `config.py`
* change working directory to `visualizations`
* start application with `bokeh serve --show APPNAME/APPNAME.py`, e.g. `bokeh serve --show cooccurrences/cooccurrences.py`
* This should - after a few seconds of processing - open a new browser window with the interactive visualization

## Deployment to heroku


### Deployment notes


* https://devcenter.heroku.com/articles/python-gunicorn
* Updating dependencies: http://stackoverflow.com/questions/9471017/how-do-i-upgrade-a-dependency-in-a-python-project-on-heroku
* Scaling out and up: https://devcenter.heroku.com/articles/dynos#isolation-and-security


###

Currently we have to split bokeh and flask into two apps (dynos), until the interprocess communication problem can be solved.
Flask frontend-development is happening on branch flask, bokeh server development is happening on branch server.
Differences are the Procfile, and in app.py, where autoload_server() looks at different urls when running on the same or two dynos. Data needs to be updated in each branch.

### Deploy via pipeline

Add staging app and server app to git remotes
```
git remote add staging https://git.heroku.com/contentmine-demo-staging.git
git remote add server https://git.heroku.com/contentmine-demos.git
```

Push new flask-app code to staging
```
git push staging flask:master    
```

Push new server-app code to server
```
git push server server:master    
```

Review functionality and then promote to production (via CLI or web interface)

## Issues


From [Tutorial](http://blog.thedataincubator.com/2015/09/painlessly-deploying-data-apps-with-bokeh-flask-and-heroku/):
```
heroku config:add BUILDPACK_URL=https://github.com/kennethreitz/conda-buildpack.git
```

http://stackoverflow.com/questions/38417200/serving-interactive-bokeh-figure-on-heroku/38447618#38447618
```
web: bokeh serve --port=$PORT --host=contentmine-demo.herokuapp.com --address=0.0.0.0 --use-xheaders APPNAME/APPNAME.py
```

http://stackoverflow.com/questions/38564389/deploying-to-heroku-a-bokeh-server-plot-embedded-in-flask


* Running bokeh-server as subprocess does not solve the issue of non-connectivity between threads, and creates new problem of two bokeh-servers wanting to listen to the same port

* Production Pipelines: Read https://devcenter.heroku.com/articles/pipelines and https://devcenter.heroku.com/articles/github-integration-review-apps
