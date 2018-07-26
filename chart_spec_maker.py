#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of chart_spec_maker.
#
#   chart_spec_maker is free software: you can
#   redistribute it and/or modify it under the terms of the GNU General
#   Public License as published by the Free Software Foundation, either
#   version 3 of the License, or (at your option) any later version.
#
#   chart_spec_maker. is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#   See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with chart_spec_maker. If not, see <http://www.gnu.org/licenses/>.
#
"""
chart_spec_maker:

Produces a spec file for each app storted in the provided URL.

Usage:
    chart_spec_maker -h
    chart_spec_maker --url=url [--include-provides]

Options:
    -h,--help           : show this help message
    --url=url           : URL of the charts repository to analyze
    --include-provides  : resulting specs will include provides for each chart version
"""
import docopt
import os
import jinja2
import yaml
import requests
from pkg_resources import parse_version

def match_first_valid_url(urls):
    for url in urls:
        try:
            requests.head(url)
            return url
        except Exception:
            pass

command_args = docopt.docopt(__doc__)

url = command_args['--url']
response = requests.get(url, stream=True)
index = yaml.load(response.raw)

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
template_file = 'spec.template'

if os.path.isfile(template_file):
    template = templateEnv.get_template(template_file)
else:
    exit(1)

for name in index['entries']:
    entry = {'name': '{0}-helm-charts'.format(name)}

    if command_args['--include-provides']:
        entry['provides'] = [
            '{0}-helm-chart = {1}'.format(
                name, parse_version(chart['version'])
            ) for chart in index['entries'][name]
        ]
    else:
        entry['provides'] = []

    # Setting the version of the RPM to the higest version of the chart
    versions = [parse_version(chart['version']) for chart in index['entries'][name]]
    entry['version'] = max(versions)
    entry['description'] = index['entries'][name][versions.index(entry['version'])]['description']
    entry['sources'] = [
        match_first_valid_url(
            chart['urls']
        ) for chart in index['entries'][name]
    ]
    entry['url'] = url

    template.stream(chart=entry).dump('{0}.spec'.format(entry['name']))
