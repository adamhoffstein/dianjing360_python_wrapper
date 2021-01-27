# This is a lightweight python wrapper for interacting with the 360 Dianjing API

## Installation

First, clone the repository into your directory.

```bash
git clone https://github.com/adamhoffstein/dianjing360_python_wrapper.git
```

Then, create a virtual environment and set the following environment variables:

(only if you are using AWS)
360_GOOGLE_SHEET: The Google sheet you want to export the data to
GDRIVE_API_CREDENTIALS: Your Google drive api credentials. Check pygsheets's documentation for service_account_env_var for more information

(required)\
360_ACCOUNT\
360_PASSWORD\
360_API_KEY\
360_API_SECRET

Then, run:

```bash
pip install -r requirements.txt
```

## Usage

You can check out the lambda_function.py file to see basic usage of the wrapper. 

The module adds a Q360Base session object which is used to run the following types of reports:
  Campaign Reports
  Fengwu Reports
  Fengwu Realtime Reports
  Region Reports
