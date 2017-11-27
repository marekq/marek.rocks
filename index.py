#!/usr/bin/python
# marek kuczynski
# @marekq
# www.marek.rocks

import random

def html():
    i    = str(random.randint(1,2))
    h    = """<html><head><title>Marek Kuczy&#324;ski</title>
    
    <style type="text/css">
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
    </style>
    
    </head><body><center><h1><center>Marek Kuczy&#324;ski</h1>AWS solution architect<br><br>
    <img src="https://www.marek.rocks/images/"""+i+""".jpg" width=100%><br><br>
    <a target="_blank" href="https://github.com/marekq">github</a> | <a target="_blank" href="http://nl.linkedin.com/in/marekkuczynski">linkedin</a> | <a href="papers.html">university papers</a> | <a target="_blank" href="http://twitter.com/marekq">twitter</a><br><br></center>
    </body></html>"""
    return h

def handler(event, context):
    return {'statusCode': 200,
            'body': html(),
            'headers': {'Content-Type': 'text/html'}}