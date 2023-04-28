# ferry-python
Website scraping scripts for FerryWave project

## Requirements

### Python

You will need Python 3.9.6 or up to run this set of scripts.

<i>/venv</i> folder contains the Python environment with necessary Python libraries. Before running the scripts, switch to this environment with a <i>source</i> command:
<code>source /venv/bin/activate</code>

If for any reason the environment does not work for you, the file <i>requirements.txt</i> includes all necessary python packages. You can install them on your machine with pip:
<code>pip install -r requirements.txt</code>

### Credentials
You need to export the MongoDB password for the 'python-user' account into the local environment. You can do it like this:
<code>export MONGODB_PASSWORD=\<password\></code>

### Tesseract
Tesseract is an image recognition library that is used to scrape some of the timetabling data for the FerryWave website.
You will need to install Tesseract and Tesseract OCR on your machine in order to run scraping for all the websites.

Follow the official documentation for installation steps for your OS (choose version 5):
<li> https://github.com/tesseract-ocr/tesseract#installing-tesseract

<li>Don't forget to install at least one full language package as well (preferably english): https://tesseract-ocr.github.io/tessdoc/Installation.html

<br>
After the installation you will have to provide the path o Tesseract executable file. Change the appropriate line in <code>settings.py</code>

<br>

## Running the scraper
Runnnig <code>update_database.py</code> will run the scraping for all defined website destinations, clear the database and push the new data into the database.