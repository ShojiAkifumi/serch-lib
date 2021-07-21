from flask import Flask, render_template, request
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
import requests, json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/serch', methods=['POST'])
def serch():
    url = 'https://iss.ndl.go.jp/api/opensearch?'
    keyword = '"'
    if request.form['book_name']:
        title = request.form['book_name']
        url += '&title=' + urllib.parse.quote(title)
        keyword += ' ' + title + ' '
    if request.form['creator_name']:
        creator = request.form['creator_name']
        url += '&creator=' + urllib.parse.quote(creator)
        keyword += ' ' + creator + ' '
    if request.form['publisher_name']:
        publisher = request.form['publisher_name']
        url += '&publisher=' + urllib.parse.quote(publisher)
        keyword += ' ' + publisher + ' '
    if request.form['mediatype'] != '0':
        url += '&mediatype=' + request.form['mediatype']
    range = request.form['range']
    keyword += '"'
    url += '&cnt=' + range
    print(url)
    req = urllib.request.Request(url)

    with urllib.request.urlopen(req) as response:
        XmlData = response.read()

    xml = ET.fromstring(XmlData)
    data = []
    isbn = '9784999999996'
    for book in xml.iter('item'):
        description = []
        title = book.find('title').text
        try:
            author = book.find('author').text
        except:
            author = ''
        try:
            category = book.find('category').text
        except:
            category = ''
        try:
            publisher = book.find('{http://purl.org/dc/elements/1.1/}publisher').text
        except:
            publisher = ''
        try:
            if book.find('{http://purl.org/dc/elements/1.1/}identifier').attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] == "dcndl:ISBN":
                isbn = book.find('{http://purl.org/dc/elements/1.1/}identifier').text
        except:
            pass
        try:
            description.append(book.find('{http://purl.org/dc/elements/1.1/}description').text)
        except:
            pass
        guid = book.find('guid').text
        data.append({
            'title': title,
            'author': author,
            'publisher': publisher,
            'category': category,
            'isbn': isbn,
            'description' : description,
            'guid': guid
        })
    return render_template('serch.html', data = data, keyword = keyword)
@app.route('/detail', methods=['GET'])
def detail():
    guid = request.args.get('guid') + '.json'
    res = requests.get(guid)
    isbn = request.args.get('isbn')
    json_data = json.loads(res.text)
    json_data.pop('link')
    try:
        json_data.pop('identifier')
    except:
        pass
    data = []
    for k, v in json_data.items():
        if type(v) is list:
            for i in v:
                if type(i) is dict:
                    for o,p in i.items():
                        data.append({o:p})
                else:
                    data.append({k:i})
        else:
            data.append({k:v})
    title = data.pop(0).pop('value')
    url = urllib.parse.quote(title)
    return render_template('detail.html', data = data, isbn = isbn, title = title, url = url)
if __name__ == '__main__':
    app.run()