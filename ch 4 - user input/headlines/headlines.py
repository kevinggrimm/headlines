import feedparser
import json
import urllib.request as urllib2
import urllib.parse
import urllib

from flask import Flask 
from flask import render_template
from flask import request

app = Flask(__name__)

WEATHER_URL = "http://api.openweathermap.org/data/2.5//weather?q={}&units=metric&appid=15264735b87b4ce7b520a41a6c83321f"
CURRENCY_URL = "https://openexchangerates.org/api/latest.json?app_id=047775a83ea5422cb290f2df4a40e49a"

DEFAULTS = {
	'publication': 'bbc',
	'city': 'London, UK',
	'currency_from': 'GBP',
	'currency_to': 'USD'
}

RSS_FEEDS = {
	'bbc': "http://feeds.bbci.co.uk/news/rss.xml",
	'cnn': "http://rss.cnn.com/rss/edition.rss",
	'fox': "http://feeds.foxnews.com/foxnews/latest",
	'iol': "http://www.iol.co.za/cmlink/1.640"
}


@app.route("/")
def home():
	# get customized headlines, based on user input or default
	publication = request.args.get("publication")
	if not publication or publication.lower() not in RSS_FEEDS:
		publication = DEFAULTS['publication']
	articles = get_news(publication)
	
	# get customized weather based on user input or default
	city = request.args.get("city")
	if not city:
		city = DEFAULTS['city']
	weather = get_weather(city)
	
	# get customized currency data based on user input or default
	currency_from = request.args.get("currency_from")
	if not currency_from:
		currency_from = DEFAULTS['currency_from']
	currency_to = request.args.get("currency_to")
	if not currency_to:
		currency_to = DEFAULTS['currency_to']
	rate, currencies = get_rates(currency_from, currency_to)

	return render_template( "home.html",
			articles=articles,
			weather=weather,
			currency_from=currency_from,
			currency_to=currency_to,
			rate=rate,
			currencies=sorted(currencies)
		)


def get_news(query):
	query = request.args.get("publication")
	if not query or query.lower() not in RSS_FEEDS:
		publication = "bbc"
	else: 
		publication = query.lower()
	feed = feedparser.parse(RSS_FEEDS[publication])
	return feed['entries']


# Makes a call to weather API with a specific query
def get_weather(query):
	query = urllib.parse.quote(query)
	url = WEATHER_URL.format(query)
	data = urllib2.urlopen(url).read()
	parsed = json.loads(data)
	weather = None
	if parsed.get("weather"):
		weather = {
			"description": parsed["weather"][0]["description"],
			"temperature": parsed["main"]["temp"],
			"city": parsed["name"],
			"country": parsed["sys"]["country"]
		}
	return weather


def get_rates(frm, to):
	all_currency = urllib2.urlopen(CURRENCY_URL).read()
	parsed = json.loads(all_currency).get('rates')
	frm_rate = parsed.get(frm.upper())
	to_rate = parsed.get(to.upper())
	return (to_rate / frm_rate, parsed.keys())



if __name__ == "__main__":
	app.run(port=5000, debug=True)