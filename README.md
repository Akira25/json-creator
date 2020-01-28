# json-creator
This script genereates the json-files for *autoupdate*. https://github.com/Akira25/autoupdate

### parse-dict (wil be soon deprecated)
This script gets the router models from the wiki page of Freifunk Berlin and saves their (buildbot-) names
in a dictionary. In a second step the routers (internal-) names must be added by hand.

### get-router-model
This gets the internal name of a router and saves it at `routermodel.txt`. That string needs to be added
into the dictionary by hand.

*autoupdate* fetches the same string and sends it to a server, if invoked like this: `autoupdate -s`. This is 
done automatically every week.

### json-creator.py
json-creator.py will create a link definition file, containing the download links for the firmware files and the router names.
You can choose different "branches" to be generated. Please refer `json-creator.py -h`

## General Structure of json-files

```JSON
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
	"...": "..."
  }
}
```
