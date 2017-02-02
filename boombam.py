import numpy as np
import bottle
from bottle import route, run, template, response, static_file, redirect
import json
from pointdata import *
bottle.debug(True)

def in_bounds(bounds,point):
    north = bounds['_northEast']['lat']
    east = bounds['_northEast']['lng']
    south = bounds['_southWest']['lat']
    west = bounds['_southWest']['lng']
    lon = point['geometry']['coordinates'][0]
    lat = point['geometry']['coordinates'][1]
    in_bounds = np.logical_and(np.logical_and(
                               lon >= west,   # filter the latitude
                               lon <= east),  # that are within the boundaries
                            np.logical_and(
                               lat <= north,  # filter the longititude
                               lat >= south)) # that are within the boundaries
   
    return in_bounds

if __name__ == '__main__':
    @route('/')
    def index():
        return '<h1 style="font-size: 40em; text-align:center">@</h1>'
        
    @route('/mapmap')
    @route('/mapmap/')
    def mymap():
        return '''
        <body>
        <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.0.2/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.0.2/dist/leaflet.js"></script>
        </head>
        <div id="mapmap" style="height: 400px; top: 0px; left:0px; right:0px"></div>
        <div id="counter">0</div>
        </body>
        <script>
        var map = L.map('mapmap', {center: [17.95, -76.75],zoom: 8});
        var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
        osm.addTo(map);
        window.gg = new L.GeoJSON();
        window.gg.addTo(map);
        map.on('moveend', function(){
        console.log(JSON.stringify(map.getBounds()))
        if (map.getZoom() < 14) {
            console.log('zoom in more');
            window.gg.clearLayers();
        } else {
            console.log('great');
            window.gg.clearLayers();
            var req = new XMLHttpRequest();
            req.onload = function() {
                feat = JSON.parse(req.responseText);
                var cn = document.getElementById("counter");
                console.log(feat.length)
                window.gg.addData(feat);
                console.log('XHR Finished');
            }
            
            req.open("GET", 'data/' + JSON.stringify(map.getBounds()), true);
            req.send();
        }   
        })
        </script>
        '''
    
    @route('/data')    
    @route('/data/')    
    def mydata():
        return json.dumps(point_list)
    
    @route('/data/<bounds>')    
    def bounded(bounds):
        bd = json.loads(bounds)
        ret = []
        for i in point_list:
            if in_bounds(bd,i):
                ret.append(i)
        print len(ret)
        return json.dumps(ret)
        
    run(host='0.0.0.0', port=8080)