#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Client facing flask application that receives search requests from the user and
 forwards the requests to the back-end server for processing. The results from
 the back-end are received and displayed on the browser.
"""


__author__ = "Anthony Sigogne"
__copyright__ = "Copyright 2017, Byprog"
__email__ = "anthony@byprog.com"
__license__ = "MIT"
__version__ = "1.0"

import os
import requests
from urllib import parse
from flask import Flask, request, jsonify, render_template

#Initialize flask app and load environment variables
app = Flask(__name__)
host = os.getenv("HOST")
port = os.getenv("PORT")


"""
End point for search requests. Receives search queries and forwards it to
back-end.
Method          : HTTP GET
Request Parameters : query - The search query
                     hits  - The number of results to be returned
                     start - Start number for the hits (for pagination purpose)
"""
@app.route("/", methods=['GET'])
def search():
   
    #Parse and analyze HTTP GET request.
    query = request.args.get("query", None)
    start = request.args.get("start", 0, type=int)
    hits = request.args.get("hits", 10, type=int)
    if start < 0 or hits < 0 :
        return "Error, start or hits cannot be negative numbers"

    #If valid query exists, create a request and forward to back-end server
    if query :
        try :
            r = requests.post('http://%s:%s/search'%(host, port), data = {
                'query':query,
                'hits':hits,
                'start':start
            })
        except :
            return "Error, check your installation"

        #Get response data and compute range of results pages
        data = r.json()
        i = int(start/hits)
        maxi = 1+int(data["total"]/hits)
        range_pages = range(i-5,i+5 if i+5 < maxi else maxi) if i >= 6 
        else range(0,maxi if maxi < 10 else 10)

        #Display the list of relevant results
        return render_template('spatial/index.html', query=query,
            response_time=r.elapsed.total_seconds(),
            total=data["total"],
            hits=hits,
            start=start,
            range_pages=range_pages,
            results=data["results"],
            page=i,
            maxpage=maxi-1)

    #Return to homepage (no query)
    return render_template('spatial/index.html')



#Jinja Custom filters for presentation#

@app.template_filter('truncate_title')
def truncate_title(title):
    """
    Truncate title to fit in result format.
    """
    return title if len(title) <= 70 else title[:70]+"..."

@app.template_filter('truncate_description')
def truncate_description(description):
    """
    Truncate description to fit in result format.
    """
    if len(description) <= 160 :
        return description

    cut_desc = ""
    character_counter = 0
    for i, letter in enumerate(description) :
        character_counter += 1
        if character_counter > 160 :
            if letter == ' ' :
                return cut_desc+"..."
            else :
                return cut_desc.rsplit(' ',1)[0]+"..."
        cut_desc += description[i]
    return cut_desc

@app.template_filter('truncate_url')
def truncate_url(url):
    """
    Truncate url to fit in result format.
    """
    url = parse.unquote(url)
    if len(url) <= 60 :
        return url
    url = url[:-1] if url.endswith("/") else url
    url = url.split("//",1)[1].split("/")
    url = "%s/.../%s"%(url[0],url[-1])
    return url[:60]+"..." if len(url) > 60 else url
