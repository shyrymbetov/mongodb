# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import pymongo
import webbrowser
import os

# Starting parsing with BeautifulSoup4
allFilms = []

for i in range(1, 5):
    url = 'https://editorial.rottentomatoes.com/guide/essential-2000s-movies/' + str(i) + '/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    raw = soup.findAll('div', class_='row countdown-item')
    for data in raw:
        allFilms.append(
            {
                'position': int(data.find("div", class_="countdown-index-resposive").text[1:]),
                'name': data.find("h2").contents[0].text,
                'link': data.find("h2").contents[0]['href'],
                'year': data.find("span", class_="subtle start-year").text[1:-1],
                'score': data.find("span", class_="tMeterScore").text,
                'img': data.find("img", class_="article_poster")['src'],

            }
        )

# Switch on our Mongodb Server
db_client = pymongo.MongoClient("mongodb://localhost:27017/")
current_db = db_client["project"]
collection = current_db["films"]
collection.drop()

for i in allFilms:
    ins_result = collection.insert_one(i)


# Show our database in browser with JavaScript

f = open('index.html', 'w')

table_element = ""

for y in collection.find():
    table_element += """<tr>
                <td>{}</td>
                <td><a href="{}">{}</a></td>
                <td>{}</td>
                <td><img src="{}" width="100"/></td>
                <td>{}</td>
                <td>{}</td>
            </tr>""".format(y['position'], y['link'], y['name'], y['year'], y['img'], y['year'], y['score'], )

html_template = '''
<!-- 
* Working with dynamic table
* WebSite: http://www.dynatable.com/
-->

<!-- 	Bootstrap v2.3.2 -->
<link rel="stylesheet" media="all" href="https://s3.amazonaws.com/dynatable-docs-assets/css/bootstrap-2.3.2.min.css" />
<!-- Plugin styles -->
<link rel="stylesheet" media="all" href="https://s3.amazonaws.com/dynatable-docs-assets/css/jquery.dynatable.css" />

<!--  jQuery v3.0.0-beta1 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.0.0-beta1/jquery.js"></script>

<!-- JS Pluging -->
<script type='text/javascript' src='https://s3.amazonaws.com/dynatable-docs-assets/js/jquery.dynatable.js'></script>


<div class = "container">
	<table id="example" class="table table-striped table-bordered" cellspacing="0" width="100%">
        <thead>
            <tr>
                <th>Position</th>
                <th>Name</th>
                <th>Year</th>
                <th>Image</th>
                <th>Date</th>
                <th>Score</th>
            </tr>
        </thead>

        <tfoot>
            <tr>
                <th>Position</th>
                <th>Name</th>
                <th>Year</th>
                <th>Image</th>
                <th>Date</th>
                <th>Score</th>
            </tr>
        </tfoot>

        <tbody>
            {}
        </tbody>
    </table>
 </div>



'''.format(table_element)

html_template += """<script type="text/javascript">
     $(document).ready(function() {
    $('#example').dynatable();
} );
 </script>"""

f.write(html_template)
f.close()

filename = 'file:///' + os.getcwd() + '/' + 'index.html'
webbrowser.open_new_tab(filename)