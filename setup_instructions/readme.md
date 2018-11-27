## set up
```
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-get update
sudo apt-get install python3.6
sudo apt-get install python3.6-dev
sudo apt-get install build-essential
sudo apt install gcc
```

```
virtualenv -p python3.6 venv
pip install -r requirements.txt
python -m spacy download en
```

For ubuntu, you add local environment variables by editing `vim ~/.bash_profile` and add the following to the file, then `source ~/.bash_profile`:

```
export RDS_DB_NAME='RDS Database Name'
export RDS_USERNAME='RDS Username'
export RDS_PASSWORD='RDS Password'
export RDS_HOSTNAME='xxx.rds.amazonaws.com'
```
