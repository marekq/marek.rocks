#!/usr/bin/python
# marek kuczynski
# @marekq
# www.marek.rocks

import boto3, datetime, os, time 
from boto3.dynamodb.conditions import Key, Attr

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
patch_all()

# defines all blog categories from dynamodb which will be included on the page
blogs = ['all', 'whats-new', 'newsblog', 'devops', 'big-data', 'security', 'java', 'mobile', 'architecture', 'compute', 'database', 'management-tools', 'security-bulletins']

# open a session with the dynamodb service
def get_dynamo_sess(): 
    d   = boto3.resource('dynamodb', region_name = os.environ['dynamo_region'])
    return d
        
# determine how old the aws blog post is  
def get_date(x):
    y = time.time()
    z = int(y) - int(x)
    
    if z > 172800:
        return str(int(int(z)/86400))+' days'
    elif z > 86400:
        return str(int(int(z)/86400))+' day'
    elif z > 7200:
        return str(int(int(z)/3600))+' hours'
    elif z > 3600:
        return str(int(int(z)/3600))+' hour'
    else:
        return str(int(int(z)/60))+' minutes'

# get all the blog posts from dynamodb    
def get_posts(d, npa):
    d   = d.Table(os.environ['dynamo_post_table'])
    y   = ''
    h   = []

    # check if a url path was specified and return all articles. if no path was selected, return all articles
    if npa == 'all':
        e   = d.scan(ReturnConsumedCapacity = 'INDEXES')
        c   = e['Count']
        s   = e['ResponseMetadata']['HTTPHeaders']['content-length']

        for x in e['Items']:
            h.append([x['timest'], x['title'], x['link'], x['desc'], x['source'], x['author']])
            
    else:
        e   = d.query(KeyConditionExpression=Key('source').eq(npa), ReturnConsumedCapacity = 'INDEXES')
        c   = e['Count']
        s   = e['ResponseMetadata']['HTTPHeaders']['content-length']

        for x in e['Items']:
            h.append([x['timest'], x['title'], x['link'], x['desc'], x['source'], x['author']])

    z       = '<center>'+str(c)+' articles found for '+npa+' - '+s+' bytes (<a href="https://github.com/marekq/marek.rocks">source</a>)<br><br>'

    # print all the articles in html, shorten description text if needed
    for x in sorted(h, reverse = True):
        if len(x[3]) > 500:
            desc    = x[3][:500]+' ...'
        else:
            desc    = x[3]
        
        t           = get_date(x[0])    
        y += '<b><a href='+x[2]+' target="_blank">'+x[1]+'</a></b><br><center><i>posted '+t+' ago by '+x[5]+' in '+x[4]+' blog</i></center><br>'+desc+'<br><br>'

    return z+y

# generate highlighted url for aws blog links
def generate_urls(d, npa):
    h   = '<center>'
    
    for x in blogs:
        if x == npa:
            h += '<a href="https://marek.rocks/'+x+'"><font color = "red">'+x+'</font></a> &#8226; '
    
        else:
            h += '<a href="https://marek.rocks/'+str(x)+'">'+x+'</a> &#8226; '
            
    return h[:-8]+'</center><br><br>'

# print http headers for debug headers
def parse_debug(event):
    h   = str(event)
    print('%', h)

# rewrite the url path if needed. if no path was specified, return all articles
def check_path(x):
    y   = x.strip('/')
    
    if y in blogs:
        return y
    else:
        return 'all'

# load the css file
def load_css():
    f   = open('main.css', 'r')
    x   = f.read()
    f.close()
    return x 
	
# parse the html file including the image
def parse_html(d, npa):
    h =  '<html><head><title>AWS RSS blog feed</title>'
    h += load_css()+'</head>'
    h += '<body><center><center><h1>Marek\'s AWS blog feed</h1></center>'
    h += '<table width="800px"><tr><td>'+generate_urls(d, npa)
    h += get_posts(d, npa)
    h += '</td></tr></table></body></html>'
    return h

# return an html document when the lambda function is triggered
def handler(event, context):
    # create a session with dynamodb and get requestor http headers
    seg     = xray_recorder.begin_subsegment('dynamo-session')
    d       = get_dynamo_sess()
    ip      = str(event['headers']['X-Forwarded-For']).split(',')[0]
    co      = str(event['headers']['CloudFront-Viewer-Country'])
    ua      = str(event['headers']['User-Agent'])
    xray_recorder.end_subsegment()

    # clean the given url path and print debug
    seg     = xray_recorder.begin_subsegment('path-find')
    pa      = event['path']
    seg.put_metadata('key', {ip}, 'IP')
    seg.put_metadata('key', {pa}, 'path')
    seg.put_metadata('key', {co}, 'country')
    
    npa     = check_path(pa)
    parse_debug(event)
    xray_recorder.end_subsegment()

    # parse the html output for the client
    seg     = xray_recorder.begin_subsegment('html-parse')
    h       = parse_html(d, npa)
    xray_recorder.end_subsegment()

    # return the html code to api gateway
    return {'statusCode': 200,
            'body': h,
            'headers': {'Content-Type': 'text/html'}}
