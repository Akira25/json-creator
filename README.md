# json-creator
This script genereates the json-files for *autoupdate*. https://github.com/Akira25/autoupdate


## json-creator.py
json-creator.py holds different functions for generating json-files. 
```
Usage:
        ./json-creator.py <arg> [arg]
       
Options:
 -r     generate release
 -t     generate testing
 -d     generate development
 
 -s     generate an (empty) strings-dictionary file. 
 -a     write the complete list fetched from wiki (just for debugging)
 -h     print this message
```
At least one argument is needed. More arguments are optional.


## Workflow
### dictionary creation
At first, you should generate a dictionary with `-s`-option. This file will handle the conversion
from (internal) buildbot-names into the original router-strings.

Unfortunately, you need to add the router-strings by hand. To avoid to much work on that, you will
find a pre-filled dictionary in this repository. (see `routernames_dict.json`)

If there already is a dictionary, json-creator will save a backup before it saves the new one.

*Note: routerstrings can be obtained automatically via autoupdate. They are 'send' to a freely chosen*
*web-address from the config-files.*


### generate link definition files
Equipped with the routernames_dict you can start json-creator with `-r -t` or `-d`.

`-r | release.json`: 
* contains only routers with stable-release-status

`-t | testinng.json`:
* the same file as release.json, but named differently. In that way we realise different update-branches

`-d | development.json`:
* contains all routers with a development-snapshot avaiable


### link-def-files and certification
`autoupdate` will look for `$BRANCH_NAME.json` at a specified web-address. Additionally it will interpret
any other file in the same directory machting `*$BRANCH_NAME*` as certificate for the link-def-file.

Verification is handled by openwrt-included usign, a derivate of openbsd-signify. For a package avaiable
at debian-based systems, have a look [here.](https://packages.debian.org/sid/signify-openbsd)
Currently, autoupdate only do sysupgrade, if the link-def was signed by at least 4 independant keys.


## Not essentially important, but possibly useful:
### script: get-router-model
This gets the internal name of a router and saves it at `routermodel.txt`. That string needs to be added
into the dictionary by hand.

`autoupdate` fetches the same string and sends it to a server, if invoked like this: `autoupdate -s`. This is 
done automatically every week.


## General Structure of link-def-files

```
{
  "date":"20190512",
  "ROUTER-NAME#1":
  {
    "default": "http://link-to-sysupgrade.bin",
    "tunneldigger": "http://link-to-sysupgrade.bin"
    "...": "..."
  },
  "ROUTER-NAME#2":
  {
    "default": "http://link-to-sysupgrade.bin",
    "tunneldigger": "http://link-to-sysupgrade.bin"
    "...": NULL
  }
}
```
