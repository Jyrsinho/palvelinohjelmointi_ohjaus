from flask import Flask, request, Response, render_template, make_response, session
import json
import urllib
app = Flask(__name__)

app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
)


@app.route('/',methods=['GET'])
def autolaskuri():
    
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
