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

## Running a visualization

* Change path to input-data
* change working directory to `visualizations`
* start application with `bokeh serve --show cmvisualizations/APPNAME`
