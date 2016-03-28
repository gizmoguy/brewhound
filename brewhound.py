from flask import Flask, Response, render_template
app = Flask(__name__)

from bs4 import BeautifulSoup
import urllib, json

@app.route('/')
def api_root():
    return render_template('index.html')

@app.route('/taplist/<locationid>')
def api_taplist(locationid):
    try:
        locid = int(locationid)
    except:
        return json.dumps({'error': 'Bad location ID'})

    url = 'http://brewhound.nz/embedlocation.php?locationID={:d}'.format(locid)

    r = urllib.urlopen(url)
    soup = BeautifulSoup(r)

    locdiv     = soup.find('div', {'class': 'locationDetails'})
    name       = locdiv.h3.text
    contactdiv = locdiv.find_all('div', {'class': 'contactDetails'})

    contactdeets = []
    for deet in contactdiv:
        contactdeets.append(deet.text)

    location = {
        'name': name,
        'contact': contactdeets
        }

    listings = soup.find('ul', id='listings')
    taplist = []
    for li in listings.findAll('li'):
        brewdiv = li.find('div', {'class': ['itemBrewery', 'phoneVisible']})
        beerdiv = li.find('div', {'class': 'itemTitle'})
        metadiv = li.find_all('div', {'class': 'itemAlcohol'})
        logodiv = li.find('div', {'class': 'itemLogo'})

        brewery = brewdiv.a.text
        beer    = beerdiv.a.text
        style   = metadiv[0].text
        abv     = metadiv[1].text
        badge   = "http://brewhound.nz/" + urllib.quote(logodiv.a.img['src'])

        tapdict = {
            'brewery': brewery,
            'beer':    beer,
            'style':   style,
            'abv':     abv,
            'badge':   badge
            }
        taplist.append(tapdict)

    ret  = json.dumps({'location': location, 'taplist': taplist})
    resp = Response(ret, status=200, mimetype='application/json')
    return resp

@app.route('/dashboard/<locationid>')
def api_dashboard(locationid):
    try:
        locid = int(locationid)
    except:
        return json.dumps({'error': 'Bad location ID'})

    url = 'https://brewhound.sla.ac/taplist/{:d}'.format(locid)

    r = urllib.urlopen(url)
    data = json.load(r)

    venue = data['location']['name']
    beers = data['taplist']

    return render_template('dashboard.html', venue=venue, beers=beers)

if __name__ == '__main__':
    app.run()
