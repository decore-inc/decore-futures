# decore-futures
simulation trades from Bitmex futures

## Setup Env
1. use virtualenv
    ```
    pip3 install virtualenv
    
    virtualenv -p /path/to/python3 my_env_name
    
    source my_env_name/bin/activate
    
    ```
1. download packages on virtualenv
    ```
    (venv) pipenv install
    ```

## Start a simulation
1. Import source files under `sorces/` (ex. XBTU19.csv)

    (You can download files from [here](https://console.cloud.google.com/storage/browser/decore-futures/trades?authuser=1&hl=zh-TW&organizationId=1053220464045&project=decore-gpd-btc-test))
1. Setup initial conditions at `start.py`
1.  Run
    ```
    (venv) python start.py
    ```
1. Output file would be under `results/`
