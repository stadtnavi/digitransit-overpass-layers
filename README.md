# digitransit-overpass-layers
Scripts to generate digitransit GeoJSON layers from overpass.

## Layers already implemented in the example HB config
* taxi stands
* car parkings (covered and opened)
* park and ride parkings
* car charging stations
* car sharing places
* bike parkings (covered and opened)
* bike charging stations
* bike monitoring stations
* bike rental places
* bike repair stations
* bike shops

## Get the GeoJson files for the new layers
The `geojson_modifier` Python program includes all methods needed and set the global variable for the array 
of `necessary_properties` that includes the keys of the properties which will be saved from deletion.

### Create your own layer config py file
The `geojson_modifier` has to be imported before generation.
```
from geojson_modifier_v2 import *
```
Global variables that have to be set:
* String destination dir
* String bounding box
* String icon SVG source file
* the String array of showed details in the popup description field (and their translations).

When adding a new field to the `details` array, make sure to add its translation to all the `details_$locale` array.

The parameters to be given to the class call (every one is a String):
```
newLayer = GenerateLayer(dest_dir, bbox, overpass_query, name_de,name_en, iconID, iconSource, details, details_de, details_en)
try: newLayer.run()
except IndexError:
    print("No locations found")
```
## Error messages while generation
```IndexError: list index out of range``` simply means that in the give boundig box area there were no overpass data 
given as the result of the query. Thanks to the ~~little hack~~ error handling above, the script will run further without 
problem and the generated GeoJson file's ```feature``` array will be empty.

```MultipleRequestsError``` means that the Overpass server was overloaded and couldn't answer the query. The request 
should be repeated. _Fact_: If there were too many queries in a short period of time, there probably will be lots of 
errors like this.

## Add layers to the UI
[Follow the original Digitransit documentation.](https://github.com/HSLdevcom/digitransit-ui/blob/master/docs/GeoJson.md#geojson-map-layers)

_Important fact:_ if even only one URL is misleading **or** even only one layer's ```feature``` array is empty (meaning 
there were no found coordinates in the given bounding box) none of the layers will be displayed.

You have to make sure that all the given URLs are valid **and** you shouldn't include an empty layer. 

## Run
```cmd
$ python generate-hb-layers.py
``` 