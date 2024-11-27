from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.staticfiles import StaticFiles
# from typing import Union
import asyncio
import traceback
# from pydantic import BaseModel
# import magic
# import json
from fastapi.middleware.cors import CORSMiddleware

import auxilio as aux

print("Para acessar a aplicacao: http://localhost:8000/recursos/index.html")

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

# Configure CORS
origins = [
    "http://localhost:3000",  # Add your frontend origin(s) here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow requests from these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.mount("/recursos", StaticFiles(directory="../",html = True), name="static")
app.mount("/output", StaticFiles(directory="output",html = True), name="static")
app.mount("/graficos", StaticFiles(directory="graphs",html = True), name="graphs")

async def processIP(filename):
    p = aux.lista_pacotes(filename)
    return await aux.communication_graph(p)
    # aux.grafico_mapa(publicIps)
    # return {}

async def processARP(filename):
    p = aux.lista_pacotes(filename)
    return aux.getARPInfo(p)

async def processRIP(filename):
    #gambiarra temporaria
    p = aux.lista_pacotes("rip.pcap")
    return aux.handleRIP(p)

async def processUDP(filename):
    p = aux.lista_pacotes(filename)
    return aux.handleUDP(p)

async def processaTCP(filename):
    p = aux.lista_pacotes(filename)
    return aux.handleTCP(p)

async def processHTTP(filename):
    p = aux.lista_pacotes(filename)
    return aux.HTTPcontent(p)

async def processaDNS(filename):
    p = aux.lista_pacotes(filename)
    return aux.handleDNS(p)

async def processSNMP(filename):
    p = aux.lista_pacotes(filename)
    return aux.handleSNMP(p)

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
            if protocol == "TCP":
                return await processaTCP(file.filename)
            if protocol == "HTTP":
                return await processHTTP(file.filename)
            if protocol == "DNS":
                return await processaDNS(file.filename)
            if protocol == "SNMP":
                return await processSNMP(file.filename)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code = 500, detail = str(e))


"""async def main():
    filename = 'arp.pcap'
    await proccessARP(filename)"""