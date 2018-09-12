import logging
import azure.functions as func
import pyclamd
from azure.storage.blob import BlockBlobService
import os
from urllib.parse import unquote

def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    cd = pyclamd.ClamdNetworkSocket()
    result = cd.scan_stream(myblob.read())
    logging.info(f'{result}')
    try:
        if (result['stream'][0] == 'FOUND'):
            virus = str(result['stream'][1])
            deleteBlob(myblob.uri)
            return f'blobname:{myblob.name}, blobsize:{myblob.length}, uri:{myblob.uri}, virus:{virus}'
    except TypeError:
        return f'novirus'

def deleteBlob(uri):
    conn_string = os.environ.get('BlockStorageAccount')
    uri = unquote(uri)
    container_name, file_name = extractBlobInfoFromUri(uri)
    account = BlockBlobService(connection_string = conn_string)
    logging.info(f'{container_name}, {file_name}')
    account.delete_blob(container_name, file_name)

def extractBlobInfoFromUri(uri):
    uri_length = len(uri)
    server_pos = uri.find(':443/') + 5
    strip_server = uri[server_pos:uri_length]
    file_pos = strip_server.find('/')
    strip_server_length = len(strip_server)
    container_name = strip_server[0:file_pos]
    file_name = strip_server[file_pos + 1:strip_server_length]
    return container_name, file_name


