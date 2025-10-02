from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import current_user, login_required

from models import db, Product, Order, OrderItem

shop_bp = Blueprint('shop', __name__)

def _get_cart():
    return session.setdefault('cart', {})

@shop_bp.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@shop_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@shop_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart = _get_cart()
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    session.modified = True
    flash('Added to cart', 'success')
    return redirect(url_for('shop.cart'))

@shop_bp.route('/cart')
def cart():
    cart = _get_cart()
    cart_items = []
    cart_total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            total = product.price * qty
            cart_items.append({'product': product, 'quantity': qty, 'total': total})
            cart_total += total
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total)

@shop_bp.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = _get_cart()
    cart.pop(str(product_id), None)
    session.modified = True
    return redirect(url_for('shop.cart'))

@shop_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart = _get_cart()
    if not cart:
        flash('Cart is empty', 'warning')
        return redirect(url_for('shop.cart'))

    cart_total = 0
    order = Order(user=current_user, total_price=0)
    db.session.add(order)

    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            line_total = product.price * qty
            order_item = OrderItem(order=order, product=product, quantity=qty, price=line_total)
            db.session.add(order_item)
            cart_total += line_total

    order.total_price = cart_total
    db.session.commit()

    session['cart'] = {}
    flash('Order placed! (Payment mocked).', 'success')
    return redirect(url_for('shop.index'))