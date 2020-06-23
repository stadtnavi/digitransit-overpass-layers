# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'

#%%
import json
import re
import overpass
from osmtogeojson import osmtogeojson

#%% [markdown]
# ### UpdateLayer class' functions
# * get data from Overpass-API
#     * change it into geojson format
# * add _name_ and _popupContent_ localized attributes for each feature
#     * _name_ attribute have also English and German versions
#     * _popupContent_ attribute have the values of prior _opening_hours_, _phone_ and _capacity_ attributes (if they were defined)
# * delete unnecessary attributes (also the above mentioned ones due to their copied values)
# * localize the _popupContent_ property's value: name of days are in German and in English too
# * each type of location has its own icon

#%% [markdown]
# #### String arrays
# The necessary_properties array includes the necessary properties which shouldn't be deleted. All fields excluded will be lost.
# New elements can be added. The order doesn't matter.
#
# The details array includes all the field names which we would like to display as description of the location. New
# fields can be added. The order of the elements will be the display order in the popup.
#
# Details_$locale includes the translations of the displayed fields. Important to have the same order as in the details array
# and every element has to have it's pair.

def _determine_feature_type(way):
    # get more advanced???
    if "center" in way:
        return "Point"
    elif way["nodes"][0] == way["nodes"][-1]:
        return "Polygon"
    else:
        return "LineString"

def _process_single_way(way_id, w, node_storage, nodes_used_in_ways):
    way = {}
    way["type"] = "Feature"
    wid = "way/{}".format(way_id)
    way["id"] = wid
    way["properties"] = w["tags"] if "tags" in w else {}
    way["properties"]["@id"] = wid  # the original osmtogeojson does this, so following suit
    way["geometry"] = {}

    geo_type = _determine_feature_type(w)
    way["geometry"]["type"] = geo_type

    if geo_type == "Point":
        way["geometry"]["coordinates"] = [w["center"]["lon"], w["center"]["lat"]]
        return way
    elif geo_type == "Polygon":
        way["geometry"]["coordinates"] = [[]]  # Polygons are list of list of lists...
        append_here = way["geometry"]["coordinates"][0]
    elif geo_type == "LineString":
        way["geometry"]["coordinates"] = []
        append_here = way["geometry"]["coordinates"]
     
    for n in w["nodes"]:
        node = node_storage[n]
        append_here.append([node["lon"], node["lat"]])
        nodes_used_in_ways[n] = 1

    return way

def _process_relations(resulting_geojson, relation_storage, way_storage, node_storage, nodes_used_in_ways):
    ways_used_in_relations = {}
    for rel_id in relation_storage:
        r = relation_storage[rel_id]
        rel = {}
        rel["type"] = "Feature"
        rid = "relation/{}".format(rel_id)
        rel["id"] = rid
        rel["properties"] = r["tags"] if "tags" in r else {}
        rel["properties"]["@id"] = rid
        rel["geometry"] = {}

        if "center" in r:
            rel["geometry"]["type"] = "Point"
            rel["geometry"]["coordinates"] = [r["center"]["lon"],r["center"]["lat"]]
        else:
            way_types = []
            way_coordinate_blocks = []
            only_way_members = True
            for mem in r["members"]:
                if mem["type"] == "way":
                    way_id = mem["ref"]
                    processed = _process_single_way(way_id, way_storage[way_id], node_storage, nodes_used_in_ways)
                    way_types.append(processed["geometry"]["type"])
                    way_coordinate_blocks.append(processed["geometry"]["coordinates"])
                    ways_used_in_relations[way_id] = 1
                else:
                    only_way_members = False

            
            if len([x for x in way_types if x == "Polygon"]) == len(way_types):
                # all polygons, the resulting relation geometry is polygon
                rel["geometry"]["type"] = "Polygon"
                rel["geometry"]["coordinates"] = [x[0] for x in way_coordinate_blocks]
            elif len([x for x in way_types if x == "LineString"]) == len(way_types):
                rel["geometry"]["type"] = "MultiLineString"
                rel["geometry"]["coordinates"] = [x for x in way_coordinate_blocks]
                merge.merge_line_string(rel)
            else:
                # relation does not consist of Polygons or LineStrings only... 
                # In this case, overpass reports every individual member with its relation reference
                # Another option would be to export such a relation as GeometryCollection
               
                rel["geometry"]["type"] = "GeometryCollection"
                member_geometries = []
                for mem in r["members"]:
                    if mem["type"] == "way":
                        way_id = mem["ref"]
                        processed = _process_single_way(way_id, way_storage[way_id], node_storage, nodes_used_in_ways)
                        member_geometries.append(processed["geometry"])
                    elif mem["type"] == "node":
                        node_id = mem["ref"]
                        node = node_storage[node_id]
                        geometry = {}
                        geometry["type"] = "Point"
                        geometry["coordinates"] = [node["lon"], node["lat"]]
                        member_geometries.append(geometry)
                        # Well, used_in_rels, but we want to ignore it as well, don't we?
                        nodes_used_in_ways[node_id] = 1
                    else:
                        logger.warn("Relations members not yet handled (%s)", rel_id)
                    
                rel["geometry"]["geometries"] = member_geometries
            
        resulting_geojson["features"].append(rel)
    return ways_used_in_relations
osmtogeojson._process_single_way = _process_single_way
osmtogeojson._process_relations = _process_relations


#%%
class GenerateLayer:
    def __init__(self, dest_dir, bbox, details, details_de, details_en):
        self.necessary_properties = ['name', 'name_en', 'name_de', 'address', 'popupContent', 'popupContent_de', 'popupContent_en', 'icon', 'city']
        self.details = details
        self.details_de = details_de
        self.details_en = details_en
        self.dest_dir = dest_dir
        self.bbox = bbox
        
        self.api = overpass.API(timeout=600)
        
    def run(self, query, name_de, name_en, iconId, iconSourceFile):
        default_name = name_de
        layerName = name_en.replace(" ", "").replace("/", "").lower()
        filePath = self.dest_dir + layerName + '.geojson'
        iconSource = self.read_svg_source(iconSourceFile)
        
        bbQuery = self._prepare_overpass_query(query, self.bbox)
        print(bbQuery)

        response = self.api.get(bbQuery, 'geojson', build=False)
        #print(response)

        data = osmtogeojson.process_osm_json(response)
        #self.write_geojson_file(geojson_response, filePath)
        
        #data = self._load_json_file(filePath)
        self.add_properties(data, default_name, name_de, name_en)
        self.localize_description(data)
        self.set_default_description(data)
        self.add_icon(data, iconId, iconSource)
        self.delete_unnecessary_properties(data, self.necessary_properties)
        self._write_geojson_file(data, filePath)

    def merge_layers(self, dir, layer_file_names, dest_file_name):
        merged_json = None
    
        for file_name in layer_file_names:
            layer = self._load_json_file(dir + file_name)
            if not merged_json:
                merged_json = layer
            else:
                merged_json['features'] += layer['features']

        self._write_geojson_file(merged_json, dir+dest_file_name)

    def _prepare_overpass_query(self, overpass_query, bbox):
        return "[out:json];" + overpass_query.replace('{{bbox}}', bbox) + " out center;"
    
    def _write_geojson_file(self, data, fileName):
         with open(fileName, "w") as file:
            json.dump(data, file, indent=2)
    
    def _load_json_file(self, fileName):
        with open(fileName) as file:
            data = json.load(file)
        return data
    
    def add_properties(self, data, default_name, name_de, name_en):
        for feat in data['features']:
            # set the name properties (localized)
            # If the location has it's own name, all localized versions get the original value.
            if not 'name_en' in feat['properties'] and 'name' in feat['properties']:
                feat['properties']['name_en'] = feat['properties']['name']
            else:
                feat['properties']['name_en'] = name_en
            if not 'name_de' in feat['properties'] and 'name' in feat['properties']:
                feat['properties']['name_de'] = feat['properties']['name']
            else:
                feat['properties']['name_de'] = name_de
            if not 'name' in feat['properties']:
                feat['properties']['name'] = default_name
            # create the popupContent properties
            feat['properties']['popupContent'] = []
            feat['properties']['popupContent_de'] = []
            feat['properties']['popupContent_en'] = []
            # modifying name for 'Nette Toilette' nodes
            if feat['properties']['toilets:scheme'] == 'Nette Toilette':
                feat['properties']['name'] = 'Nette Toilette ' + '"' + feat['properties']['name'] + '"'
                feat['properties']['name_en'] = 'Public toilet ' + '"' + feat['properties']['name_en'] + '"'
                feat['properties']['name_de'] = 'Nette Toilette ' + '"' + feat['properties']['name_de'] + '"'
            # add the listed (in details array) properties to the popupContent property (these will be displayed)
            for key in feat['properties']:
                if key in self.details:
                    feat['properties']['popupContent_de'].append(key+': ' + feat['properties'][key] + ', ')
                    feat['properties']['popupContent_en'].append(key+': ' + feat['properties'][key] + ', ')

    def localize_description(self, data):
        for feat in data['features']:
            if 'popupContent_de' in feat['properties']:
                # Tu -> Di, We -> Mi, Th -> Do, Su -> So, yes -> ja, no -> nein
                desc = ''.join(feat['properties']['popupContent_de'])
                desc = re.sub(r"\bTu\b", "Di", desc)
                desc = re.sub(r"\bWe\b", "Mi", desc)
                desc = re.sub(r"\bTh\b", "Do", desc)
                desc = re.sub(r"\bSu\b", "So", desc)
                # yes -> ja, no -> nein
                desc = re.sub(r"\byes\b", "ja", desc)
                desc = re.sub(r"\bno\b", "nein", desc)
                # limited -> begrenzt
                desc = desc.replace("limited", "begrenzt")
                # At opening hours PH off won't be displayed.
                desc = desc.replace(" PH off, ", "")
                # Translate as declared in the details_$locale array.
                j = 0
                while j < len(self.details):
                    desc = desc.replace(self.details[j], self.details_de[j])
                    j += 1
                if "Webseite" in desc:
                    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\)]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', desc)
                    url = ''.join(url)
                    url = url.rstrip(',')
                    desc = desc.replace("Webseite:", "<a href=\""+url+"\" target=\"_blank\">Webseite</a>,")
                    desc = desc.replace(url+",", "")
                # Strip the end
                desc = desc.rstrip(' ').rstrip(',')
                # Rewrite the popupContent field.
                feat['properties']['popupContent_de'] = desc
            if 'popupContent_en' in feat['properties']:
                desc = ''.join(feat['properties']['popupContent_en'])
                # At opening hours PH off won't be displayed.
                desc = desc.replace(" PH off, ", "")
                # Translate as declared in the details_$locale array.
                j = 0
                while j < len(self.details):
                   desc = desc.replace(self.details[j], self.details_en[j])
                   j += 1
                if "Website" in desc:
                    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\)]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', desc)
                    url = ''.join(url)
                    url = url.rstrip(',')
                    desc = desc.replace("Website:", "<a href=\""+url+"\" target=\"_blank\">Website</a>,")
                    desc = desc.replace(url+",", "")
                # Strip the end
                desc = desc.rstrip(' ').rstrip(',')
                # Rewrite the popupContent field.
                feat['properties']['popupContent_en'] = desc

    def set_default_description(self, data):
    # Set the default description as one of the listed locales.
        for feat in data['features']:
            feat['properties']['popupContent'] = feat['properties']['popupContent_de']

    def read_svg_source(self, iconSourceFile):
        with open(iconSourceFile, 'r') as file:
            iconSource = file.read().replace('\n', '')
        return iconSource

    def add_icon(self, data, iconId, iconSource):
        # In the same type of feature the icon is the same. The icon.id has to be set for every feature.
        for feat in data['features']:
            if not 'icon' in feat['properties']:
                feat['properties']['icon'] = {}
            if not 'id' in feat['properties']['icon']:
                feat['properties']['icon']['id'] = iconId

        # Only the very first feature has to have the SVG source of the icon.
        if len(data['features']) > 0:
            data['features'][0]['properties']['icon']['svg'] = iconSource
    
    def delete_unnecessary_properties(self, data, necessary_properties):
        if 'generator' in data:
            del data['generator']
        for feat in data['features']:
            if 'generator' in feat:
                del feat['generator']
            if 'id' in feat:
                del feat['id']
            for key in list(feat['properties']):
                if not key in self.necessary_properties:
                    del feat['properties'][key]
