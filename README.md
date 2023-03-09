# bulk-delete-clients
API script to prompt the user for a list of tags then search an instance of PT and delete clients with corresponding tags. Clients can be selected for deletion based on 2 filter modes.

Mode 1: Delete all clients that contain at least one of the selected tags
Mode 2: Delete all clients that contain all of the selected tags

IMPORTANT: Deleting clients is a very resource heavy operation. Each delete operation takes ~20 seconds. Multiple delete operations in succession will increase this time and increase latency for all user actions in the platform. If this continues the time it takes to delete a client will surpass the request timeout threshold and the delete client operation will fail.

# Requirements
- [Python 3+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [pipenv](https://pipenv.pypa.io/en/latest/install/)

# Installing
After installing Python, pip, and pipenv, run the following commands to setup the Python virtual environment.
```bash
git clone this_repo
cd path/to/cloned/repo
pipenv install
```

# Setup
After setting up the Python environment, you will need to setup a few things before you can run the script.

## Credentials
In the `config.yaml` file you should add the full URL to your instance of Plextrac.

The config also can store your username and password. Plextrac authentication lasts for 15 mins before requiring you to re-authenticate. The script is set up to do this automatically. If these 3 values are set in the config, and MFA is not enable for the user, the script will take those values and authenticate automatically, both initially and every 15 mins. If any value is not saved in the config, you will be prompted when the script is run and during re-authentication.

# Usage
After setting everything up you can run the script with the following command. You should be in the folder where you cloned the repo when running the following.
```bash
pipenv run python main.py
```
You can also add values to the `config.yaml` file to simplify providing the script with the data needed to run. Values not in the config will be prompted for when the script is run.

## Required Information
The following values can either be added to the `config.yaml` file or entered when prompted for when the script is run.
- PlexTrac Top Level Domain e.g. https://yourapp.plextrac.com
- Username
- Password
- MFA Token (if enabled)

## Script Execution Flow
- Prompts user for Plextrac instance URL
  - Validate URL points to a running instance of Plextrac
- Prompts user for username, password, and mfa (if applicable)
- Prompts user for list of tags that will be used to filter clients for deletion
- Prompts user which deletion mode should be used to select clients
- Deletes selected clients
