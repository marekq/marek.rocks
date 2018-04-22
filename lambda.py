#!/usr/bin/python
# marek kuczynski
# @marekq
# www.marek.rocks
# coding: utf-8

import boto3, datetime, os, time
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
from boto3.dynamodb.conditions import Key, Attr
patch_all()

# defines all blog categories from dynamodb which will be included on the page
blogs       = ['all', 'whats-new', 'newsblog', 'devops', 'big-data', 'security', 'java', 'mobile', 'architecture', 'compute', 'database', 'management-tools', 'security-bulletins']
baseurl     = 'https://marek.rocks/'

# open a session with the dynamodb service
def get_dynamo_sess(): 
    d   = boto3.resource('dynamodb', region_name = os.environ['dynamo_region']).Table(os.environ['dynamo_post_table'])
    return d
        
# create a connection with DynamoDB which can persist as long as the lambda function is "warm"
d   = get_dynamo_sess()

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
def get_posts(d, npa, tag, url):
    y   = ''
    h   = []
    a   = []

    # check if a url path was specified and return all articles. if no path was selected, return all articles. return the last 30 days of blogposts only.
    if npa == 'all':
        e   = d.scan(ReturnConsumedCapacity = 'INDEXES', FilterExpression = Key('timest').gt(str(int(time.time()) - int(2592000))))

    # if a tag is specified in the get path, scan for it in the tag value
    elif npa == 'tag':
        e   = d.scan(ReturnConsumedCapacity = 'INDEXES', FilterExpression = Attr('lower-tag').contains(tag.lower().replace('%20', ' ')))

    # else resume the articles for the tag specified
    else:
        e   = d.query(ReturnConsumedCapacity = 'INDEXES', KeyConditionExpression = Key('source').eq(npa))
    
    c   = e['Count']
    s   = e['ResponseMetadata']['HTTPHeaders']['content-length']

    for x in e['Items']:
        if x.get('tag'):
            h.append([x['timest'], x['title'], x['link'], x['desc'], x['source'], x['author'], x['tag']])
        else:
            h.append([x['timest'], x['title'], x['link'], x['desc'], x['source'], x['author'], ''])

        a.append(str(x['timest']+','+x['source']))

    z   = '<center>'+str(c)+' articles found for '+npa+' <font color = "red">'+tag.replace('%20', ' ')+'</font> - '+s+' bytes (<a href="https://github.com/marekq/marek.rocks">source</a>)<br><br>'

    print('???', ','.join(a))

    # print all the articles in html, shorten description text if needed
    for x in sorted(h, reverse = True):
        if len(x[3]) > 750:
            desc    = x[3][:750]+' ...'
        else:
            desc    = x[3]
        
        t           = get_date(x[0])
        y += '<center><b><a href='+x[2]+' target="_blank">'+x[1]+'</a></b><br><i>posted '+t+' ago by '+x[5]+' in '+x[4]+' blog</i><br><br>'+desc+'<br><br><small><font color="#cccccc">'+get_links(x[6], tag.replace('%20', ' '), url)+'</font></small><br><br>'

    return z+y

# generate tag url links
def get_links(tags, tag, url):
    h = '<center>'
    for x in tags.split(','):
        ct = str(x).strip(' ').replace('%20', ' ')

        if tag.lower() == ct.lower():
            h += '<a href = "'+url+'tag/'+ct+'"><font color = "red">'+ct+'</font></a> &#8226; '
        else:
            h += '<a href = "'+url+'tag/'+ct+'">'+ct+'</a> &#8226; '
            
    return h[:-8]+'</center>'

# generate highlighted url for aws blog links
def generate_urls(d, npa, url):
    h   = '<center>'
    
    for x in blogs:
        if x == npa:
            h += '<a href="'+url+str(x)+'"><font color = "red">'+x+'</font></a> &#8226; '
    
        else:
            h += '<a href="'+url+str(x)+'">'+x+'</a> &#8226; '
            
    return h[:-8]+'</center><br>'

# print http headers for debug headers
def parse_debug(event):
    h   = str(event)
    print('%', h)

# rewrite the url path if needed. if no path was specified, return all articles
def check_path(x):
    if x.startswith('/http://') or x.startswith('/https://'):
        return 'redir', x[1:]

    if x.strip('/') in blogs:
        return x.strip('/'), ''
    
    elif x.strip('/')[:3] == 'tag':
        return 'tag', x.strip('/')[4:]
    
    else:
        return 'all', ''

# load the css file
def load_file(x):
    f   = open(x, 'r')
    x   = f.read()
    f.close()
    return x 

# check user agent
def check_ua(x):
    if x == 'Amazon CloudFront':
        b     = os.environ['baseurl']
        
    else:
        b     = os.environ['apigw']

    return b

# parse the html file including the image
def parse_html(d, npa, tag, url):
    h =  '<html><head><meta charset="UTF-8"><title>marek\'s serverless demo</title>'
    h += load_file('main.css')+'</head>'
    h += '<body><center><h1>Marek\'s Serverless AWS blog</h1>'
    h += load_file('search.js')
    h += '<center><table width="800px"><tr><td>'+generate_urls(d, npa, url)
    h += get_posts(d, npa, tag, url)
    h += '</td></tr></table></body></html>'
    return h

# return an html document when the lambda function is triggered
def handler(event, context):
    
    # get requestor http headers
    seg     = xray_recorder.begin_subsegment('dynamo-session')
    ip      = str(event['headers']['X-Forwarded-For']).split(',')[0]
    ua      = str(event['headers']['User-Agent'])

    # print request headers in cloudwatch for debug purposes
    print('%%%', str(event['headers']))
    xray_recorder.end_subsegment()

    # clean the given url path and print debug
    seg     = xray_recorder.begin_subsegment('path-find')
    pa      = event['path']
    
    seg.put_metadata('key', {ip}, 'IP')
    seg.put_metadata('key', {pa}, 'path')

    # check whether a tag, category, url or no path argument was given
    npa, tag = check_path(pa)
    parse_debug(event)
    xray_recorder.end_subsegment()

    seg     = xray_recorder.begin_subsegment('html-parse')
    
    # if a url was submitted, redirect to it with a 301
    if npa == 'redir':
        print('### 301 to '+tag)
        url     = 'h'
        return {'statusCode': '301',
                'headers': {'Location': tag}} 
    
    # else parse the html page
    else:
        url     = check_ua(ua)
        h       = parse_html(d, npa, tag, url)
    
        print('### 200 to '+tag)
        print('***', str(event['headers']['User-Agent']), str(event['headers']['Host']), pa, url)

        return {'statusCode': '200',
                'body': str(h),
                'headers': {'Content-Type': 'text/html', 'charset': 'utf-8'}} 

    xray_recorder.end_subsegment()
