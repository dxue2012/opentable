import sys
import datetime
import requests
from bs4 import BeautifulSoup

def date_to_string(date):
    return date.strftime('%Y-%m-%d')

def extract_time(datetime_str):
    return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M").strftime('%H:%M')

def post_request(rid, date):
    # CR dxue for dxue: hard-code nakazawa's sushi bar for now. Make this configurable
    url = "http://www.opentable.com/restaurant/profile/" + rid + "/search"
    dateTime = date_to_string(date) + " 19:00"
    payload = {"covers" : 2, "dateTime": dateTime}
    return requests.post(url, data=payload)

def parse_response(response):
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    error_message = soup.find('h4', class_='dtp-result-text')
    if error_message is not None:
        return []
    else:
        all_buttons = soup.find_all('a', {'class':['dtp-button']})
        unavailable_buttons = soup.find_all('a', {'class':['unavailable']})
        available_datetimes = [button["data-datetime"] for button in all_buttons if button not in unavailable_buttons]
        return [extract_time(x) for x in available_datetimes]

def available_times(rid, date):
    return parse_response(post_request(rid, date))

def has_availability_on(date):
    return len(available_times_on(date)) == 0

def get_restaurant_rid(restaurant_str):
    url = "http://www.opentable.com/" + restaurant_str
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    try:
        return soup.find('a', class_='favorite-button')['data-rid']
    except Exception:
        return None

def main():
    restaurant = sys.argv[1]
    rid = get_restaurant_rid(restaurant)
    if rid is None:
        print restaurant + " not found. Make sure the url http://www.opentable.com/RESTAURANT is valid."
        exit(1)
    else:
        today = datetime.date.today()
        print "looking for available for " + restaurant + " in the next 30 days..."
        for x in range(30):
            date = today + datetime.timedelta(days=x)
            avail = available_times(rid, date)
            print "has availability on " + date_to_string(date) + "? " + str(avail)
        print "Done!"

main()
