from symbol import parameters

from flask import Flask, request, Response, render_template, make_response, session, redirect, url_for
import hashlib
import json
import urllib
from functools import wraps
app = Flask(__name__)

app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
)

app.secret_key = b"\x98c\xaf\xf3`q\x8e\x1a\xe3\x91\xf5c\xe9O\xd72\x98EG'N\x1d&\x17"


def auth(f):
    """
    Tämä decorator hoitaa kirjautumisen tarkistamisen ja ohjaa tarvittaessa kirjautumissivulle
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not 'kirjautunut' in session:
            return redirect(url_for('kirjaudu'))
        return f(*args, **kwargs)
    return decorated

@app.route('/',methods=['GET'])
@auth
def autolaskuri():

    try:
        session['laskuri'] = session['laskuri'] + 1
    except:
        session['laskuri'] = 0
    
    automerkit_oletus = {
            "1": { "nimi": "Tesla", "maara": 0},
            "2": { "nimi": "Lada" , "maara": 0},
            "3": { "nimi": "Mini" , "maara": 0}
            }
    
    form = request.values
    
    try:
        lkm = int(form.get("lkm", 1))
    except Exception as e:
        print("Virheellinen lkm")

    try:
        automerkit = json.loads(form.get("automerkit_json"))
    except Exception as e:
        automerkit = automerkit_oletus

    try:
        automerkki = form.get("automerkki", "1")
    except:
        automerkki = "1"

    automerkit[automerkki]["maara"] = automerkit[automerkki]["maara"] + lkm        
        
    # luodaan parametrilista linkkiä varten
    parametrit = urllib.parse.urlencode({
        "lkm" :"1" ,
        "automerkit_json": json.dumps(automerkit)
    })
    
   
    rendered = render_template("jinja.html", lkm = lkm, automerkit_json= json.dumps(automerkit), automerkit= automerkit, parametrit = parametrit) 
    response = make_response(rendered)
    response.headers['Content-Type'] = 'application/xhtml+xml; charset=utf-8'
    return response


@app.route('/kirjaudu')
def kirjaudu():

    try:
        kayttajatunnus = request.args.get('tunnus')
    except:
        kayttajatunnus = None

    try:
        salasana = request.args.get('salasana')
    except:
        salasana = None

    if salasana and kayttajatunnus:
        m = hashlib.sha512()
        avain = u"omasalainenavain"
        m.update(avain.encode('utf-8'))
        m.update(salasana.encode('utf-8'))
        if kayttajatunnus == "ties4080" and m.hexdigest() == ("366e90b5fe29a9d9c1420afa334c4b19c4d63dcd200f424b7a9fe332"
                                                              "8a352da5818fc03cffa463c2362db3535b612df4eb27df33d4720fbf5"
                                                              "92964571ad7572e"):
            # jos kaikki ok niin asetetaan sessioon tieto kirjautumisesta ja ohjataan laskurisivulle
            session['kirjautunut'] = "ok"
            return redirect(url_for('autolaskuri'))
            # jos ei ollut oikea salasana niin pysytään kirjautumissivulla.
        return render_template('kirjaudu.html')


    rendered = render_template("kirjaudu.html" )
    response = make_response(rendered)
    response.headers['Content-Type'] = 'application/xhtml+xml; charset=utf-8'
    return response

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('laskuri', None)
    session.pop('kirjautunut', None)
    return redirect(url_for('kirjaudu'))


@app.route('/nollaa')
def nollaa():
    session.pop('laskuri', None)
    # url_for-metodilla voidaan muodostaa osoite haluttuun funktioon. redirect taas ohjaa suoraan tälle sivulle joten
    # nollaa-osoite ei tarvitse omaa sisältöä
    return redirect(url_for('autolaskuri'))

