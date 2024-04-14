import os
from flask import Flask, jsonify, request,abort
from db import get_db
conjunto_api = {
     "karina", "karina2","karina77"
}
app = Flask(__name__)

##servivios    

#para controlar que la api_key esta o no autorizada, se basa en un conjunto de api_keys autorizadas.
@app.route("/autorizacion", methods=["POST"])
def autorizacion():
      api_key = request.headers.get("Authorization")
      if api_key not in conjunto_api:
         abort(401, description="API key no autorizada")      
      return ("API key autorizada") 
        

if __name__ == '__main__':
    app.run(port=5001)