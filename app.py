from flask import Flask, render_template, request
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/serch', methods=['POST'])
def serch():
    url = 'https://iss.ndl.go.jp/api/opensearch?cnt=10&dpid=iss-ndl-opac'
    if request.form['book_name']:
        url += '&title=' + urllib.parse.quote(request.form['book_name'])
    if request.form['creator_name']:
        url += '&creator=' + urllib.parse.quote(request.form['creator_name'])
    req = urllib.request.Request(url)

    with urllib.request.urlopen(req) as response:
        XmlData = response.read()

    xml = ET.fromstring(XmlData)
    data = []
    
    for item in xml.findall('./channel/item'):
        title = item.find('title').text
        try:
            author = item.find('author').text
        except:
            author = ''
        category = item.find('category').text
        url = item.find('guid').text
        data.append({
            'title': title,
            'author': author,
            'category': category,
            'url': url
        })
    return render_template('serch.html', data = data)

if __name__ == '__main__':
    app.run()