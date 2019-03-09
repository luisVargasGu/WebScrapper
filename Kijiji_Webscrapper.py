from multiprocessing import Pool
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import urllib.request
import datetime
import time
import sys
import re
import os


# this function checks the similarities between ads
# SequenceMatcher checks how similar strings are and returns a percent
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# Checks the Similarities between the current ad and others in the database
def check_equal(ad, key, all_ads):
    if all_ads.__len__() != 0:
        if key not in all_ads:
            for key_, value in all_ads.items():
                counter = 0
                checker = [similar(ad["Title"], value["Title"]),
                           similar(ad["Address"], value["Address"]),
                           similar(ad["Url"], value["Url"]),
                           similar(ad["Description"], value["Description"]),
                           similar(ad["Phone"], value["Phone"]),
                           similar(ad["Property Type"], value["Property Type"]),
                           similar(ad["Location"], value["Location"]),
                           similar(ad["Date"], value["Date"]),
                           similar(ad["Price"], value["Price"])]
                # This is done to avoid getting thesame ad more than once
                # By checking all of the matching fields againts other ads we avoid
                # Adding the same ad more than once
                for percent in checker:
                    if percent > 0.65:
                        counter += 1
            if counter != 0 and counter > 4:
                return False
        else:
            return False
    return True


def write_ads(ad_dict, filename):  # Writes ads from given dictionary to given file
    file = open(filename, "a", encoding="utf-8")
    all_ads = read_ads('../Files,Databases/Recorded Ads')
    w_i = 0
    for ad_id, value in ad_dict.items():
        if check_equal(value, ad_id, all_ads):
            file.write(str(ad_id))
            file.write(str(value) + "\n")
            w_i += 1
    print("Wrote: " + str(w_i) + " New Ads.")
    file.close()


def parse_ads(html):  # Parses ad html trees and sorts relevant data into a dictionary
    ad_info = {}

    # Initialize variables for scraping
    source = urllib.request.urlopen('http://www.kijiji.ca' + html.get("data-vip-url")).read()
    soup_ = BeautifulSoup(source, "html.parser")
    try:
        ad_info["Title"] = html.find('a', {"class": "title"}).text.strip()
    except:
        print('[Error] Unable to parse Title data.')

    try:
        ad_info["Image"] = str(html.find('img'))
    except:
        print('[Error] Unable to parse Image data')

    # Find The Url
    ad_info["Url"] = 'http://www.kijiji.ca' + html.get("data-vip-url")

    # Get Initial Description
    if html.find('div', {"class": "description"}) is not None:
        description = html.find('div', {"class": "description"}).text.strip()
        ad_info["Description"] = description

    # Phone Number Hunting
    table = soup_.findAll('div', attrs={"class": "descriptionContainer-3820652057"})
    p_text = ''
    if len(table) != 0:
        p_tags = table[0].select("div > p")
        # Regular Expression for finding phone numbers
        regex = re.compile(r'(\d{3}[-\.\s]\d{3}[-\.\s]\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]\d{4}|\d{3}[-\.\s]\d{4})')
        p_text = ''
        numbers = ""
        for x in p_tags:
            p_text += x.text
        matchlist = regex.findall(p_text)
        for all_ in matchlist:
            numbers += str(all_)
        ad_info["Phone"] = numbers
        # Description Gathering
        ad_info["Description"] = p_text

    else:
        ad_info["Phone"] = "N/A"

    # Property Type Gathering
    property_re_ap = re.compile(r'[a,A]partment')
    prop_cn_regex = re.compile(r'[C,c]ondo')
    if property_re_ap.findall(ad_info['Description']) or property_re_ap.findall(ad_info['Title']) or \
            property_re_ap.findall(p_text):
        ad_info['Property Type'] = 'Apartment'
    elif prop_cn_regex.findall(ad_info['Description']) or prop_cn_regex.findall(ad_info['Title']) or \
            property_re_ap.findall(p_text):
        ad_info['Property Type'] = 'Condo'
    else:
        ad_info['Property Type'] = 'N/A'

    # Location and Address Gathering
    date_ = html.find('span', {"class": "date-posted"}).text
    address = "N/A"
    location = "N/A"
    if soup_.find('span', {"class": "address-2932131783"}) is not None:
        address = soup_.find('span', {"class": "address-2932131783"}).text.strip()
    if html.find('div', {"class": "location"}) is not None:
        location = html.find('div', {"class": "location"}).text.strip()
        location = location.replace(date_, '')
    ad_info["Location"] = location
    ad_info["Address"] = address

    ad_info["Date"] = date_
    # Regular Expression used to find how long ago the ad was posted
    date_regex = re.compile(r'\<\s[\d]+\s[minutes,hours]*\sago')
    if date_regex.findall(ad_info['Date']):
        # Number of hours or Minutes since posting
        # Has all the Options provided By Kijiji
        number_of = date_regex.findall(ad_info['Date'])[0].split(" ")
        if int(number_of[1]) > 12 and number_of[2] == "hours" and int(datetime.datetime.now().hour) < 13:
            yesterday = datetime.date.today() - datetime.timedelta(1)
            ad_info["Date"] = yesterday.strftime('%d-%b-%Y')
        elif ad_info['Date'] == 'Yesterday':
            yesterday = datetime.date.today() - datetime.timedelta(1)
            ad_info["Date"] = yesterday.strftime('%d-%b-%Y')
        else:
            ad_info["Date"] = datetime.date.today().strftime('%d-%b-%Y')

    # Basic error Checking
    try:
        ad_info["Price"] = html.find('div', {"class": "price"}).text.strip()
    except:
        print('[Error] Unable to parse Price data.')

    return ad_info


def scrape(url):  # Pulls page data from a given kijiji url and finds all ads on each page
    # Initialize variables for loop
    ad_dict = {}
    good_ads = {}
    # Excluded words may be put in a file
    excluded_lst = ['house']
    try:
        page = urllib.request.urlopen(url).read()  # Get the html data from the URL
    except:
        print("[Error] Unable to load " + url)
        sys.exit(1)

    soup = BeautifulSoup(page, "html.parser")

    kijiji_ads = soup.find_all("div", {"class": "regular-ad"})  # Finds all ad trees in page html.
    for ad in kijiji_ads:
        ad_id = ad['data-ad-id']  # Get the ad id
        ad_dict[ad_id] = parse_ads(ad)  # Parse data from ad
        ad_info = ad_dict[ad_id]["Title"].lower() + ad_dict[ad_id]["Description"].lower() + \
                  ad_dict[ad_id]["Property Type"].lower()
        if not [False for match in excluded_lst if match in ad_info]:
            good_ads[ad_id] = ad_dict[ad_id]
        print('[Okay] New ad found! Ad id: ' + ad_id)

    return good_ads


def read_ads(filename):  # Reads given file and creates a dict of ads in file
    import ast
    if not os.path.exists(filename):  # If the file doesn't exist, it makes it.
        file = open(filename, 'w')
        file.close()

    ad_dict = {}
    with open(filename, 'r', encoding="utf-8") as file:
        for line in file:
            if line.strip() != '':
                index = line.find('{')
                ad_id = line[:index]
                dictionary = line[index:]
                dictionary = ast.literal_eval(dictionary)
                ad_dict[ad_id] = dictionary
    return ad_dict


if __name__ == '__main__':
    # Check how long the program took to run
    start = time.time()
    full_ads = {}
    # Careful with opening up too many you may crash your computer
    # Multithreading
    p = Pool(25)  # Pool tells how many at a time
    url_list = ["https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273r50.0" +
                "?ad=offering&price=1600__&for-rent-by=ownr"]
    # Goes Through All the pages on Kijiji
    for i in range(2, 101):
        url = 'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-' + str(i) + \
              '/c37l1700273r50.0?ad=offering&price=1600__&for-rent-by=ownr'
        url_list.append(url)
    records = p.map(scrape, url_list)
    for ad_dic in records:
        full_ads.update(ad_dic)
    # full_ads.update(scrape(url_list[0]))
    write_ads(full_ads, '../Files,Databases/Recorded Ads')
    end = time.time()
    print(str((end - start) / 60) + ": Minutes")
