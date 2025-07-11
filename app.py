# app.py
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from flask_flatpages import FlatPages
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from datetime import datetime
import os

app = Flask(__name__)
# Memuat konfigurasi dari config.py
app.config.from_object('config')
app.config['SECRET_KEY'] = 'your_very_secret_key' # Ganti dengan kunci rahasia yang kuat!

pages = FlatPages(app)

# Pastikan direktori 'content/products' dan 'content/blog' ada
os.makedirs('content/products', exist_ok=True)
os.makedirs('content/blog', exist_ok=True)
# Juga pastikan direktori untuk upload gambar Decap CMS ada
os.makedirs('static/uploads', exist_ok=True)
# Pastikan direktori admin ada
os.makedirs('static/admin', exist_ok=True)


# Menambahkan variabel global untuk tahun saat ini di semua template
@app.context_processor
def inject_global_vars():
    return dict(current_year=datetime.now().year)

# Halaman Beranda
@app.route('/')
def index():
    return render_template('index.html', title='Home')

# Halaman About
@app.route('/about')
def about():
    return render_template('about.html', title='About Us')

# Halaman Produk
@app.route('/products')
def products():
    all_products = [p for p in pages if p.path.startswith('products/')]
    
    for p in all_products:
        if 'date' not in p.meta:
            print(f"WARNING: Product {p.path} is missing 'date' in its metadata.")
        
    all_products.sort(key=lambda item: item.meta.get('date', '9999-99-99'), reverse=True)
    return render_template('products.html', products=all_products, title='Our Products')

@app.route('/product/<path:path>')
def product_detail(path):
    product = pages.get_or_404(f'products/{path}')
    return render_template('product_detail.html', product=product, title=product.meta.get('title', 'Product Detail'))

# Halaman Blog
@app.route('/blog')
def blog():
    all_posts = [p for p in pages if p.path.startswith('blog/')]

    for p in all_posts:
        if 'date' not in p.meta:
            print(f"WARNING: Blog post {p.path} is missing 'date' in its metadata.")

    all_posts.sort(key=lambda item: item.meta.get('date', '9999-99-99'), reverse=True)
    return render_template('blog.html', posts=all_posts, title='Our Blog')

@app.route('/blog/<path:path>')
def blog_post(path):
    post = pages.get_or_404(f'blog/{path}')
    return render_template('blog_post.html', post=post, title=post.meta.get('title', 'Blog Post'))

# Formulir Kontak (menggunakan Flask-WTF)
class ContactForm(FlaskForm):
    name = StringField('Nama', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Pesan', validators=[DataRequired()])
    submit = SubmitField('Kirim')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        flash('Pesan Anda telah terkirim! Terima kasih.', 'success')
        print(f"Nama: {form.name.data}, Email: {form.email.data}, Pesan: {form.message.data}")
        return redirect(url_for('contact'))
    return render_template('contact.html', title='Contact Us', form=form)

# Rute untuk mengakses halaman admin Decap CMS (index.html)
@app.route('/admin/')
def admin_index():
    # Mengirim file index.html dari direktori static/admin
    return send_from_directory(os.path.join(app.root_path, 'static', 'admin'), 'index.html')

# Rute untuk melayani file-file lain di dalam direktori static/admin (misalnya config.yml)
@app.route('/admin/<path:filename>')
def admin_files(filename):
    # Mengirim file yang diminta dari direktori static/admin
    return send_from_directory(os.path.join(app.root_path, 'static', 'admin'), filename)


# Menjalankan aplikasi
if __name__ == '__main__':
    app.run(debug=True)
