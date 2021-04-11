#################################
##### Name: Priyanka Panjwani
##### Uniqname: ppanj
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key


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
    response = requests.get(url) #access the data from the webpage
    soup = BeautifulSoup(response.text, 'html.parser') #create beautiful soup object

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
    response = requests.get(site_url) #access the data from the site webpage
    parkSoup = BeautifulSoup(response.text, 'html.parser') #create beautiful soup object

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
    
    response = requests.get(state_url)
    soup = BeautifulSoup(response.text, 'html.parser') #create beautiful soup object

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
    pass
    

if __name__ == "__main__":

    state_urls = build_state_url_dict() #get the initial dictionary of state, url key/values
    userinput = input('Enter a state name (e.g. Michigan, michigan) or "exit":').lower() #user input
    
    while userinput != "exit": #make sure the user is not trying to exit
        if userinput in state_urls.keys(): #make sure it is a valid search

            stateurl = state_urls[userinput] #search for the specific url
            list_of_sites = get_sites_for_state(stateurl) #get all the sites for that state
            num = 1
            for site in list_of_sites: #print the information for each site
                print(f"[{num}] {site.info()}")
                num +=1
        else: #if it isn't valid prompt them to search again
            print("\nSorry! Please enter the full name of a valid state.")
        userinput = input('Enter a state name (e.g. Michigan, michigan) or "exit":').lower() #restart input