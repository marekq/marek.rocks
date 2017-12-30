#!/usr/bin/python
# marek kuczynski
# @marekq
# www.marek.rocks

<<<<<<< HEAD
import botocore.vendored.requests as requests, boto3, os, random, datetime, time

# get a random image back
def get_image():
    return '<img src="https://marek.rocks/images/'+str(random.randint(1,4))+'.jpg" width=100%>'
  
def get_date(x):
    y = time.time()
    z = int(y) - int(x)
    
    if z > 172800:
        return 'posted '+str(int(z)/86400)+' days'
    elif z > 86400:
	    return 'posted '+str(int(z)/86400)+' day'
    else:
	    return 'posted '+str(int(z)/3600)+' hours'
    
# get all the blog posts from dynamodb    
def get_dynamo():
    d   = boto3.resource('dynamodb', region_name = os.environ['dynamo_region']).Table(os.environ['dynamo_table'])
    h   = []
    
    for x in d.scan()['Items']:
        if x.has_key('desc'):
            h.append([x['timest'], x['title'], x['link'], x['desc']])
        else:
            h.append([x['timest'], x['title'], x['link'], 'no description found'])

    y   = ''
    for x in sorted(h, reverse = True):
        y += '<b><a href='+x[2]+'>'+x[1]+'</a></b><br><i>posted '+get_date(x[0])+' ago</i><br><br>'+x[3]+'<br><br>'

    return y
    
=======
import botocore.vendored.requests as requests, shutil, hashlib, os

# retrieve the ip address of the visitor and return lat/lon from freegeoip.net
def get_ip(event):
    ip  = str(event['headers']['X-Forwarded-For']).split(',')[0]
    a   = requests.get('https://freegeoip.net/csv/'+ip)
    b   = str(a.text).split(',')
    # switch around the lat and lon
    c   = b[9]+','+b[8]
    d   = plot_gps(c)
    return str(d)

>>>>>>> origin/master
# return a static blob of css
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

<<<<<<< HEAD
# parse the html file including the image
def parse_html():
    h = '<html><head><title>Marek Kuczy&#324;ski</title>'+css()+'</head>'
    h += '<body><center><h1><center>Marek Kuczy&#324;ski</h1>AWS solution architect<br><br>'
    h += '<a href="https://github.com/marekq/marek.rocks"><img style="position: absolute; top: 0; right: 0; border: 0;" src="https://camo.githubusercontent.com/38ef81f8aca64bb9a64448d0d70f1308ef5341ab/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f72696768745f6461726b626c75655f3132313632312e706e67" alt="Fork me on GitHub" data-canonical-src="https://s3.amazonaws.com/github/ribbons/forkme_right_darkblue_121621.png"></a>'
    #h += get_image()+'<br><br>'
    h += '<a target="_blank" href="https://github.com/marekq">github</a> | <a target="_blank" href="http://nl.linkedin.com/in/marekkuczynski">linkedin</a> | <a href="https://s3-eu-west-1.amazonaws.com/marek.rocks/papers.html">university papers</a> | <a target="_blank" href="http://twitter.com/marekq">twitter</a><br><br>'
    h += '<h3><a href="https://github.com/marekq/rss-lambda">AWS blog feeds</a></h3></center>'
    h += get_dynamo()
    h += '</body></html>'
=======
# create a map tile based on the visitor's gps coordinates. remember to set the lambda environment value 'tomtomkey' with a valid api key
def plot_gps(x):
    k   = os.environ['tomtomkey']
    u   = 'https://api.tomtom.com/map/1/staticimage?center='+str(x)+'&zoom=12&format=jpg&layer=basic&style=main&width=1280&height=250&view=Unified&key='+k

    # create an md5 hash of the url path, this is unique per gps coordinate
    f   = str(hashlib.md5(u).hexdigest())
    g   = '/tmp/'+f+'.jpg'

    # if there is no map tile on disk, download it from the tomtom api
    if not os.path.isfile(g):    
        r   = requests.get(u, stream = True)
        b   = 'file not found, downloaded'

        with open(g, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f) 
    else:
        b = 'file '+g+' found in lambda cache'

    # read the map tile and encode it as base64
    with open(g, 'rb') as x:                         
        data = x.read().encode("base64")

    # parse the html file including the image
    h = '<html><head><title>Marek Kuczy&#324;ski</title>'+css()+'</head>'
    h += '<body><center><h1><center>Marek Kuczy&#324;ski</h1>AWS solution architect<br><br>'
    h += '<img src="data:image/gif;base64,'+data+'"><br><br>'
    h += '<a target="_blank" href="https://github.com/marekq">github</a> | <a target="_blank" href="http://nl.linkedin.com/in/marekkuczynski">linkedin</a> | <a href="papers.html">university papers</a> | <a target="_blank" href="http://twitter.com/marekq">twitter</a>'
    h += '</center></body></html>'
>>>>>>> origin/master
    return h

# return an html document when the lambda function is triggered
def handler(event, context):
    return {'statusCode': 200,
<<<<<<< HEAD
            'body': parse_html(),
=======
            'body': get_ip(event),
>>>>>>> origin/master
            'headers': {'Content-Type': 'text/html'}}