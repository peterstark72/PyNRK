#!/usr/bin/env python
# encoding: utf-8
"""
NRK XML API Python module
av Peter Stark <peterstark72@gmail.com>

Dokumentation finns här:
http://om.yr.no/verdata/xml/spesifikasjon/




Copyright (c) 2012, Peter Stark 
All rights reserved.

Unless otherwise specified, redistribution and use of this software in
source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * The name of the author nor the names of any contributors may be
      used to endorse or promote products derived from this software without
      specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import pprint

import sys
import os
import datetime
import string

import urllib2
import xml.etree.ElementTree
import StringIO


API_SERVER = u"http://www.yr.no"
API_XML_TEMPLATE = string.Template(
	'${server}/place/${country}/${area}/${city}/forecast.xml')


string = lambda s : s
date = lambda d : datetime.datetime.strptime(d,'%Y-%m-%dT%H:%M:%S')
timeoffset = lambda t: datetime.timedelta(minutes=int(t))


TIMEZONE = 'timezone', {
	'@id' : string,
	'@utcoffsetMinutes' : timeoffset	
}

LOCATION2 = 'location', {
	'@altitude' : float,
	'@latitude' : float,		
	'@longitude' : float,	
	'@geobase' : string,
	'@geobaseid' : int		
}


LOCATION = 'location', {
		'name' : string,
		'type' : string,
		'country' : string,
		'timezone' : TIMEZONE,
		'location' : LOCATION2
}

LINK = 'link', {
	'@text' : string,
	'@url' : string
}

CREDIT = 'credit', {
	'link' : LINK
}


SUN = 'sun', {
	'@rise' : date,
	'@set' : date
}

SYMBOL = 'symbol' , {
	'@number' : int,
	'@name' : string,
	'@var' : string}


PRECIPITATION = 'precipitation', {
	'@value' : float,
	'@minvalue' : float,
	'@maxvalue' : float
}

TEMPERATURE = 'temperature', {
	'@unit' : string,
	'@value' : float
}

PRESSURE = 'pressure', {
	'@unit' : string,
	'@value' : float
}

WINDSPEED = 'windSpeed', {
	'@mps' : float,
	'@name' : string
}

WINDDIRECTION = 'windDirection', {
	'@deg' : float,
	'@code' : string,
	'@name' : string
}

TIME = 'forecast/tabular/time', {
	'@from' : date,
	'@to' : date,
	'@period' : int,
	'symbol' : SYMBOL,
	'precipitation' : PRECIPITATION,
	'temperature' : TEMPERATURE,
	'pressure' : PRESSURE,
	'windSpeed' : WINDSPEED,
	'windDirection' : WINDDIRECTION,	
}

WEATHER_DATA = {
	'location' : LOCATION,
	'credit' : CREDIT,
	'sun' : SUN,
	'forecast' : TIME
}


class NRKException( Exception ):
    pass



class NRK(object):
	
	def __init__(self):
		
		self.api_server  = API_SERVER
		self.url_template = API_XML_TEMPLATE
		

	def convert_element(self, node, conversions):	

		e_data = {}

		for name, conversion in conversions.items():
			key_name = ""
			value = ""
			if name.startswith("@"):
				attrib_name = name[1:]
				key_name = attrib_name
				if attrib_name in node.attrib:
					e_data[key_name] = conversion(node.attrib[attrib_name])
			else:
				key_name = name
				if isinstance(conversion, tuple):
					value = self.build_element(node, conversion)
				else:
					value = conversion(node.findtext(name))
				e_data[key_name] = value

		return e_data
		
			
	def build_element(self, dom_tree, data_map):
		
		path, conversions = data_map
		
		nodes = dom_tree.findall(path)
		if (len(nodes) > 1):
			data = []
			for node in nodes:
				data.append(self.convert_element(node, conversions))
		else:
			data = self.convert_element(nodes[0], conversions)
			
		return data

				
	def forecast(self, country, area, city):
		
		url = self.url_template.substitute(
			server=self.api_server,
			country=country,
			area=area,
			city=city)
		
			
		try:
			response = urllib2.urlopen(url.encode('utf-8'))
		except IOError as e:
			logging.info("NRK::Error when opening URL -- %s", e)
			return None
			
		f = StringIO.StringIO(response.read())
		dom_tree = xml.etree.ElementTree.parse(f)
				
		results = {}
		for key, data_map in WEATHER_DATA.items():
			results[key] = self.build_element(dom_tree, data_map)
		
		return results



def main():

	w = NRK()
	
	forecast = w.forecast(u"Sweden", u"Skåne", u"Malmö")		
	pprint.pprint(forecast)
	


if __name__ == '__main__':
	main()

