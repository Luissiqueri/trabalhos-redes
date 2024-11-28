from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import traceback

import auxilio as aux


app = FastAPI()

origins = ["https://jai-front-tawny.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def processIP(file):
    p = aux.lista_pacotes(file)
    return await aux.communication_graph(p)

async def processARP(file):
    p = aux.lista_pacotes(file)
    return aux.getARPInfo(p)

async def processRIP(file):
    p = aux.lista_pacotes(file)
    return aux.handleRIP(p)

async def processUDP(file):
    p = aux.lista_pacotes(file)
    return aux.handleUDP(p)

async def processaTCP(file):
    p = aux.lista_pacotes(file)
    return aux.handleTCP(p)

async def processHTTP(file):
    p = aux.lista_pacotes(file)
    return aux.HTTPcontent(p)

async def processaDNS(file):
    p = aux.lista_pacotes(file)
    return aux.handleDNS(p)

async def processSNMP(file):
    p = aux.lista_pacotes(file)
    return aux.handleSNMP(p)

@app.post("/uploadfile/{protocol}")
async def upload_file(protocol: str, file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        if protocol == "IP":
            return await processIP(file_content)
        if protocol == "ARP":   
            return await processARP(file_content)
        if protocol == "RIP":
            return await processRIP(file_content)
        if protocol == "UDP":
            return await processUDP(file_content)
        if protocol == "TCP":
            return await processaTCP(file_content)
        if protocol == "HTTP":
            return await processHTTP(file_content)
        if protocol == "DNS":
            return await processaDNS(file_content)
        if protocol == "SNMP":
            return await processSNMP(file_content)
    except Exception as e :
        traceback.print_exc()
        raise HTTPException(status_code = 500, detail = str(e))



"""async def main():
    filename = 'arp.pcap'
    await proccessARP(filename)"""

# from typing import Union
# from pydantic import BaseModel
# import magic
# import json
# app.mount("/recursos", StaticFiles(directory="../",html = True), name="static")
# app.mount("/output", StaticFiles(directory="output",html = True), name="static")
# app.mount("/graficos", StaticFiles(directory="graphs",html = True), name="graphs")

    # try:
    #     with open(file.filename, "wb") as buffer:
    #         buffer.write(await file.read())
    #         if protocol == "IP":
    #             return await processIP(file.filename)
    #         if protocol == "ARP":
    #             return await processARP(file.filename)
    #         if protocol == "RIP":
    #             return await processRIP(file.filename)
    #         if protocol == "UDP":
    #             return await processUDP(file.filename)
    #         if protocol == "TCP":
    #             return await processaTCP(file.filename)
    #         if protocol == "HTTP":
    #             return await processHTTP(file.filename)
    #         if protocol == "DNS":
    #             return await processaDNS(file.filename)
    #         if protocol == "SNMP":
    #             return await processSNMP(file.filename)
    # except Exception as e:
    #     traceback.print_exc()
    #     raise HTTPException(status_code = 500, detail = str(e))
