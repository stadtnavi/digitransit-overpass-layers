#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from geojson_modifier import *
import os

Herrenberg_bbox = os.getenv('ENV_BBOX', "48.51592209023528,8.533287048339844,48.72607645125842,9.036598205566406")
svgSourceDir = os.getenv('ENV_ICONSRC', "./layer-icons/")

geojson_destDir = os.getenv('ENV_DDIR', "../digitransit-ui/static/assets/geojson/hb-layers/")
details = ["capacity", "opening_hours", "contact:phone", "phone", "wheelchair", "fee", "contact:website", "website"]
details_de = ["Kapazität", "Öffnungszeiten", "Telefon", "Telefon", "Barrierefrei", "Gebühr", "Webseite", "Webseite"]
details_en = ["Capacity", "Opening hours", "Phone", "Phone", "Wheelchair", "Fee", "Website", "Website"]

#bikeMon = GenerateLayer(geojson_destDir, Herrenberg_bbox,  """nwr["man_made"="monitoring_station"]["monitoring:bicycle"="yes"]({{bbox}});""", "Fahrradzählstelle", "Bicycle monitoring station", "bikeMonIcon", svgSourceDir+"bikemonitoring.svg", details, details_de, details_en)
#try: bikeMon.run()
#except IndexError:
#    print("No locations found")

bikeCharge = GenerateLayer(geojson_destDir, Herrenberg_bbox, "nwr[amenity=charging_station][bicycle=yes]({{bbox}});", "Fahrradladestation", "Bicycle charging station", "bikeChargeIcon", svgSourceDir+"bikecharge.svg", details, details_de, details_en)
try: bikeCharge.run()
except IndexError:
    print("No locations found")

bikeParkOp = GenerateLayer(geojson_destDir, Herrenberg_bbox, "nwr[amenity=bicycle_parking][covered=no]({{bbox}});", "Fahrradstellplatz", "Open-air bike park", "bikeParkOpIcon", svgSourceDir+"openedbikepark.svg", details, details_de, details_en)
try: bikeParkOp.run()
except IndexError:
    print("No locations found")

bikeParkCov = GenerateLayer(geojson_destDir, Herrenberg_bbox, "nwr[amenity=bicycle_parking][covered=yes]({{bbox}});", "Überdachter Fahrradstellplatz", "Covered bike park", "bikeParkCovIcon", svgSourceDir+"coveredbikepark2.svg", details, details_de, details_en)
try: bikeParkCov.run()
except IndexError:
    print("No locations found")

bikeRent = GenerateLayer(geojson_destDir, Herrenberg_bbox, "nwr[amenity=bicycle_rental]({{bbox}});", "Fahrradverleih", "Bike rental", "bikeRentIcon", svgSourceDir+"bikerent.svg", details, details_de, details_en)
try: bikeRent.run()
except IndexError:
    print("No locations found")

bikeRep = GenerateLayer(geojson_destDir, Herrenberg_bbox, "nwr[amenity=bicycle_repair_station]({{bbox}});", "Fahrradreparaturstation", "Bicycle repair station", "bikeRepIcon", svgSourceDir+"bikerepair.svg", details, details_de, details_en)
try: bikeRep.run()
except IndexError:
    print("No locations found")

bikeShop = GenerateLayer(geojson_destDir, Herrenberg_bbox, "nwr[shop=bicycle]({{bbox}});", "Fahrradgeschäft", "Bicycle shop", "bikeShopIcon", svgSourceDir+"bikeshop2.svg", details, details_de, details_en)
try: bikeShop.run()
except IndexError:
    print("No locations found")

carCharge = GenerateLayer(geojson_destDir, Herrenberg_bbox, "nwr[amenity=charging_station][car=yes]({{bbox}});", "Elktroauto-Ladestation", "Car charging station", "carChargeIcon", svgSourceDir+"carcharge.svg", details, details_de, details_en)
try: carCharge.run()
except IndexError:
    print("No locations found")

carParkOp = GenerateLayer(geojson_destDir, Herrenberg_bbox,  """nwr[amenity=parking]["access"!="private"]["access"!="customers"]["parking"="surface"]({{bbox}}); """, "Parkplatz", "Car parking", "carParkOpIcon", svgSourceDir+"openedcarpark.svg", details, details_de, details_en)
try: carParkOp.run()
except IndexError:
    print("No locations found")

carParkCov = GenerateLayer(geojson_destDir, Herrenberg_bbox,   """nwr[amenity=parking]["access"!="private"]["access"!="customers"]["parking"!="surface"]({{bbox}}); """, "Parkhaus/Tiefgarage", "Multi-story/underground car parking", "carParkCovIcon", svgSourceDir+"coveredcarpark.svg", details, details_de, details_en)
try: carParkCov.run()
except IndexError:
    print("No locations found")

carShare = GenerateLayer(geojson_destDir, Herrenberg_bbox, "nwr[amenity=car_sharing]({{bbox}});", "Car-Sharing", "Car sharing", "carShareIcon", svgSourceDir+"carshare.svg", details, details_de, details_en)
try: carShare.run()
except IndexError:
    print("No locations found")

carPR = GenerateLayer(geojson_destDir, Herrenberg_bbox,  """nwr[amenity=parking]["park_ride"="yes"]({{bbox}}); """, "Park-Und-Ride", "Park and Ride", "carPRIcon", svgSourceDir+"parkandride.svg", details, details_de, details_en)
try: carPR.run()
except IndexError:
    print("No locations found")

taxi = GenerateLayer(geojson_destDir, Herrenberg_bbox, "nwr[amenity=taxi]({{bbox}});", "Taxi Standort", "Taxi stand", "taxiIcon", svgSourceDir+"taxi.svg", details, details_de, details_en)
try: taxi.run()
except IndexError:
    print("No locations found")