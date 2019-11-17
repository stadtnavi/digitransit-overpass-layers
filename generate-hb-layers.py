#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from geojson_modifier import *
import os

bbox = os.getenv('ENV_BBOX', "48.51592209023528,8.533287048339844,48.72607645125842,9.036598205566406")
svgSourceDir = os.getenv('ENV_ICONSRC', "./layer-icons/")

geojson_destDir = os.getenv('ENV_DDIR', "../digitransit-ui/static/assets/geojson/hb-layers/")
details = ["capacity", "opening_hours", "contact:phone", "phone", "wheelchair", "fee", "contact:website", "website"]
details_de = ["Stellplätze", "Öffnungszeiten", "Telefon", "Telefon", "Barrierefrei", "Gebührenpflichtig:", "Webseite", "Webseite"]
details_en = ["Capacity", "Opening hours", "Phone", "Phone", "Wheelchair", "Fee", "Website", "Website"]

layerGenerator = GenerateLayer(geojson_destDir, bbox, details, details_de, details_en)

layerGenerator.run("nwr[amenity=bicycle_parking][covered=no]({{bbox}});", "Fahrradstellplatz", "Open-air bike park", "bikeParkOpIcon", svgSourceDir+"openedbikepark.svg")
layerGenerator.run("nwr[amenity=bicycle_parking][covered=yes]({{bbox}});", "Überdachter Fahrradstellplatz", "Covered bike park", "bikeParkCovIcon", svgSourceDir+"coveredbikepark2.svg")
layerGenerator.merge_layers(geojson_destDir, ["coveredbikepark.geojson","open-airbikepark.geojson"], "bicycle-parking.geojson")

layerGenerator.run("""nwr["man_made"="monitoring_station"]["monitoring:bicycle"="yes"]({{bbox}});""", "Fahrradzählstelle", "Bicycle monitoring station", "layerGeneratorIcon", svgSourceDir+"bikemonitoring.svg")
layerGenerator.run("nwr[amenity=bicycle_repair_station]({{bbox}});", "Fahrradreparaturstation", "Bicycle repair station", "bikeRepIcon", svgSourceDir+"bikerepair.svg")
layerGenerator.run("nwr[shop=bicycle]({{bbox}});", "Fahrradgeschäft", "Bicycle shop", "bikeShopIcon", svgSourceDir+"bikeshop2.svg")
layerGenerator.merge_layers(geojson_destDir, ["bicyclemonitoringstation.geojson","bicyclerepairstation.geojson","bicycleshop.geojson"], "bicycleinfrastructure.geojson")

layerGenerator.run("nwr[amenity=charging_station][bicycle=yes]({{bbox}});", "Fahrradladestation", "Bicycle charging station", "bikeChargeIcon", svgSourceDir+"bikecharge.svg")
layerGenerator.run("nwr[amenity=charging_station][car=yes]({{bbox}});", "Elektroauto-Ladestation", "Car charging station", "carChargeIcon", svgSourceDir+"carcharge.svg")
layerGenerator.merge_layers(geojson_destDir, ["bicyclechargingstation.geojson","carchargingstation.geojson"], "charging.geojson")

layerGenerator.run("""(nwr[amenity=parking]["access"!="private"]["access"!="customers"]({{bbox}});)->.parkings;nwr.parkings(if: (is_number(t["capacity"]) && t["capacity"]>10));""", "Parkplatz", "Car parking", "carParkOpIcon", svgSourceDir+"openedcarpark.svg")
layerGenerator.run("""nwr[amenity=parking]["access"!="private"]["access"!="customers"]["parking"!="surface"]({{bbox}}); """, "Parkhaus/Tiefgarage", "Multi-storey/underground car parking", "carParkCovIcon", svgSourceDir+"coveredcarpark.svg")
layerGenerator.run("""nwr[amenity=parking]["park_ride"="yes"]({{bbox}}); """, "Park-Und-Ride", "Park and Ride", "carPRIcon", svgSourceDir+"parkandride.svg")
layerGenerator.merge_layers(geojson_destDir, ["carparking.geojson","parkandride.geojson","multi-storeyundergroundcarparking.geojson"], "car-parking.geojson")

layerGenerator.run("nwr[amenity=taxi]({{bbox}});", "Taxi-Stellplatz", "Taxi stand", "taxiIcon", svgSourceDir+"taxi.svg")
layerGenerator.run("nwr[amenity=car_sharing]({{bbox}});", "Car-Sharing", "Car sharing", "carShareIcon", svgSourceDir+"carshare.svg")
layerGenerator.run("nwr[amenity=bicycle_rental]({{bbox}});", "Fahrradverleih", "Bike rental", "bikeRentIcon", svgSourceDir+"bikerent.svg")
layerGenerator.merge_layers(geojson_destDir, ["taxistand.geojson","carsharing.geojson","bikerental.geojson"], "taxi-and-sharing.geojson")
