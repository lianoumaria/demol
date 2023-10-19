import uuid
import os
import base64
import subprocess
import shutil

import tarfile

from pydantic import BaseModel

from fastapi import FastAPI, File, UploadFile, status, HTTPException, Security
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from demol.lang import build_model

API_KEY = os.getenv("API_KEY", "Cslq4QfG0A4vNZzjOf1miz7v")

api_keys = [
    API_KEY
]

api = FastAPI()

api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header in api_keys:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMP_DIR = '/tmp/smauto'


if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)


class DeMoLModel(BaseModel):
    name: str
    text: str
    type: str = ''


@api.post("/validate/file")
async def validate_file(file: UploadFile = File(...),
                        api_key: str = Security(get_api_key)):
    print(f'Validation for request: file=<{file.filename}>,' + \
          f' descriptor=<{file.file}>')
    resp = {
        'status': 200,
        'message': ''
    }
    fd = file.file
    u_id = uuid.uuid4().hex[0:8]
    ext = file.filename.split('.')[-1]
    fpath = os.path.join(
        TMP_DIR,
        f'model_for_validation-{u_id}.{ext}'
    )
    with open(fpath, 'w') as f:
        f.write(fd.read().decode('utf8'))
    try:
        model = build_model(fpath)
        print('Model validation success!!')
        resp['message'] = 'Model validation success'
    except Exception as e:
        print('Exception while validating model. Validation failed!!')
        print(e)
        resp['status'] = 404
        resp['message'] = str(e)
        raise HTTPException(status_code=400, detail=f"Validation error: {e}")
    return resp


@api.post("/validate")
async def validate(model: DeMoLModel,
                   api_key: str = Security(get_api_key)):
    text = model.text
    name = model.name
    mtype = model.type if model.type not in (None, '') else 'device'
    if len(text) == 0:
        return 404
    resp = {
        'status': 200,
        'message': ''
    }
    if mtype == 'peripheral':
        ext = 'hwd'
    elif mtype == 'device':
        ext = 'dev'
    else:
        raise HTTPException(status_code=400, detail=f"Not a valid model type")
    u_id = uuid.uuid4().hex[0:8]
    fpath = os.path.join(
        TMP_DIR,
        f'model_for_validation-{u_id}.{ext}'
    )
    with open(fpath, 'w') as f:
        f.write(text)
    try:
        model = build_model(fpath)
        print('Model validation success!!')
        resp['message'] = 'Model validation success'
    except Exception as e:
        print('Exception while validating model. Validation failed!!')
        print(e)
        resp['status'] = 404
        resp['message'] = str(e)
        raise HTTPException(status_code=400, detail=f"Validation error: {e}")
    return resp
