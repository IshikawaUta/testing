# netlify/functions/app.py
import sys
import os
from io import BytesIO
import base64

# Tambahkan root proyek ke sys.path agar Flask app Anda dapat diimpor
# Ini penting karena fungsi Netlify berjalan di direktori netlify/functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app # Impor instance Flask app Anda

# Ini adalah handler untuk Netlify Function
# Netlify akan memanggil fungsi ini ketika ada permintaan HTTP
def handler(event, context):
    from werkzeug.wrappers import Request, Response
    from werkzeug.serving import run_simple # run_simple tidak digunakan di sini, bisa dihapus

    # Buat objek Request dari event Netlify
    # Netlify Functions menerima event yang mirip dengan AWS Lambda event
    # Werkzeug Request perlu environment dictionary
    environ = {
        'REQUEST_METHOD': event['httpMethod'],
        'SCRIPT_NAME': '',
        'PATH_INFO': event['path'],
        'QUERY_STRING': '&'.join([f"{k}={v}" for k, v in event['queryStringParameters'].items()]) if event['queryStringParameters'] else '',
        'SERVER_NAME': 'localhost', # Ini bisa diabaikan untuk Netlify
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'CONTENT_TYPE': event['headers'].get('content-type', ''),
        'CONTENT_LENGTH': str(len(event['body'])) if event['body'] else '0',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http', # Atau 'https' jika di produksi
        'wsgi.input': BytesIO(event['body'].encode('utf-8')) if event['body'] else BytesIO(b''),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'HTTP_HOST': event['headers'].get('host', ''),
        # Tambahkan semua header dari event ke environ
        **{'HTTP_' + k.upper().replace('-', '_'): v for k, v in event['headers'].items()}
    }

    # Jika ada body dan itu JSON, pastikan itu di-decode dengan benar
    if event.get('isBase64Encoded'):
        environ['wsgi.input'] = BytesIO(base64.b64decode(event['body']))
    elif event['body']:
        environ['wsgi.input'] = BytesIO(event['body'].encode('utf-8'))

    # Panggil aplikasi Flask Anda
    # Flask app menerima environ dan start_response
    response_data = []
    def start_response(status, headers):
        response_data.append(status)
        response_data.append(headers)

    response_iter = app(environ, start_response)
    
    # Kumpulkan body response
    response_body = b''.join(response_iter).decode('utf-8')

    # Konversi response Flask ke format yang diharapkan Netlify Function
    status_code = int(response_data[0].split(' ')[0])
    headers = dict(response_data[1])

    return {
        "statusCode": status_code,
        "headers": headers,
        "body": response_body
    }

# Untuk pengembangan lokal (opsional, jika Anda ingin menguji fungsi secara terpisah)
# Ini memerlukan instalasi netlify-cli dan menjalankan `netlify dev`
# if __name__ == '__main__':
#     from netlify_lambda_local.main import serve
#     serve(handler)