from typing import Union
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import magic

import auxilio as aux

app = FastAPI()

def plot_graph(file: File):
    p = aux.lista_pacotes(file)
    aux.communication_graph(p)


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.pcap') and file.filename.endswith('.pcapng'):
        raise HTTPException(status_code = 400, detail = "Apenas arquivos do tipo .pcap")
    
    try:
        with open(file.filename, "wb") as buffer:
            buffer.write(await file.read())
            plot_graph(file);
        return{"filename" : file.filename}
    
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))
    



    

