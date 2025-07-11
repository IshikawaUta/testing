# netlify/functions/app.py
import sys
import os

# Tambahkan root proyek ke sys.path agar Flask app Anda dapat diimpor
# Ini penting karena fungsi Netlify berjalan di direktori netlify/functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app # Impor instance Flask app Anda

# Ini adalah handler untuk Netlify Function
# Netlify akan memanggil fungsi ini ketika ada permintaan HTTP
def handler(event, context):
    from werkzeug.wrappers import Request, Response
    from werkzeug.serving import run_simple

    # Buat objek Request dari event Netlify
    request = Request(event)

    # Panggil aplikasi Flask Anda
    response = app(request.environ, lambda status, headers: Response(status=status, headers=headers))

    # Konversi response Flask ke format yang diharapkan Netlify Function
    return {
        "statusCode": response.status_code,
        "headers": dict(response.headers),
        "body": response.get_data(as_text=True)
    }

# Untuk pengembangan lokal (opsional, jika Anda ingin menguji fungsi secara terpisah)
if __name__ == '__main__':
    from netlify_lambda_local.main import serve
    serve(handler)