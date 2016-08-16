# visualizations

Create and publish interactive visualizations of ContentMine-facts.

## Installation and Requirements

The easiest entry is by using [Anaconda](https://www.continuum.io/downloads) with Python 3, opening the Anaconda Prompt and creating a new virtual environment.

```
conda create -n contentmine3 python=3.4 anaconda
```

After that activate the virtual environment and install the packages with pip:

```
source activate contentmine3
pip install pandas bokeh jupyter pycproject matplotlib scipy
```

* Python3
  * [pandas](http://pandas.pydata.org/)
  * [bokeh](http://bokeh.pydata.org/en/latest/)
  * [jupyter](http://jupyter.org/)
  * [pycproject](https://github.com/ContentMine/pyCProject/)
  * matplotlib
  * scipy


## Configuration

At the moment very basic, three options have to be set in `config.py`:
* `rawdatapath` = where the raw data in form of `facts.json` and `metadata.json` is expected
* `cacheddatapath` = where the intermediary dataframes can be stored for reuse
* `resultspath` = where the output-htmls and plots are expected


## Getting some testdata

* Download the facts and metadata json-files from [Zenodo](https://zenodo.org/record/58839#.V7L6wO1MdhF), and place them into the `rawdatapath`.
* rename the files into `facts.json` and `metadata.json`

## Produce static plots

* Active virtualenv with `source activate contentmine3`
* Change paths in `cmvisualizations/config.py`
* change working directory to `visualizations`
* run script with `python3 cmvisualizations/APPNAME/static.py`, e.g. `python3 cmvisualizations/trending/static.py`
* Output files can be found in the corresponding `resultspath` from config


## Running an inveractive visualization

* Active virtualenv with `source activate contentmine3`
* Change paths in `cmvisualizations/config.py`
* change working directory to `visualizations`
* start application with `bokeh serve --show cmvisualizations/APPNAME/interactive.py`, e.g. `bokeh serve --show cmvisualizations/factheatmap/interactive.py`
* This should - after a few seconds of preprocessing - open a new browser window with the interactive visualization
