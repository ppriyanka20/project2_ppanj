#################################
##### Name: Priyanka Panjwani
##### Uniqname: ppanj
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

BASE_URL = 'https://www.nps.gov'
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}

my_api_key = secrets.API_KEY

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, name, address, zipcode, phone, category):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''

    url = "https://www.nps.gov/index.htm" #initial url to scrape
    #response = requests.get(url) #access the data from the webpage
    soup = BeautifulSoup(make_url_request_using_cache(url, CACHE_DICT), 'html.parser') #create beautiful soup object

    dropdownMenu = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch') #access the dropdown menu information
    all_links = dropdownMenu.find_all('a') #from dropdown menu, get all 'a' tags which refer to each state and it's url

    stateNames = [] #empty list for state names
    stateUrls = [] #empty list for state urls
    for link in all_links: #parse through the 'a' tags and only get the urls and the state names
        stateUrls.append(link.get('href')) #add urls
        stateNames.append(link.text.strip().lower()) #add stateNames

    state_url_dict = {} #empty dictionary for state: url values
    url_firsthalf = "https://www.nps.gov" #will concatenate this with the scraped state url

    for i in range(len(stateNames)): #go though the state names and urls and add to the dictionary
        state_url_dict[stateNames[i]] = url_firsthalf + stateUrls[i]

    return state_url_dict #return the dictionary


def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    #response = requests.get(site_url) #access the data from the site webpage
    parkSoup = BeautifulSoup(make_url_request_using_cache(site_url, CACHE_DICT), 'html.parser') #create beautiful soup object

    #find the different instance variables: name, category, address, zipcode, phonenumber
    #if statements check if the information actually exists, otherwise it is assigned none to ensure that nothing crashes
    #name:
    if parkSoup.find('div', class_='Hero-titleContainer clearfix').find('a'):
        name = parkSoup.find('div', class_='Hero-titleContainer clearfix').find('a').text.strip() #access the name of the park
    else:
        name = ""
    #category:
    if parkSoup.find('span', class_='Hero-designation'):
        category = parkSoup.find('span', class_='Hero-designation').text.strip() #access the type of the park
    else:
        category = ""
    #address:
    if parkSoup.find('span', itemprop='addressLocality'):
        address = parkSoup.find('span', itemprop='addressLocality').text.strip() + ", " + parkSoup.find('span', itemprop='addressRegion').text.strip()
    else:
        address = ""
    #zipcode:
    if parkSoup.find('span', itemprop='postalCode'):
        zip = parkSoup.find('span', itemprop='postalCode').text.strip()
    else:
        zip = ""
    #phone number:
    if parkSoup.find('span', itemprop='telephone'):
        phonenumber = parkSoup.find('span', itemprop='telephone').text.strip()
    else: 
        phonenumber = ""

    return NationalSite(name=name, address=address, zipcode=zip, phone=phonenumber, category=category)

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    
    #response = requests.get(state_url)
    soup = BeautifulSoup(make_url_request_using_cache(state_url, CACHE_DICT), 'html.parser') #create beautiful soup object

    allSites = soup.find_all('div', class_='col-md-9 col-sm-9 col-xs-12 table-cell list_left') #get all site info for state

    site_link_list = [] #empty list for all the site links
    firsthalf_url = "https://www.nps.gov" #will concatenate this with the scraped state url

    for site in allSites: #loop to get just the site link endings
        currentLink = site.find('a').get('href')
        site_link_list.append(firsthalf_url + currentLink)

    nationalsite_instances = []
    for site in site_link_list:
        new_instance = get_site_instance(site)
        nationalsite_instances.append(new_instance)
    
    return nationalsite_instances


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    baseurl = "http://www.mapquestapi.com/search/v2/radius"
    params = {'key': my_api_key, 'origin': site_object.zipcode, 'radius': 10, 'maxMatches': 10, 'ambiguities': "ignore", 'outFormat': "json"}
    mapResponse = make_map_request_using_cache(baseurl, params, CACHE_DICT)
    #mapquest_json = mapResponse.json()
    return mapResponse
    #list_of_places = mapResponse['searchResults']

def format_nearby_places(list_of_places):
    '''formats the dictionary return from the MapQuest API into an easier format of nested dictionaries
    Each key of the dictionary is a place, and the place maps to another dictionary which has all 
    the relevant information for that place: the category, address and city
    
    Parameters
    ----------
    list_of_places: list
        the list of places, received from the 'searchResults' key in the MapQuest API dict

    Returns
    -------
    dict
        a nested dictionary. The key is the places name, the value is a dictionary of relevant info
    '''
    nearbyplaces_dict = {} #dictionary to be returned
    for place in list_of_places:
        name = place['fields']['name']
        nearbyplaces_dict[name] = {} #set the name of the place as a key, to an empty dictionary
        #if statements to create a dictionary of each places name mapping to a dictionary of information:
        if place['fields']['group_sic_code_name_ext']: #if there is a category
            category = place['fields']['group_sic_code_name_ext'] #set the category to this
            nearbyplaces_dict[name]['category'] = category #create new key/value in the name dict
        else:
            category = "no category" #else there is no category
            nearbyplaces_dict[name]['category'] = category

        if place['fields']['address']: #if there is an address
            address = place['fields']['address'] #set the address to this
            nearbyplaces_dict[name]['address'] = address
        else:
            address = "no address"
            nearbyplaces_dict[name]['address'] = address

        if place['fields']['city']: #if there is a city
            city = place['fields']['city'] #set the city to this
            nearbyplaces_dict[name]['city'] = city
        else:
            city = "no city"
            nearbyplaces_dict[name]['city'] = city
    return nearbyplaces_dict

def load_cache():
    '''Loads the file data into a cache dict, which is then returned
    
    Parameters
    ----------
    none
    
    Returns
    -------
    dict
        a dictionary of the cache data, with the keys as urls and values the request information
    '''
    try: #see if there is any existing data in the cache file
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents) #add this information to our dictionary
        cache_file.close()
    except: #there is no existing data, return a blank dictionary
        cache = {}
    return cache

def save_cache(cache):
    '''Saves any new cache data to the cache file
    
    Parameters
    ----------
    cache: dict
        a dictionary with the cache data. The urls are the keys
    
    Returns
    -------
    none
    '''
    cache_file = open(CACHE_FILE_NAME, 'w') #open the file
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write) #write the new urls and data to the cache file
    cache_file.close()

def make_url_request_using_cache(url, cache):
    '''Makes a url request using the cache data. If the url is not already in
        our cache data, it saves it to the cache data. 
    
    Parameters
    ----------
    url: string
        the url used for the request
    cache: dict
        the cache dict with the information we are searching through 

    Returns
    -------
    string
        the text of the data received from the request, that is associated with the url
    '''
    if (url in cache.keys()): # the url is has already been searched
        print("Using cache")
        return cache[url]
    else: #this is a new request, save the requested data to our cache file and dictionary
        print("Fetching")
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

def make_map_request_using_cache(url, params, cache):
    '''Makes a url request to MapQuest using the cache data. If the url is not already in
        our cache data, it saves it to the cache data. 

    Parameters
    ----------
    url: string
        the url used for the request
    params: dictionary
        the additional parameters needed for the request
    cache: dictionary
        the cache dictionary to search through

    Returns
    -------
    string
        the text of the data received from the MaqQuest request, that is associated with the url
    '''
    if (url in cache.keys()): # the url has already been searched
        print("Using cache")
        return cache[url]
    else: #this is a new request, add the info to our cache file and dictionary
        print("Fetching")
        response = requests.get(url, params)
        cache[url] = response.json()
        save_cache(cache)
        return cache[url]


if __name__ == "__main__":

    state_urls = build_state_url_dict() #get the initial dictionary of state, url key/values
    userinput = input('Enter a state name (e.g. Michigan, michigan) or "exit":').lower() #initial user input

    while True: #as long as we don't input exit

        if userinput == "exit": #make sure the user is not trying to exit
            break

        elif userinput in state_urls.keys(): #make sure it is a valid search
            stateurl = state_urls[userinput] #search for the specific url
            list_of_sites = get_sites_for_state(stateurl) #get all the sites for that state
            num = 1
            print("-----------------------------------")
            print(f"List of national sites in {userinput}")
            print("-----------------------------------")

            for site in list_of_sites: #print the information for each site
                print(f"[{num}] {site.info()}")
                num +=1

            while True:
                #ask for input again, but this time it's for a number to detail search
                userinput = input('Choose the number for detail search or "exit" or "back":').lower()

                if userinput == "exit": #if they want to exit, break
                    break

                elif userinput == "back": #if they want to go back
                    #ask for a new input so the outer while loop doesn't break
                    userinput = input('Enter a state name (e.g. Michigan, michigan) or "exit":').lower()
                    break #break from this while loop

                elif userinput.isnumeric() and float(userinput) >0 and float(userinput).is_integer()\
                     and int(float(userinput)) in range(len(list_of_sites)+1):
                    #else, we check to see if it's a valid number entry
                    site_in_question = list_of_sites[int(float(userinput))-1] #the site the user wants
                    nearby_places_dict = get_nearby_places(site_in_question) #get dict of nearby places
                    list_of_places = nearby_places_dict['searchResults'] #get the relevant list
                    formatted_places = format_nearby_places(list_of_places) #a nicely formatted dictionary of the nearby places

                    #printing the output of the details on the site:
                    print("-----------------------------------")
                    print(f"Places near {site_in_question.name}")
                    print("-----------------------------------")
                    for key in formatted_places.keys():
                        attributes = formatted_places[key] #get the dict of attributes for that place
                        print(f"- {key} ({attributes['category']}): {attributes['address']}, {attributes['city']}")

                else: #it is not a valid input, prompt them again.
                    print("Invalid input\n")
                    print("------------------------------------")

        else: #if it isn't valid prompt them to search again
            print("\nSorry! Please enter the full name of a valid state.")
            userinput = input('Enter a state name (e.g. Michigan, michigan) or "exit":').lower() #restart input