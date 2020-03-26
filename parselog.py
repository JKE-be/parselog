#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import sys
#import tempfile
import webbrowser
import random
import os


def unfuck(myList):
    return list(filter(None, myList))


def colorMe(lines):
    colors = 'green red blue gray yellow'.split(' ')
    for i, s in enumerate(lines):
        lines[i] = "".join(['<span style="color:%s"> %s </span>' % (colors[colidx], text) for colidx, text in enumerate(s.split(" | "))])
    return lines


def scrape_and_reformat():
    # call your scraping code here
    url = False
    search = sys.argv[1]
    f = open('/tmp/log', 'r')
    lines = f.read().split('\n%s' % datetime.strftime(datetime.now(), "%Y-%m-%d"))
    queries = []
    stacks = []

    find = [l for l in lines if 'GET %s HTTP' % search in l]
    if not find:
        return 'Request not found'
    requested_proc = unfuck(find[0].split(' '))[1]
    for line in lines:
        line = ' '.join([l.strip() for l in line.split('\n')])
        is_query = ' query: ' in line and len(line.split(' ')) > 6
        is_werkz = ' werkzeug: ' in line and 'GET ' in line
        is_stack = ' stack: ' in line and 'File: ' in line
        if is_query or is_werkz or is_stack:
            head, content = line.split(': ', 1)
            hour, procid, logtype, db, path = head.split(' ')
            if requested_proc == procid:
                if is_query:
                    queries.append(content)
                elif is_stack:
                    stacks.append(content)
                elif is_werkz:
                    #get_by_proc[procid]
                    url, _, status, _, querycount, time, remtime = list(filter(None, content.split("GET")[1].split(' ')))
                    if url != search:
                        url, stacks, queries = False, [], []
                    else:
                        break

    if url:
        html = """<div class='container-fluid'>
                    <h1>%s - [%s %s %s]</h1><br/><br/>
                    <div class='row'>
                        <div class='col-12'>
                            <div id="accordion">""" % (url, querycount, time, remtime)
        for inc, (q, s) in enumerate(zip(queries, stacks)):
            query_type = unfuck(q.split('query: ')[1].split(' '))[0].strip()
            query_table = query_type.upper() == "SELECT" and unfuck(q.split('FROM')[1].split(' '))[0] or unfuck(q.split(query_type)[1].split(' '))[0].strip()
            for KW in ['SELECT ', ' FROM ', ' WHERE ', ' ORDER ', ' LIMIT ']:
                q = q.replace(KW, "<b style='color:red'>%s</b>" % KW)
            html += """
            <div class="card">
                <div class="card-header" id="heading{inc}">
                  <h5 class="mb-0">
                    <button class="btn btn-link" data-toggle="collapse" data-target="#collapse{inc}" aria-expanded="false" aria-controls="collapse{inc}">
                      {head}
                    </button>
                  </h5>
                </div>

                <div id="collapse{inc}" class="collapse" aria-labelledby="heading{inc}" xdata-parent="#accordion">
                  <div class="card-body">
                    {query}
                    <br/><br/>
                    ---
                    <br/><br/>
                    {stack}
                  </div>
                </div>
              </div>
            """.format(
                inc=inc,
                head="# %s | %s - %s" % (inc, query_type, query_table),
                query=q.strip('query: '),
                stack="<br/>".join(colorMe(s.split('File:')[1:])),
            )
        html += "</div></div></div></div>"

        template = """
            <html>
                <head>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js" integrity="sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo=" crossorigin="anonymous"></script>
                    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
                    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
                </head>
                <body>
                    %s
                </body>
            </html>
        """ % html
        return template
    return 'no url'


def main():
    h = scrape_and_reformat()
    rand = random.randrange(1000, 10000)
    file = "log%s.html" % rand
    # with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
    with open('/tmp/parselog/%s' % file, 'w') as f:
        url = url = 'file://' + f.name
        f.write(h)

    online = len(sys.argv) >= 3 and sys.argv[2]
    if online:
        os.system('surge /tmp/parselog/ %s.surge.sh' % online)
        url = "https://%s.surge.sh/%s" % (online, file)
    webbrowser.open(url)


main()
