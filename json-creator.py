#!/usr/bin/env python3

from bs4 import BeautifulSoup
from datetime import datetime as date
import urllib.request
import os
import json
import sys
import re

"""
This script takes all routers listed in wiki of Freifunk Berlin and fetches
their image dowload links. The links are stored in a json-file. Thus they will
be easily accessible by autoupdate
"""


def print_help():
    print("""Usage:
    \t./json-creator.py <arg> [arg]
       
Options:
 -r\tgenerate release
 -t\tgenerate testing
 -d\tgenerate development
 
 -s\tgenerate an (empty) strings-dictionary file. 
 -a\twrite the complete list fetched from wiki (just for debugging)
 -h\tprint this message
 """)


def get_links(url):
    # gets all links from the given page and returns them as list
    html_page = urllib.request.urlopen(url, None)
    soup = BeautifulSoup(html_page, "html.parser")
    links = []

    for link in soup.findAll('a', attrs={'href': re.compile("^(http|https)://")}):
        links.append(link.get('href'))

    return links


def write_file(r_dict, filename):
    out = json.dumps(r_dict)

    print("Writing file "+filename+"...")
    f = open(filename, "w")
    f.write(out)
    f.close()
    print("Done.")


def load_routername_dict():
    routernamedict = {}
    
    if os.path.isfile("routernames_dict.json"):
        g = open("routernames_dict.json", "r")
        routernamedict = json.loads(g.read())
        g.close()
    
    return routernamedict


def rename_router(router, routernamedict):
    # rename the router, if it is the dict. else return routername without changes.
    new_router = routernamedict.get(router)
    if new_router == None or new_router == " ":
        return router
    else:
        return new_router


def rename_type(website_form):
    """transform the firmware-types from buildbot-form into autoupdate-form"""
    type_dict = {
        "tunnel-berlin-tunneldigger": "tunneldigger",
        "tunnel-berlin-tunneldigger_4MB": "tunneldigger",
        "default_4MB": "default"
        }
    
    if type_dict.get(website_form) != None:
        return type_dict.get(website_form)
    
    return website_form


def sort_release(r_dict, testing):
    # store the routers with release status at seperate list.
    stables = {}
    for router in r_dict:
        # continue, if current elem is creation date string.
        if router == "date":
            stables[router] = r_dict.get(router)
            continue

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
        write_file(stables, "testing.json")
    else:
        write_file(stables, "release.json")


def sort_development(r_dict):
    # store the routers with release status at seperate list.
    devs = {}
    for router in r_dict:
        # continue, if current elem is creation date string.
        if router == "date":
            devs[router] = r_dict.get(router)
            continue

        # get release status from download link: take first link from
        # router and split by '/'.  fourth elem will be 'stable' or 'unstable'
        key = list(r_dict[router])[0]
        status = r_dict.get(router)
        status = status.get(key).split("/")[4]

        # copy stables to r_dict
        if status == "unstable":
            devs[router] = r_dict.get(router)

    # write data into json-file
    write_file(devs, "development.json")


def write_all(r_dict):
    write_file(r_dict, "DEBUG_all_routers.json")


def generate_dict(r_dict):
    # generate a dictionary. This transfers the router names from
    # buildbot to the strings reffered to by the routers.
    router_list = list(r_dict)

    name_dict = {}
    for router in router_list:
        name_dict[router] = " "

    # if there is already a file, make a backup.
    # filename includes date of backup
    if os.path.isfile("routernames_dict.json"):
        today = date.now().strftime("%Y-%m-%d_%H-%M_")
        current_dir = os.getcwd()
        os.rename(current_dir+"/routernames_dict.json",
                  current_dir+"/"+today+"routernames_dict.json.bak")

    # write the empty dict to file. The original strings musst
    # be inserted by hand!
    write_file(name_dict, "routernames_dict.json")


def fetch_routers(routernamedict):

    router_links = get_links("https://wiki.freifunk.net/Berlin:Firmware")

    # let there only be the links pointing to util.berlin.freifunk.net
    # removing didnt work reliable... thus second try with appending
    links = []
    for link in router_links:
        if 'util' in link:
            links.append(link)

    # dict to save the routers and their links
    routers = {}
    # add creation date as
    today = date.today()
    routers["date"] = str(today.strftime("%Y%m%d"))

    # parse the images for the routers
    for link in links:
        router_link = link
        router = (link)[47:]
        # if the router-link states multiple router names: oly take the first one
        # omit substring &complete=true (occurs for routers, which doesn't have a stable-release yet)
        router_name = str(router).split(",")[0]
        router_name = router_name.split("&")[0]

        # debugging
        print("fetching "+router_name+" ...")
        # print(link)

        image_links = get_links(link)
        # omit any link, thats not pointing to sysupgrade-images
        # same problem as above...
        images = {}
        for link in image_links:
            if 'sysupgrade' in link:
                firmware_type = str(link).split("/")[-2]
                #transform buildbot types to autoupdate tpes
                firmware_type = rename_type(firmware_type)
                images[firmware_type] = link

        # if there weren't any links (due to development-firmware), try to get the image-links again.

        if len(images) == 0:
            image_links = get_links(router_link+"&complete=true")
            # print(image_links)
            images.clear()  # just to be sure...
            for link in image_links:
                if 'sysupgrade' in link:
                    firmware_type = str(link).split("/")[-2]
                    images[firmware_type] = link

        # print(images)

        if len(images) != 0:
            router_name = rename_router(router_name, routernamedict)
            routers[router_name] = images
        else:
            err_string = router_name+" did not contain any links. It won't be included!"
            print(err_string)
            # stderr do print only at the and of the output. I prefer it to be in between
            # the other routers...
            # sys.stderr.write(err_string)

    return routers

    """
    #DEBUGGING: load json-file with debugging-list
    print("fetching routers")
    g = open("routers.json.bkp", "r")
    dictionary = g.read()
    data = {}
    data = json.loads(dictionary)
    data.pop("date")
    g.close()
    print("fetching done.")
    
    return data
    """


def invalid_invokation(opt):
    errstring = "invalid option: "+opt + \
        "\nStart script with -h for further information\n"
    sys.stderr.write(errstring)
    exit(2)


def check_cmd_option(option):
    option_list = ["-r", "-t", "-d", "-s", "-a", "-h"]

    if option not in option_list:
        invalid_invokation(option)


"""
##

Main-Programm

##
"""

"""
#read the options and start the function respectively
"""

argc = len(sys.argv)
# exit, if no options are given
if argc == 1:
    print_help()
    exit(2)


arg_index = 1
func = str(sys.argv[arg_index])
check_cmd_option(func)
if func == "-h":
    print_help()
    exit(0)

if func == "-s":
    # give fetch_routers() an empty dictionary. Otherwise, function will generate a dictionary
    # not with the buildbot-names as keys, but with the routerstrings.
    routernames = {}
    complete_router_list = fetch_routers(routernames)
    generate_dict(complete_router_list)
    exit(0)

# get routername-strings from dict. While fetching the download links, already replace
# the builbot names by the original ones.
routernamedict = load_routername_dict()
complete_router_list = fetch_routers(routernamedict)

while arg_index < argc:
    func = str(sys.argv[arg_index])
    check_cmd_option(func)

    # True and False control the name of the output file: False will generate a "release.json"
    # True will generate a "testing.json"
    if func == "-r":
        sort_release(complete_router_list, False)
    elif func == "-t":
        sort_release(complete_router_list, True)
    elif func == "-d":
        sort_development(complete_router_list)
    elif func == "-a":
        write_all(complete_router_list)
    else:
        invalid_invokation(func)

    arg_index += 1
