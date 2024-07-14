from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.staticfiles import StaticFiles
# from typing import Union
import asyncio
import traceback
# from pydantic import BaseModel
# import magic
# import json

import auxilio as aux

print("Para acessar a aplicacao: http://localhost:8000/recursos/index.html")

app = FastAPI()

app.mount("/recursos", StaticFiles(directory="../",html = True), name="static")
app.mount("/graficos", StaticFiles(directory="graphs",html = True), name="graphs")

async def processIP(filename):
    p = aux.lista_pacotes(filename)
    publicIps = await aux.communication_graph(p)
    aux.grafico_mapa(publicIps)
    return {}

async def processARP(filename):
    p = aux.lista_pacotes(filename)
    return aux.getARPInfo(p)

async def processRIP(filename):
    #gambiarra temporaria
    p = aux.lista_pacotes("rip.pcap")
    return aux.handleRIP(p)

async def processUDP(filename):
    p = aux.lista_pacotes(filename)
    return {}

@app.post("/uploadfile/{protocol}")
async def upload_file(protocol: str, file: UploadFile = File(...)):
    try:
        with open(file.filename, "wb") as buffer:
            buffer.write(await file.read())
            if protocol == "IP":
                return await processIP(file.filename)
            if protocol == "ARP":
                return await processARP(file.filename)
            if protocol == "RIP":
                return await processRIP(file.filename)
            if protocol == "UDP":
                return await processUDP(file.filename)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code = 500, detail = str(e))


"""async def main():
    filename = 'arp.pcap'
    await proccessARP(filename)"""