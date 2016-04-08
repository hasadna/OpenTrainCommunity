This README file describes basic usage for the data analysis Python scripts. 

### Download local cache from API

The first step (only done once) involves downloading a local cache of the train data from the otrain.org API.

Edit the `download_cache_data.py` script to set the desired date ranges--the `TIME_PERIODS` list contains all year/month combinations to download. Then run the script as follows:

```
python3 download_cache_data.py
```

The script will create a JSON file for each route, each file containing objects for every time period of interest. These JSON files can later be loaded for analysis offline.

### Example analysis--find URLs showing poor performance

The `find_interesting_urls.ipynb` file is an Jupyter notebook (aka IPython notebook). The notebook is a web interface to Python that allows for executing snippets of code, or cells, while keeping the output for all previous cells in memory. The notebook lends itself to separation of loading, pre-processing, exploring, and analyzing data.

The default OTrain development environment should include IPython notebook functionality, which can be launched with the `ipython notebook` command. If running outside of the development environment, [installing Anaconda](https://www.continuum.io/downloads) is the easiest way to get notebook functionality without effecting any other Python environments (works on Linux/OS X/Windows).

Once IPython notebook is running, open the `find_interesting_urls.ipynb` file.

The first few cells import libraries and load the initial data.

The next cell iterates over the first 100 routes (can be manually modified) and prints route IDs that may be interesting to look at--they must be in the time range of interest and have a minimum number of trips.

Finally we look at the results for one route ID at a time (manually modified) and find time periods where stations have a percentage of late departures that are statistically larger than the mean. The results are printed in a table that include a URL that can be used for further exploration using the OTrain website UI.

Additional cells create some plots that were used to visualize the data. The final cell creates the time-series plot that was included in the February 2016 trends report. It shows percentage of late departures over time for תחנה פתח תקווה קריית אריה.