import sys
import datetime
import requests
from bs4 import BeautifulSoup

def date_to_string(date):
    return date.strftime('%Y-%m-%d')

def extract_time(datetime_str):
    return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M").strftime('%H:%M')

def post_request(date):
    # CR dxue for dxue: hard-code nakazawa's sushi bar for now. Make this configurable
    url = "http://www.opentable.com/restaurant/profile/118903/search"
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

def available_times_on(date):
    return parse_response(post_request(date))

def has_availability_on(date):
    return len(available_times_on(date)) == 0

def main():
    restaurant = sys.argv[1]
    today = datetime.date.today()
    for x in range(30):
        date = today + datetime.timedelta(days=x)
        avail = available_times_on(date)
        print len(avail)
        print "The restaurant " + restaurant + " has availability on " + date_to_string(date) + "? " + str(avail)

main()
