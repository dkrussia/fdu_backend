import base64
import hashlib
import logging
import os
from json import JSONDecodeError
from fastapi import HTTPException
from requests import Response
from starlette import status
from pprint import pprint
from pydantic import BaseModel
import json
logger = logging.getLogger('log_service')

handler = logging.FileHandler(filename='logs/service.log',
                              mode='a',
                              encoding='utf-8', )
formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S')
handler.setFormatter(formatter)

logger.setLevel(logging.INFO)
logger.addHandler(handler)


def handling_microservice_response(resp: Response, service: str) -> dict:
    logger.info(
        f"""
            URL: {resp.url}
            Method: {resp.request.method}
            Request Body: {resp.request.body}
            Response Body: {resp.content.decode("utf-8")}
            Status Code: {resp.status_code}\n\n
        """)
    if resp.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{service} Обращение по неизвесному пути. Код ошибки 404.",
        )
    if resp.status_code == 422:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resp.json(),
        )
    if resp.status_code == 500:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{service} Возникла ошибка 500.",
        )
    if resp.status_code == 502:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{service} Не доступен или не смог запутится.",
        )
    try:
        response_data = resp.json()
        return response_data
    except JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{service} Не могу распознать JSON. JSONDecodeError. \n{str(e)}\n {resp.content}",
        )


class BaseSchema(BaseModel):
    """
    extended_type:
         <datetime>; <props_of_type> {"datetime_format": "DD-MM-YYYY HH:mm"}
         <selected>; <props_of_type> {"path": "DD-MM-YYYY HH:mm"}
    """
    @classmethod
    def get_headers(cls):
        headers = []
        for name, prop in cls.schema()['properties'].items():
            header_type = prop.get('type', None)
            header = {"value": name, 'text': prop["title"], 'type': header_type}

            header.update({'props_of_type': {}})

            if props_of_type := prop.get('props_of_type'):
                header.update({'props_of_type': props_of_type})

            if header_type == 'array':
                header.update({'entity': prop.get('entity')})

            if format := prop.get('format'):
                header.update({'format': format})

            if extended_type := prop.get('extended_type'):
                header.update({'extended_type': extended_type})

            if hide := prop.get('hide'):
                header.update({'hide': hide})

            # Производит вставку значения колонки/поля как HTML
            if prop.get('html'):
                header.update({'html': True})

            # Dynamic select - List
            if prop.get('dynamic'):
                header.update({'dynamic': True})
            headers.append(header)

        return headers


def generate_temporary_password():
    return base64.urlsafe_b64encode(hashlib.md5(os.urandom(128)).digest())[:8].decode('utf-8')


import re
import unidecode

def slugify(text):
    text = unidecode.unidecode(text).lower()
    return re.sub(r'[\W_]+', '-', text)
