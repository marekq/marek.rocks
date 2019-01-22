#!/usr/bin/python
# marek kuczynski
# @marekq
# www.marek.rocks
# coding: utf-8

# set import path for python libraries to the './libs' folder.

import boto3, datetime, epsagon, os, time, sys
from boto3.dynamodb.conditions import Key, Attr
sys.path.insert(0, './libs')

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

# defines all blog categories from dynamodb which will be included on the page
blogs       = ['all', 'whats-new', 'newsblog', 'big-data', 'security', 'mobile', 'architecture', 'compute', 'database', 'management-tools', 'security-bulletins', 'public-sector', 'gamedev', 'ml', 'serverless'] # ['cli']
baseurl     = 'https://marek.rocks/'

# open a session with the dynamodb service
def get_dynamo_sess(): 
	d   = boto3.resource('dynamodb', region_name = os.environ['dynamo_region']).Table(os.environ['dynamo_post_table'])
	return d

d       = get_dynamo_sess()

# determine how old the aws blog post is  
def get_date(x):
	y		= time.time()
	z		= int(y) - int(x)
	
	weeks	= str(int(int(z)/604800))
	days	= str(int(int(z)/86400))
	hours	= str(int(int(z)/3600) % 24)
	mins 	= str(int(int(z)/60) % 3600)

	if days == str('0') and hours != str('0'):
		return hours+'h'

	elif days == str('0') and hours == str('0'):
		return mins+'m'
	
	elif int(days) < int('99'):
		return days+'d'

	else:
		return '99+d'

# get all the blog posts from dynamodb    
def get_posts(d, npa, tag, url):
	y   = ''
	h   = []
	
	# check if a url path was specified and return all articles. if no path was selected, return all articles. return the last 90 days of blogposts only.
	if npa == 'all' or npa == 'mini':
		e	= d.query(IndexName = 'allts', KeyConditionExpression = Key('allts').eq('y'))
		for x in e['Items']:
			h.append([x['timest'], x['title'], x['link'], x['desc'], x['source'], x['author'], x['tag']])

	# if a tag is specified in the get path, scan for it in the tag value
	elif npa == 'tag':
		e   = d.scan(FilterExpression = Attr('lower-tag').contains(tag.lower().replace('%20', ' ')))
		for x in e['Items']:
			h.append([x['timest'], x['title'], x['link'], x['desc'], x['source'], x['author'], x['tag']])

	# else resume the articles for the tag specified for the last 90 days
	else:
		# calculate the unix timestamp for 90 days ago
		n	= datetime.datetime.now()
		s	= n - datetime.timedelta(days = 90)
		ts	= int(time.mktime(s.timetuple()))
		
		e   = d.query(KeyConditionExpression = Key('source').eq(npa) & Key('timest').gt(str(ts)))
		for x in e['Items']:
			h.append([x['timest'], x['title'], x['link'], x['desc'], x['source'], x['author'], x['tag']])

	# print all the articles in html, shorten description text if needed
	if npa != 'mini':

		for x in sorted(h, reverse = True):
			desc    	= x[3]
			t           = get_date(x[0])
			y			+= '<tr><td width = 7%, valign = "top", align = "right"><font color = "#D3D3D3">'+t+'</font></td><td><button class="collapsible">'+x[1]+'</button><div class="content"><p>'+desc+'<br><br><a href="'+x[2].strip()+'">visit article here</a></p></div></td></tr>\n'

	else:
		ds	= ''
		for x in sorted(h, reverse = True):
			t           = get_date(x[0])
			if t != ds:
				ds		= t
				y		+= '<b>posted '+t+'</b>'
			y += x[4]+'<a href='+baseurl+x[2].strip()+' target="_blank">'+x[1][:70]+'</a><br>\n'

	return y

# generate highlighted url for aws blog links
def generate_urls(d, npa, url):
	h   = '<center>'
	
	for x in blogs:
		if x == npa:
			h += '<a href="'+url+str(x)+'"><font color = "red">'+x+'</font></a> &#8226; '
	
		else:
			h += '<a href="'+url+str(x)+'">'+x+'</a> &#8226; '
			
	return h+'<a href="#about">about this page</a></center>'

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

	elif x.strip('/') == 'mini':
		return 'mini', ''
	
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
	h	=  '<html><head><meta charset="UTF-8"><title>marek\'s serverless demo</title>'
	h	+= load_file('main.css')+'</head>'
	h	+= '<body><center><table width="800px"><tr><td><h1><center id = "top">Marek\'s Serverless AWS blog</center></h1></td></tr>'
	h	+= '<tr><td>'+generate_urls(d, npa, url)+'</td></tr></table><br>'
	h	+= '<table width = "800px"><tr><td>'
	h	+= get_posts(d, npa, tag, url)
	h	+= '</tr></td></table>'+load_file('collapse.js')+'</body></html>'
	return h

# return an html document when the lambda function is triggered
def handler(event, context):
	
	# get requestor http headers
	seg     = xray_recorder.begin_subsegment('dynamo-session')
	ip      = str(event['headers']['X-Forwarded-For']).split(',')[0]
	ua      = str(event['headers']['User-Agent'])

	# print request headers in cloudwatch for debug purposes
	#print('%%%', str(event['headers']))
	xray_recorder.end_subsegment()

	# clean the given url path and print debug
	xray_recorder.begin_subsegment('path-find')
	pa      = event['path']
	
	xray_recorder.current_subsegment().put_annotation('clientip', ip)
	xray_recorder.current_subsegment().put_annotation('useragent', ua)
	xray_recorder.current_subsegment().put_annotation('urlpath', pa)

	# check whether a tag, category, url or no path argument was given
	npa, tag = check_path(pa)
	#parse_debug(event)
	xray_recorder.end_subsegment()
	xray_recorder.begin_subsegment('html-parse')
	
	# if a url was submitted, redirect to it with a 301
	if npa == 'redir':
		print('301 ***', str(event['headers']['User-Agent']), str(event['headers']['Host']), pa, '', tag)
		xray_recorder.current_subsegment().put_annotation('statuscode', '301')

		return {'statusCode': '301',
				'headers': {'Location': tag}} 
	
	# else parse the html page
	else:
		url     = check_ua(ua)
		h       = parse_html(d, npa, tag, url)
	
		print('200 ***', str(event['headers']['User-Agent']), str(event['headers']['Host']), pa, url, tag)
		xray_recorder.current_subsegment().put_annotation('statuscode', '200')

		return {'statusCode': '200',
				'body': str(h),
				'headers': {'Content-Type': 'text/html', 'charset': 'utf-8'}} 

	xray_recorder.end_subsegment()
