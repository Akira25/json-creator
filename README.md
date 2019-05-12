# json-creator
This collection of scripts helps to genereate the json-files for *autoupdate*. https://github.com/Akira25/autoupdate

### parse-dict
This script gets the router models from the wiki page of Freifunk Berlin and saves their (buildbot-) names
in a dictionary. In a second step the routers (internal-) names must be added by hand.

### get-router-model
This gets the internal name of a router and saves it at `routermodel.txt`. That string needs to be added
into the dictionary by hand.

Please feel free to send me the names of router models and their corresponding strings. I will add them into the dict-file in this repository

### parse-links
Finally parse-links will create a link definition file, containing the download links for the firmware files and the router names.
Only routers which name ist defined in the dict-file will be included.

## General Structure of router.json

```JSON
{
  "date":"20190512",
  "ROUTER-NAME#1":
  {
    "default": "http://link-to-sysupgrade.bin",
    "tunneldigger": "http://link-to-sysupgrade.bin"
  },
  "ROUTER-NAME#2":
  {
    "default": "http://link-to-sysupgrade.bin",
    "tunneldigger": "http://link-to-sysupgrade.bin"
  }
}
```
