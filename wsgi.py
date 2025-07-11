# wsgi.py
from app import app as application

# Opsional: Jika Anda ingin Decap CMS bekerja dengan Netlify Identity pada pengembangan lokal,
# Anda bisa uncomment baris berikut (meskipun tidak umum untuk produksi)
# application.config['SERVER_NAME'] = 'localhost:5000'