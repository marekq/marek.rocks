#!/usr/bin/python
# marek kuczynski
# @marekq
# www.marek.rocks

import botocore.vendored.requests as requests, boto3, datetime, os, random, time

# get a random image back
def get_image():
    return '<img src="https://s3-'+os.environ['s3_region']+'.amazonaws.com/'+os.environ['s3_bucket']+'/images/'+str(random.randint(1,4))+'.jpg" width=100%>'
  
def get_dynamo_sess(): 
    d   = boto3.resource('dynamodb', region_name = os.environ['dynamo_region'])
    return d
  
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
def get_posts():
    h   = []
    d   = get_dynamo_sess().Table(os.environ['dynamo_post_table'])
    for x in d.scan()['Items']:
        if x.has_key('desc'):
            h.append([x['timest'], x['title'], x['link'], x['desc']])
        else:
            h.append([x['timest'], x['title'], x['link'], 'no description found'])

    y   = ''
    for x in sorted(h, reverse = True):
        y += '<b><a href='+x[2]+' target="_blank">'+x[1]+'</a></b> - <i>posted '+get_date(x[0])+' ago</i><br><br>'+x[3]+'<br><br><br>'

    return y

def write_dynamo(ip, co, ua):
    d   = get_dynamo_sess().Table(os.environ['dynamo_user_table'])
    d.put_item(Item = {
        'date' : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
        'timest' : str(int(time.time())),
        'ip' : ip,
        'usera' : ua,
        'country' : co
    })
    
# parse the html file including the image
def parse_html():
    h = '<html><head><title>Marek Kuczy&#324;ski</title><link rel="stylesheet" type="text/css" href="https://s3-'+os.environ['s3_region']+'.amazonaws.com/'+os.environ['s3_bucket']+'/main.css"></script></head>'
    h += '<body><center><h1><center>Marek Kuczy&#324;ski</h1>'
    h += get_image()+'<br><br>'
    h += '<a target="_blank" href="https://github.com/marekq">github</a> | '
    h += '<a target="_blank" href="http://nl.linkedin.com/in/marekkuczynski">linkedin</a> | '
    h += '<a href="https://s3-'+os.environ['s3_region']+'.amazonaws.com/'+os.environ['s3_bucket']+'/papers.html">university papers</a> | '
    h += '<a target="_blank" href="http://twitter.com/marekq">twitter</a><br><br>'
    h += '<h3>AWS blog feeds</h3><table width="800px"><tr><td>'
    h += get_posts()
    h += '</td></tr></table></center></body></html>'
    return h

# return an html document when the lambda function is triggered
def handler(event, context):
    ip = str(event['headers']['X-Forwarded-For']).split(',')[0]
    co = str(event['headers']['CloudFront-Viewer-Country'])
    ua = str(event['headers']['User-Agent'])
    write_dynamo(ip, co, ua)

    return {'statusCode': 200,
            'body': parse_html(),
            'headers': {'Content-Type': 'text/html'}}