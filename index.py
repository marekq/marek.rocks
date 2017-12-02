#!/usr/bin/python
# marek kuczynski
# @marekq
# www.marek.rocks

import botocore.vendored.requests as requests, shutil, hashlib, os

# retrieve the ip address of the visitor and return lat/lon 
def get_ip(event):
    ip  = str(event['headers']['X-Forwarded-For']).split(',')[0]
    a   = requests.get('https://freegeoip.net/csv/'+ip)
    b   = str(a.text).split(',')
    c   = b[9]+','+b[8]
    d   = plot_gps(c)
    return str(d)

def css():
    return """<style type="text/css">
    body {
        height: 50%;
        background: #fff;
        margin-top: 50px;
        margin-bottom: 50px;
        padding: 0;
        font-family: Courier New, Fixed;
        font-size: 15px;
        color: #555;
    }
    </style>"""

# create a 
def plot_gps(x):
    k   = os.environ['tomtomkey']
    u   = 'https://api.tomtom.com/map/1/staticimage?center='+str(x)+'&zoom=12&format=jpg&layer=basic&style=main&width=1280&height=250&view=Unified&key='+k
    f   = str(hashlib.md5(u).hexdigest())
    g   = '/tmp/'+f+'.jpg'

    if not os.path.isfile(g):    
        r   = requests.get(u, stream = True)
        b   = 'file not found, downloaded'

        #if r.status_code == 200:
        with open(g, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f) 
    else:
        b = 'file '+g+' found in lambda cache'

    with open(g, 'rb') as x:                         
        data = x.read().encode("base64")

    h = '<html><head><title>Marek Kuczy&#324;ski</title>'+css()+'</head>'
    h += '<body><center><h1><center>Marek Kuczy&#324;ski</h1>AWS solution architect<br><br>'
    h += '<img src="data:image/gif;base64,'+data+'"><br><br>'
    h += '<a target="_blank" href="https://github.com/marekq">github</a> | <a target="_blank" href="http://nl.linkedin.com/in/marekkuczynski">linkedin</a> | <a href="papers.html">university papers</a> | <a target="_blank" href="http://twitter.com/marekq">twitter</a>'
    h += '</center></body></html>'
    return h



def handler(event, context):
    return {'statusCode': 200,
            'body': get_ip(event),
            'headers': {'Content-Type': 'text/html'}}