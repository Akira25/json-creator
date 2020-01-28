#!/usr/bin/env python3

from bs4 import BeautifulSoup
from datetime import date
import urllib.request
import json
import sys
import re


def print_help():
    print("""Usage:
    \t./generate_release.py <arg> [arg]
       
Options:
 -r\tgenerate release
 -t\tgenerate testing
 -d\tgenerate developement
 
 -a\twrite the complete list fetched from wiki (just for debugging)
 -h\tprint this message
 """)


#gets all links from the given page and returns them as list
def get_links(url):
    html_page = urllib.request.urlopen(url,None)
    soup = BeautifulSoup(html_page, "html.parser")
    links = []

    for link in soup.findAll('a', attrs={'href': re.compile("^(http|https)://")}):
        links.append(link.get('href'))
        
    return links


def write_file(r_dict, filename):
    out = json.dumps(r_dict)

    print("Writing file "+filename+"...")
    f = open(filename,"w")
    f.write(out)
    f.close()
    print("Done.")


def sort_release(r_dict, testing):
    # store the routers with release status at seperate list.
    stables = {}
    for router in r_dict:
        # get release status from download link: take first link from 
        # router and split by '/'.  fourth elem will be 'stable' or 'unstable'
        key = list(r_dict[router])[0]
        status = r_dict.get(router)
        status = status.get(key).split("/")[4]
        
        # copy stables to r_dict
        if status == "stable":
            stables[router] = r_dict.get(router)
        
    # write data into json-file
    # distinguish between release and testing
    if testing == True:
        write_file(stables,"testing.json")
    else:
        write_file(stables,"release.json")

    
def sort_development(r_dict):
    # store the routers with release status at seperate list.
    devs = {}
    for router in r_dict:
        # get release status from download link: take first link from 
        # router and split by '/'.  fourth elem will be 'stable' or 'unstable'
        key = list(r_dict[router])[0]
        status = r_dict.get(router)
        status = status.get(key).split("/")[4]
        
        # copy stables to r_dict
        if status == "unstable":
            devs[router] = r_dict.get(router)
        
    # write data into json-file
    write_file(devs,"development.json")


def write_all(r_dict):
    write_file(r_dict,"DEBUG_all_routers.json")


def fetch_routers():
    
    router_links = get_links("https://wiki.freifunk.net/Berlin:Firmware")
    
    #let there only be the links pointing to util.berlin.freifunk.net
    #removing didnt work reliable... thus second try with appending
    links = []
    for link in router_links:
        if 'util' in link:
            links.append(link)
    
    
    #dict to save the routers and their links
    routers = {} 
    #add creation date as 
    today = date.today()
    routers["date"] = str(today.strftime("%Y%m%d"))
    
    #parse the images for the routers
    for link in links:
        router_link = link
        router = (link)[47:]
        #if the router-link states multiple router names: oly take the first one
        #omit substring &complete=true (occurs for routers, which doesn't have a stable-release yet)
        router_name = str(router).split(",")[0]
        router_name = router_name.split("&")[0]
        
        #debugging
        print("fetching "+router_name+" ...")
        #print(link)
        
        image_links = get_links(link)
        #omit any link, thats not pointing to sysupgrade-images
        #same problem as above...
        images = {}
        for link in image_links:
            if 'sysupgrade' in link:
                firmware_type = str(link).split("/")[-2]
                images[firmware_type] = link
        
        #if there weren't any links (due to developement-firmware), try to get the image-links again.
        
        if len(images) == 0:
            image_links = get_links(router_link+"&complete=true")
            #print(image_links)
            images.clear()  # just to be sure...
            for link in image_links:
                if 'sysupgrade' in link:
                    firmware_type = str(link).split("/")[-2]
                    images[firmware_type] = link
                    
        #print(images)
        
        if len(images) != 0:
            routers[router_name] = images
        else:
            print(router_name+" did not contain links. It won't be added.")
    
    return routers
    
    """
    #DEBUGGING: load json-file with debugging-list
    g = open("routers.json.bkp", "r")
    dictionary = g.read()
    data = {}
    data = json.loads(dictionary)
    data.pop("date")
    g.close()
    
    return data
    """


"""
##

Main-Programm

##
"""

#get arguments and start functions
argc = len(sys.argv)
arg_index = 1

while arg_index < argc:
    func = str(sys.argv[arg_index])
    
    if func == None:
        sys.stderr.write("invalid argument! Start script with -h\n")
        exit()
    
    if func == "print_help()":
        print_help()
        exit()
    
    complete_router_list = fetch_routers()
    
    #True and False control the name of the output file: False will generate a "release.json"
    #True will generate a "testing.json"
    if func == "-r":
        sort_release(complete_router_list,False)
    elif func == "-t":
        sort_release(complete_router_list,True)
    elif func == "-d":
        sort_development(complete_router_list)
    elif func == "-a":
        write_all(complete_router_list)
    else:
        errstring = "invalid option: "+func+"\n"
        sys.stderr.write(errstring)
        exit(False)

    arg_index +=1
    
