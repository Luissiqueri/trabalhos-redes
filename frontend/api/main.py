from typing import Union
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import magic

import auxilio as aux

print("Para acessar a aplicacao: http://localhost:8000/recursos/index.html")

app = FastAPI()

app.mount("/recursos", StaticFiles(directory="../",html = True), name="static")
app.mount("/graficos", StaticFiles(directory="graphs",html = True), name="graphs")

async def plot_graph(filename):
    p = aux.lista_pacotes(filename)
    publicIps = await aux.communication_graph(p)
    aux.grafico_mapa(publicIps)

@app.post("/uploadfile")
async def upload_file(file: UploadFile = File(...)):
    if file.filename.endswith('.pcap') and not file.filename.endswith('.pcapng'):
        raise HTTPException(status_code = 400, detail = "Apenas arquivos do tipo .pcapng")
    
    try:
        with open(file.filename, "wb") as buffer:
            buffer.write(await file.read())
            await plot_graph(file.filename)
        return{"dados" : {}} #insira aqui os dados a serem retornados
    
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))