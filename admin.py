from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from functools import wraps
import os #
import uuid #
from werkzeug.utils import secure_filename #
from urllib.parse import urlparse #

from models import db, Product

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('shop.index'))
        return fn(*args, **kwargs)
    return wrapper

def allowed_file(filename): #
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False #

@admin_bp.route('/products', methods=['GET', 'POST'])
@login_required
@admin_required
def products():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        product = Product(name=name, description=description, price=price)
        
         # Обработка локальной загрузки файла
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                if file.content_length > MAX_FILE_SIZE:
                    flash('File size too large (max 5MB)', 'danger')
                    return redirect(url_for('admin.products'))
                
                # Генерируем уникальное имя файла
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                
                # Сохраняем файл
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                
                product.image_filename = unique_filename
                flash('Image uploaded successfully', 'success')
        
        # Обработка URL изображения
        image_url = request.form.get('image_url', '').strip()
        if image_url:
            if is_valid_url(image_url):
                product.image_url = image_url
                flash('Image URL set successfully', 'success')
            else:
                flash('Invalid URL format', 'danger')
        
        db.session.add(product)
        db.session.commit()
        flash('Product added', 'success')
        return redirect(url_for('admin.products'))
    products = Product.query.all()
    return render_template('admin_products.html', products=products)

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        # Обновляем основные данные
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = request.form['price']
        
        # Обработка загрузки нового файла
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                if file.content_length > MAX_FILE_SIZE:
                    flash('File size too large (max 5MB)', 'danger')
                    return redirect(url_for('admin.edit_product', product_id=product_id))
                
                # Удаляем старый файл если он существует
                if product.image_filename:
                    old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_filename)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                # Сохраняем новый файл
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                
                product.image_filename = unique_filename
                product.image_url = None  # Сбрасываем URL если загружаем файл
                flash('Image updated successfully', 'success')
        
        # Обработка URL изображения
        image_url = request.form.get('image_url', '').strip()
        if image_url:
            if is_valid_url(image_url):
                # Удаляем старый файл если переходим на URL
                if product.image_filename:
                    old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_filename)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                    product.image_filename = None
                
                product.image_url = image_url
                flash('Image URL updated successfully', 'success')
            else:
                flash('Invalid URL format', 'danger')
        else:
            # Если URL очищен, но есть файл - оставляем файл
            if not product.image_filename:
                product.image_url = None
        
        # Обработка удаления изображения
        if 'remove_image' in request.form:
            if product.image_filename:
                old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_filename)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                product.image_filename = None
            product.image_url = None
            flash('Image removed', 'success')
        
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('edit_product.html', product=product)

@admin_bp.route('/products/delete/<int:product_id>')
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Удаляем локальный файл если существует
    if product.image_filename:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        file_path = os.path.join(upload_folder, product.image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted', 'success')
    return redirect(url_for('admin.products'))