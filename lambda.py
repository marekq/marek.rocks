#!/usr/bin/python
# marek kuczynski
# @marekq
# www.marek.rocks

import botocore.vendored.requests as requests, boto3, datetime, os, random, time
from boto3.dynamodb.conditions import Key, Attr

# get a random image back
def get_image():
    return '<img src="https://s3-'+os.environ['s3_region']+'.amazonaws.com/'+os.environ['s3_bucket']+'/images/'+str(random.randint(1,4))+'.jpg" width=100%>'
  
# open a session with the dynamodb service
def get_dynamo_sess(): 
    d   = boto3.resource('dynamodb', region_name = os.environ['dynamo_region'])
    return d
  
# determine how old the aws blog post is  
def get_date(x):
    y = time.time()
    z = int(y) - int(x)
    
    if z > 172800:
        return str(int(z)/86400)+' days'
    elif z > 86400:
        return str(int(z)/86400)+' day'
    else:
        return str(int(z)/3600)+' hours'
    
# get all the blog posts from dynamodb    
def get_posts(d, npa):
    d   = d.Table(os.environ['dynamo_post_table'])
    y   = ''
    h   = []

    if npa == 'all':
        for x in d.scan()['Items']:
            h.append([x['timest'], x['title'], x['link'], x['desc'], x['source']])
            
    else:
        for x in d.query(KeyConditionExpression=Key('source').eq(npa))['Items']:
            h.append([x['timest'], x['title'], x['link'], x['desc'], x['source']])

    for x in sorted(h, reverse = True):
        y += '<b><a href='+x[2]+' target="_blank">'+x[1]+'</a></b><br><i>posted '+get_date(x[0])+' ago in '+x[4]+'</i><br><br>'+x[3]+'<br><br><br>'

    return y

# write details about the web visitor to dynamodb
def write_dynamo(d, ip, co, ua, pa, npa):
    d   = d.Table(os.environ['dynamo_user_table'])
    d.put_item(Item = {
        'date' : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
		'timest' : str(int(time.time())),
		'ip' : ip,
		'usera' : ua,
		'country' : co,
		'user-path' : pa,
		'new-path' : npa
	})

# generate highlighted url for aws blog links
def generate_urls(npa):
    h   = 'AWS blog feeds ( '

    for x in ['all', 'whats-new', 'newsblog']:
        h += '<a href="https://marek.rocks/'+x+'">'+x+'</a> '
            
    return h+' )<br><br>'

# print http headers for debug headers
def parse_debug(event):
    h = str(event)
    return h

# rewrite the url path if needed
def check_path(x):
    if x.strip('/') == 'whats-new':
        return 'whats-new'
    elif x.strip('/') == 'newsblog':
        return 'newsblog'
    else:
        return 'all'

# parse the html file including the image
def parse_html(d, npa):
    h = '<html><head><title>Marek Kuczy&#324;ski</title><link rel="stylesheet" type="text/css" href="https://s3-'+os.environ['s3_region']+'.amazonaws.com/'+os.environ['s3_bucket']+'/main.css"></script></head>'
    h += '<body><center><h1><center>Marek Kuczy&#324;ski</h1>'
    h += get_image()+'<br><br>'
    h += '<a target="_blank" href="https://github.com/marekq">github</a> | '
    h += '<a target="_blank" href="http://nl.linkedin.com/in/marekkuczynski">linkedin</a> | '
    h += '<a href="https://s3-'+os.environ['s3_region']+'.amazonaws.com/'+os.environ['s3_bucket']+'/papers.html">university papers</a> | '
    h += '<a target="_blank" href="http://twitter.com/marekq">twitter</a><br><br>- - -<br><br>'
    h += generate_urls(npa)
    h += '<table width="800px"><tr><td>'+get_posts(d, npa)
    h += '</td></tr></table></center></body></html>'
    return h

# return an html document when the lambda function is triggered
def handler(event, context):
    d   = get_dynamo_sess()
    ip  = str(event['headers']['X-Forwarded-For']).split(',')[0]
    co  = str(event['headers']['CloudFront-Viewer-Country'])
    ua  = str(event['headers']['User-Agent'])

    pa  = event['path']
    npa = check_path(pa)

    write_dynamo(d, ip, co, ua, pa, npa)

    return {'statusCode': 200,
            'body': parse_html(d, npa),
            'headers': {'Content-Type': 'text/html'}}
