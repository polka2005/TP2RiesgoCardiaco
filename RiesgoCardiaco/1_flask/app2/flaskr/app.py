from flask import Flask, request, jsonify
from db import get_db
import numpy as np
import tensorflow as tf
from flask import request_started, Response 
import requests
from datetime import datetime, timedelta 
import time
import redis



servicio_guardarEnBitacora =  'http://127.0.0.1:5005/guardarBitacora?'
servicio_autorizacion   =  'http://127.0.0.1:5001/autorizacion?'
redis_client = redis.Redis(host="localhost", port=6379)
ttl = 60                                                       # Limit resets after 1 minute
        

app = Flask(__name__)

#Función que valida los parámetros. Primero valida que estén todos y despues el rango de los mismos

def validarParametros(colesterol,presion, glucosa,edad,sobrepeso,tabaquismo):
    
    errores = []
    # Validar que los parámetros no sean nulos o vacíos
    for param, nombre in zip((colesterol, presion, glucosa, edad, sobrepeso, tabaquismo),
                             ("colesterol", "presion", "glucosa", "edad", "sobrepeso", "tabaquismo")):
        if param is None or param == '':
            errores.append(f"Se requiere el {nombre}")

    # Validar rangos
    for valor, nombre, rango in zip((colesterol, presion, glucosa, edad),
                                    ("colesterol", "presion", "glucosa", "edad"),
                                    ((1, 3), (0.6, 1.8), (0.5, 2.0), (0, 99))):
        if valor is not None and (float(valor) < rango[0] or float(valor) > rango[1]):
            errores.append(f"Se requiere el rango del {nombre} debe estar entre {rango[0]} y {rango[1]}")

    # Validar valores específicos
    for valor, nombre, valores_validos in zip((sobrepeso, tabaquismo),
                                              ("sobrepeso", "tabaquismo"),
                                              ((0, 1), (0, 1))):
        if valor is not None and float(valor) not in valores_validos:
            errores.append(f"Se requiere el rango del {nombre} debe estar entre {', '.join(map(str, valores_validos))}")
    if errores:
        print(errores)   
        """errores1 = ["Error de Parametros: "]
        errores2  =errores
        errores = errores1.extended(errores2)"""
        
        return (errores)  # Retorna un mensaje de error con todos los errores
    else:
        return None  # Parametros validos
        

def predecir_conTiempo(api_key, data, limit):
        # Set limit and TTL (time to live) for user's rate limit
        user_key = f"rate_limit:{api_key}"                             # Create a unique key for the user's rate limit        
        current_count = int(redis_client.hget(user_key, "count") or 0) # Check if user's limit has been reached        
        if current_count >= limit:
            return "error"  # se termino el tiempo
        # Update count and expiration for the user's rate limit
        redis_client.hincrby(user_key, "count", 1)
        redis_client.expire(user_key, ttl)            
        return prediceFuncion(data)     # Call the prediction function         
      


def validartiempo(api_key,data):
        inicio = time.time()       
        type = get_user_type(api_key)       
        if type == "FREEMIUM":
            response = predecir_conTiempo(api_key, data,5)              
        elif type == "PREMIUM":
            response = predecir_conTiempo(api_key, data,50)  
        else:
            Response(response="Invalid user", status=500, mimetype="application/json")        
        if response == "error":
           return("error")      
        return response
       
def get_user_type(api_key):
    encontro = get_db().usuario.find_one({"api_key": api_key})
    if encontro != None:
         tipo = encontro["tipo"]
    else:
         tipo = None       
    return(tipo)


def prediceFuncion(data):  
    colesterol = data.get('colesterol')
    presion = data.get('presion')
    glucosa = data.get('glucosa')
    edad = data.get('edad')
    sobrepeso = data.get('sobrepeso')
    tabaquismo = data.get('tabaquismo')  
    error = validarParametros(colesterol,presion, glucosa,edad,sobrepeso,tabaquismo)       
    if error == None:
       param = np.array([[0,colesterol,presion,glucosa,edad,sobrepeso,tabaquismo]]).astype("float32")                 
       model = tf.keras.models.load_model("C:/RiesgoCardiaco/modeloRiesgoC.keras")

       
       result = model.predict(param)            
       return(result)
    else:
       return(error)


@app.route("/altaUsuario", methods=["POST"])
def altaUsuario():          
        print("pase por ingresar") 
        error = None
        api_key = request.headers.get("Authorization")
        usuario = request.json.get('usuario', '')
        contraseña = request.json.get('contraseña','')
        tipo = request.json.get('tipo','')
        if tipo != "FREEMIUM" and tipo != "PREMIUM":
           error = "Mal tipo"       
        elif api_key == None or api_key == "":       #controlo que tenga api_key para que el nuevo usuario tenga su api_key        
           error = "No tiene Api Key, fijese el Headers"
        elif usuario == None or usuario == "":       #controlo el usuario
           error = "No tiene usuario"              
        elif contraseña == None or contraseña == "": #controlo la contraseña
           error = "No tiene contraseña"                      
        else:
           encontro = get_db().usuario.find_one({"api_key": api_key})        
           if (encontro == None):          
              encontro = get_db().usuario.find_one({"usuario": usuario})
              if (encontro == None):                                        
                get_db().usuario.insert_one(
                  {"api_key":api_key,
                   "usuario": usuario, 
                   "contraseña": contraseña,
                   "tipo":tipo
                  })     
              else:   
                 error= "Encontro el usuario, no se puede ingresar"          
           else:   
                 error= "Existe el Api_key. Cada Api_key se asigna a un usuario"  
        if error:
            return(error)               
        return ("Se cargó el usuario exitosamente!")

#Solo para predecir el modelo, tomando los parámetros del json. 
@app.route("/predictor", methods=["POST"])
def predictor():      
      respuesta = requests.post(servicio_autorizacion, headers=request.headers)   ## lo busca en el servicio de autorizacion. Autentifica contra la api_key autorizadas.      
      if respuesta.status_code == 200:
         api_key = request.headers.get("Authorization")                            #Toma api_key de Postman, ya que es autorizada                                 
         data = request.json
         prediccion=validartiempo(api_key,data)
         print(type(prediccion))
         if isinstance(prediccion, list):
            return(prediccion)
         elif isinstance(prediccion, str):
            return("Excedio el limite de consultas el usuario")
         resultValor= prediccion[0][0]
         result = ": Por lo tanto, el paciente tiene riesgo cardíaco" if prediccion[0][0] > 0.5 else ": Por lo tranto, el paciente no tiene riesgo cardíaco" 
        
         data["respuesta"] = result
        
         respuesta = requests.post(servicio_guardarEnBitacora, json=data)
         if respuesta.status_code == 200: 
               resultado = str(resultValor) + result
               return jsonify({"prediction": resultado})
         else:
               return jsonify("respuesta diferente a 200")         
      else:
        return jsonify("No autorizado")      

if __name__ == '__main__':
    app.run(port=5000)

