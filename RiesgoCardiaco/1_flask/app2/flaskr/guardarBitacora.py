import os
from flask import Flask, jsonify, request,abort
from db import get_db
import numpy as np
from datetime import datetime
import requests

app = Flask(__name__)

@app.route("/guardarBitacora", methods=["POST"])
def guardarBitacora(): 
      print("entre a bitacora")     
      colesterol = request.json.get('colesterol', '')
      presion = request.json.get('presion', '')
      glucosa = request.json.get('glucosa', '')
      edad = request.json.get('edad', '')
      sobrepeso = request.json.get('sobrepeso', '')
      tabaquismo = request.json.get('tabaquismo', '')    
      strResult= request.json.get('respuesta', '')                
      param = np.array([[0,colesterol,presion,glucosa,edad,sobrepeso,tabaquismo]]).astype("float32")
      get_db().request_log.insert_one(        
             {  "timestamp": datetime.now().isoformat(), 
                "params": param[0].tolist(),  
                "response": strResult
             })
        
      return("Dato guardado en bitácora")
    
if __name__ == '__main__':
    app.run(port=5005)