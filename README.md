# python-wedding-scraper
A Python script that scrapes wedding location information from a website and
stores it in Elasticsearch or in CSV format.

![image](https://user-images.githubusercontent.com/55914877/208426492-7e36ee12-3234-463d-a8c9-1f6499a984f1.png)

# Prerequisites
Python 3

[Beautfilsoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

[Elasticsearch](https://www.elastic.co/es/downloads/elasticsearch)

[GeoPy](https://geopy.readthedocs.io/en/stable/)

[Pandas](https://pandas.pydata.org/)

[Requests](https://requests.readthedocs.io/en/latest/)


# Installing
1. Clone the repository:
```
git clone https://github.com/ocriado91/python-wedding-scraper
```
2. Install the required Python libraries using pip and the requirements.txt file:
```
pip install -r requirements.txt
```

# Usage
1. Start the Elasticsearch server:

```
sudo systemctl start elasticsearch
```

2. Run the script:

```
python3 main.py
```

# Customization
You can modify the following variables in the script to customize the scraping:

* `--first_page`: First index of page to extract information
* `--last_page`: Last index of page to extract information
* `--remove_index`: Remove Elasticsearch index before inject new data
* `--store_csv`: Save information in CSV format


# Disclaimer
This script is for educational purposes only. Use it at your own risk and make sure to respect the website's terms of service and robots.txt.
