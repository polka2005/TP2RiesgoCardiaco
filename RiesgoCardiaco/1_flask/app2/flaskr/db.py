import pymongo
from flask import g
def get_db():
    if 'db' not in g:
        print("conexion exitosa")
        #si se tiene instalado en la maquina de trabajo                  
       # CONNECTION_STRING = "mongodb://localhost:27017"   
        CONNECTION_STRING = "mongodb+srv://karina:karina@cluster0.vafnzvr.mongodb.net/"

        dbClient = pymongo.MongoClient(CONNECTION_STRING) 
        dbName="topicos2_bd"
        db = dbClient[dbName]
        g.db=db  
    return g.db
