#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os.path
import codecs
from pprint import pprint

import pyquery
from jinja2 import Template, Environment

def extract_stuff(f):
    q = pyquery.PyQuery(filename=f)
    title = q('.topictitle').text()
    pprint(title)
    dl = q(q('.variablelist dl'))
    if dl:
        properties = from_dl(dl)
        return {'title': title, 'properties': properties}
    table = q('.informaltable')
def from_dl(q):
    dt = q('dt').map(lambda i, e: q(e).text())
    dd = q('dd').map(lambda i, e: u'\n\n'.join(q(p).text() for p in q(e)('p')))
    d = [{'name':n,'doc':d} for n,d in zip(dt,dd)]
    return d

for f in sys.argv[1:]:
    context = extract_stuff(f)
    env = Environment(line_statement_prefix='##')
    template = env.from_string(codecs.open('resource_template.py', encoding='utf-8').read())
    parts = re.split('::', context['title'])
    classname = parts[-1]
    context['name'] = classname
    filename = os.path.join(*parts) + '.py'
    dirname = os.path.join(*parts[:-1])
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    init = os.path.join(dirname, '__init__.py')
    with codecs.open(init, 'a', encoding='utf-8'):
        os.utime(init, None)
    with codecs.open(init, 'r+', encoding='utf-8') as f:
        content = f.read()
        if classname not in content:
            f.write(u'from {0} import {0}\n'.format(classname))
    with codecs.open(filename, 'w', encoding='utf-8') as f:
        f.write(template.render(context))
