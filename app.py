from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
import os
import requests
import json
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# 数据库配置 - 支持环境变量
database_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
if database_url:
    # Vercel Postgres提供的URL可能需要调整
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # PostgreSQL连接配置
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'connect_args': {
            'sslmode': 'require'  # Vercel Postgres需要SSL
        }
    }
else:
    # 本地开发时使用SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 管理员密码配置
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')  # 在生产环境中应该使用更安全的密码

db = SQLAlchemy(app)

# 数据库模型
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20))
    price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(50), nullable=False)  # 书籍状况
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=1)  # 库存数量
    available_quantity = db.Column(db.Integer, default=1)  # 可售数量
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    date_sold = db.Column(db.DateTime)  # 售出日期
    
    def __repr__(self):
        return f'<Book {self.title}>'
    
    @property
    def is_sold_out(self):
        return self.available_quantity <= 0
    
    @property
    def is_sold(self):
        """判断书籍是否已售出（基于可售数量）"""
        return self.available_quantity <= 0

# 订单模型
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=True)  # 允许为空
    book = db.relationship('Book', backref=db.backref('orders', lazy=True))
    
    # 用户关联
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    
    # 保存书籍信息，即使书籍被删除也能保留订单记录
    book_title = db.Column(db.String(200), nullable=False)  # 书籍标题
    book_author = db.Column(db.String(100), nullable=False)  # 书籍作者
    book_price = db.Column(db.Float, nullable=False)  # 书籍价格
    
    buyer_name = db.Column(db.String(100), nullable=False)
    buyer_phone = db.Column(db.String(20))
    buyer_qq = db.Column(db.String(20))
    buyer_contact_preference = db.Column(db.String(20))  # phone 或 qq
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        book_title = self.book.title if self.book else self.book_title
        return f'<Order {self.id}: {book_title}>'

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    qq = db.Column(db.String(20))
    contact_preference = db.Column(db.String(20))
    user_token = db.Column(db.String(64), unique=True)  # 用于cookie识别
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.name}>'
    
    def generate_token(self):
        """生成用户token"""
        import secrets
        self.user_token = secrets.token_hex(32)
        return self.user_token

# 认证装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """获取当前用户"""
    user_token = request.cookies.get('user_token')
    if user_token:
        user = User.query.filter_by(user_token=user_token).first()
        if user:
            # 更新最后访问时间
            user.last_seen = datetime.utcnow()
            db.session.commit()
            return user
    return None

# 路由
@app.route('/')
def index():
    """主页 - 显示所有可购买的书籍"""
    available_books = Book.query.filter(Book.available_quantity > 0).order_by(Book.date_added.desc()).all()
    current_user = get_current_user()
    return render_template('index.html', books=available_books, current_user=current_user)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """管理员登录"""
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            session.permanent = True
            app.permanent_session_lifetime = timedelta(days=7)  # 7天有效期
            flash('管理员登录成功！', 'success')
            return redirect(url_for('admin'))
        else:
            flash('密码错误！', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    """管理员注销"""
    session.pop('is_admin', None)
    flash('已退出管理员模式', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin():
    """管理页面 - 显示所有书籍"""
    all_books = Book.query.order_by(Book.date_added.desc()).all()
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
    
    # 统计数据
    total_books = Book.query.count()
    total_inventory = db.session.query(db.func.sum(Book.quantity)).scalar() or 0
    available_inventory = db.session.query(db.func.sum(Book.available_quantity)).scalar() or 0
    sold_inventory = total_inventory - available_inventory
    pending_orders = Order.query.filter_by(status='pending').count()
    
    stats = {
        'total_books': total_books,
        'total_inventory': total_inventory,
        'available_inventory': available_inventory,
        'sold_inventory': sold_inventory,
        'pending_orders': pending_orders
    }
    
    return render_template('admin.html', books=all_books, orders=recent_orders, stats=stats)

@app.route('/orders')
@admin_required
def orders():
    """订单管理页面"""
    status_filter = request.args.get('status', 'all')
    if status_filter == 'all':
        orders = Order.query.order_by(Order.order_date.desc()).all()
    else:
        orders = Order.query.filter_by(status=status_filter).order_by(Order.order_date.desc()).all()
    
    return render_template('orders.html', orders=orders, current_status=status_filter)

@app.route('/my_orders')
def my_orders():
    """用户查看自己的订单"""
    current_user = get_current_user()
    if not current_user:
        flash('请先完成一次购买以查看订单状态', 'info')
        return redirect(url_for('index'))
    
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('my_orders.html', orders=orders, current_user=current_user)

@app.route('/scan_isbn')
@admin_required
def scan_isbn():
    """ISBN扫描页面"""
    return render_template('scan_isbn.html')

@app.route('/api/book_info/<isbn>')
def get_book_info(isbn):
    """通过ISBN获取书籍信息"""
    try:
        # 调用OpenLibrary API
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=details&format=json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            book_key = f"ISBN:{isbn}"
            
            if book_key in data:
                book_data = data[book_key]['details']
                
                # 提取书籍信息
                title = book_data.get('title', '')
                authors = book_data.get('authors', [])
                author = ', '.join([author.get('name', '') for author in authors]) if authors else ''
                
                # 如果没有作者信息，尝试从其他字段获取
                if not author and 'by_statement' in book_data:
                    author = book_data['by_statement']
                
                description = ''
                if 'description' in book_data:
                    if isinstance(book_data['description'], dict):
                        description = book_data['description'].get('value', '')
                    else:
                        description = book_data['description']
                
                publishers = book_data.get('publishers', [])
                publisher = publishers[0] if publishers else ''
                
                publish_date = book_data.get('publish_date', '')
                pages = book_data.get('number_of_pages', '')
                
                return jsonify({
                    'success': True,
                    'data': {
                        'title': title,
                        'author': author,
                        'isbn': isbn,
                        'description': description,
                        'publisher': publisher,
                        'publish_date': publish_date,
                        'pages': pages
                    }
                })
            else:
                return jsonify({'success': False, 'message': '未找到该ISBN对应的书籍信息'})
        else:
            return jsonify({'success': False, 'message': 'API请求失败'})
    
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'message': 'API请求超时，请稍后重试'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取书籍信息时发生错误: {str(e)}'})

@app.route('/confirm_book', methods=['GET', 'POST'])
@admin_required
def confirm_book():
    """确认添加书籍页面"""
    if request.method == 'POST':
        try:
            book = Book(
                title=request.form['title'],
                author=request.form['author'],
                isbn=request.form['isbn'],
                price=float(request.form['price']),
                condition=request.form['condition'],
                description=request.form['description'],
                quantity=int(request.form['quantity']),
                available_quantity=int(request.form['quantity'])
            )
            db.session.add(book)
            db.session.commit()
            flash('书籍添加成功！', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            flash(f'添加失败：{str(e)}', 'error')
            db.session.rollback()
    
    # GET请求，显示确认页面
    book_data = {
        'title': request.args.get('title', ''),
        'author': request.args.get('author', ''),
        'isbn': request.args.get('isbn', ''),
        'description': request.args.get('description', ''),
        'publisher': request.args.get('publisher', ''),
        'publish_date': request.args.get('publish_date', ''),
        'pages': request.args.get('pages', '')
    }
    
    return render_template('confirm_book.html', book_data=book_data)

@app.route('/add_book', methods=['GET', 'POST'])
@admin_required
def add_book():
    """添加新书籍"""
    if request.method == 'POST':
        try:
            book = Book(
                title=request.form['title'],
                author=request.form['author'],
                isbn=request.form['isbn'],
                price=float(request.form['price']),
                condition=request.form['condition'],
                description=request.form['description'],
                quantity=int(request.form.get('quantity', 1)),
                available_quantity=int(request.form.get('quantity', 1))
            )
            db.session.add(book)
            db.session.commit()
            flash('书籍添加成功！', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            flash(f'添加失败：{str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_book.html')

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    """编辑书籍信息"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        try:
            book.title = request.form['title']
            book.author = request.form['author']
            book.isbn = request.form['isbn']
            book.price = float(request.form['price'])
            book.condition = request.form['condition']
            book.description = request.form['description']
            
            # 更新库存数量
            new_quantity = int(request.form.get('quantity', book.quantity))
            if new_quantity != book.quantity:
                # 计算差值并更新可售数量
                diff = new_quantity - book.quantity
                book.quantity = new_quantity
                book.available_quantity = max(0, book.available_quantity + diff)
            
            db.session.commit()
            flash('书籍信息更新成功！', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            flash(f'更新失败：{str(e)}', 'error')
            db.session.rollback()
    
    return render_template('edit_book.html', book=book)

@app.route('/book_details/<int:book_id>')
def book_details(book_id):
    """书籍详情页面"""
    book = Book.query.get_or_404(book_id)
    current_user = get_current_user()
    return render_template('book_details.html', book=book, current_user=current_user)

@app.route('/buy_book/<int:book_id>', methods=['GET', 'POST'])
def buy_book(book_id):
    """购买书籍页面"""
    book = Book.query.get_or_404(book_id)
    current_user = get_current_user()
    
    if book.is_sold_out:
        flash('抱歉，该书籍已售完！', 'error')
        return redirect(url_for('book_details', book_id=book_id))
    
    if request.method == 'POST':
        try:
            quantity = int(request.form.get('quantity', 1))
            if quantity > book.available_quantity:
                flash(f'库存不足！当前可售数量：{book.available_quantity}', 'error')
                return render_template('buy_book.html', book=book, current_user=current_user)
            
            buyer_name = request.form['buyer_name']
            buyer_phone = request.form.get('buyer_phone', '')
            buyer_qq = request.form.get('buyer_qq', '')
            contact_preference = request.form['contact_preference']
            
            # 查找或创建用户
            user = current_user
            if not user:
                # 根据联系方式查找现有用户
                if contact_preference == 'phone' and buyer_phone:
                    user = User.query.filter_by(phone=buyer_phone, name=buyer_name).first()
                elif contact_preference == 'qq' and buyer_qq:
                    user = User.query.filter_by(qq=buyer_qq, name=buyer_name).first()
                
                # 如果找不到现有用户，创建新用户
                if not user:
                    user = User(
                        name=buyer_name,
                        phone=buyer_phone,
                        qq=buyer_qq,
                        contact_preference=contact_preference
                    )
                    user.generate_token()
                    db.session.add(user)
                    db.session.flush()  # 获取用户ID
            
            # 创建订单
            order = Order(
                book_id=book.id,
                user_id=user.id,
                book_title=book.title,
                book_author=book.author,
                book_price=book.price,
                buyer_name=buyer_name,
                buyer_phone=buyer_phone,
                buyer_qq=buyer_qq,
                buyer_contact_preference=contact_preference,
                quantity=quantity,
                total_price=book.price * quantity,
                notes=request.form.get('notes', '')
            )
            
            # 减少可售数量
            book.available_quantity -= quantity
            
            db.session.add(order)
            db.session.commit()
            
            # 设置用户cookie
            response = make_response(redirect(url_for('order_success', order_id=order.id)))
            if not current_user and user.user_token:
                response.set_cookie('user_token', user.user_token, 
                                  max_age=30*24*60*60)  # 30天有效期
            
            flash('订单提交成功！店主会尽快与您联系。', 'success')
            return response
            
        except Exception as e:
            flash(f'订单提交失败：{str(e)}', 'error')
            db.session.rollback()
    
    return render_template('buy_book.html', book=book, current_user=current_user)

@app.route('/order_success/<int:order_id>')
def order_success(order_id):
    """订单成功页面"""
    order = Order.query.get_or_404(order_id)
    current_user = get_current_user()
    return render_template('order_success.html', order=order, current_user=current_user)

@app.route('/update_order_status/<int:order_id>/<status>')
@admin_required
def update_order_status(order_id, status):
    """更新订单状态"""
    try:
        order = Order.query.get_or_404(order_id)
        
        old_status = order.status
        order.status = status
        
        # 只有当书籍还存在时才处理库存变化
        if order.book:
            # 如果订单被取消，需要恢复库存
            if status == 'cancelled' and old_status != 'cancelled':
                order.book.available_quantity += order.quantity
            # 如果从取消状态恢复，需要减少库存
            elif old_status == 'cancelled' and status != 'cancelled':
                if order.book.available_quantity >= order.quantity:
                    order.book.available_quantity -= order.quantity
                else:
                    flash('库存不足，无法恢复订单！', 'error')
                    return redirect(url_for('orders'))
        else:
            # 如果书籍已被删除，给用户提示
            if status == 'cancelled' and old_status != 'cancelled':
                flash(f'订单状态已更新为：{status}（注意：该订单的书籍已被删除）', 'warning')
            elif old_status == 'cancelled' and status != 'cancelled':
                flash(f'订单状态已更新为：{status}（注意：该订单的书籍已被删除，无法恢复库存）', 'warning')
            else:
                flash(f'订单状态已更新为：{status}（注意：该订单的书籍已被删除）', 'warning')
            db.session.commit()
            return redirect(url_for('orders'))
        
        db.session.commit()
        flash(f'订单状态已更新为：{status}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'更新订单状态失败：{str(e)}', 'error')
    
    return redirect(url_for('orders'))

@app.route('/delete_book/<int:book_id>')
@admin_required
def delete_book(book_id):
    """删除书籍"""
    book = Book.query.get_or_404(book_id)
    
    # 检查是否有关联的订单
    all_orders = Order.query.filter_by(book_id=book_id).all()
    if all_orders:
        # 检查是否所有订单都是已完成或已取消状态
        pending_orders = []
        confirmed_orders = []
        
        for order in all_orders:
            if order.status == 'pending':
                pending_orders.append(order)
            elif order.status == 'confirmed':
                confirmed_orders.append(order)
        
        # 如果有待处理或已确认的订单，不允许删除
        if pending_orders or confirmed_orders:
            error_msg = f'无法删除！该书籍还有未完成的订单：'
            if pending_orders:
                error_msg += f' {len(pending_orders)} 个待处理订单'
            if confirmed_orders:
                if pending_orders:
                    error_msg += '，'
                error_msg += f' {len(confirmed_orders)} 个已确认订单'
            error_msg += '。只有当所有订单都是已完成或已取消状态时才能删除书籍。'
            flash(error_msg, 'error')
            return redirect(url_for('admin'))
    
    # 如果没有订单，或所有订单都是已完成/已取消状态，则可以删除
    db.session.delete(book)
    db.session.commit()
    flash('书籍删除成功！', 'success')
    return redirect(url_for('admin'))

@app.route('/mark_sold/<int:book_id>')
@admin_required
def mark_sold(book_id):
    """标记书籍为售出"""
    book = Book.query.get_or_404(book_id)
    
    if book.available_quantity > 0:
        book.available_quantity = 0
        book.date_sold = datetime.utcnow()
        db.session.commit()
        flash(f'《{book.title}》已标记为售出！', 'success')
    else:
        flash(f'《{book.title}》已经是售出状态！', 'warning')
    
    return redirect(url_for('admin'))

@app.route('/mark_available/<int:book_id>')
@admin_required
def mark_available(book_id):
    """标记书籍为可售"""
    book = Book.query.get_or_404(book_id)
    
    if book.available_quantity == 0:
        book.available_quantity = book.quantity
        book.date_sold = None
        db.session.commit()
        flash(f'《{book.title}》已标记为可售！', 'success')
    else:
        flash(f'《{book.title}》已经是可售状态！', 'warning')
    
    return redirect(url_for('admin'))

@app.route('/api/stats')
def api_stats():
    """API：获取统计数据"""
    total_books = Book.query.count()
    total_inventory = db.session.query(db.func.sum(Book.quantity)).scalar() or 0
    available_inventory = db.session.query(db.func.sum(Book.available_quantity)).scalar() or 0
    sold_inventory = total_inventory - available_inventory
    pending_orders = Order.query.filter_by(status='pending').count()
    
    return jsonify({
        'total_books': total_books,
        'total_inventory': total_inventory,
        'available_inventory': available_inventory,
        'sold_inventory': sold_inventory,
        'pending_orders': pending_orders
    })

@app.route('/admin/check_integrity')
@admin_required
def check_data_integrity():
    """检查数据完整性"""
    # 查找孤立的订单（引用不存在的书籍）
    orphaned_orders = db.session.query(Order).outerjoin(Book).filter(Book.id.is_(None)).all()
    
    # 查找有问题的订单（book_id为空）
    null_book_orders = Order.query.filter(Order.book_id.is_(None)).all()
    
    issues = []
    if orphaned_orders:
        issues.append(f"发现 {len(orphaned_orders)} 个孤立订单（引用已删除的书籍）")
    if null_book_orders:
        issues.append(f"发现 {len(null_book_orders)} 个book_id为空的订单")
    
    if not issues:
        flash('数据完整性检查通过！', 'success')
    else:
        flash('发现数据完整性问题：' + '；'.join(issues), 'warning')
    
    return redirect(url_for('admin'))

@app.route('/admin/fix_integrity')
@admin_required
def fix_data_integrity():
    """修复数据完整性问题"""
    try:
        # 删除孤立的订单
        orphaned_orders = db.session.query(Order).outerjoin(Book).filter(Book.id.is_(None)).all()
        orphaned_count = len(orphaned_orders)
        for order in orphaned_orders:
            db.session.delete(order)
        
        # 删除book_id为空的订单
        null_book_orders = Order.query.filter(Order.book_id.is_(None)).all()
        null_count = len(null_book_orders)
        for order in null_book_orders:
            db.session.delete(order)
        
        db.session.commit()
        
        if orphaned_count > 0 or null_count > 0:
            flash(f'已修复数据完整性问题：删除了 {orphaned_count} 个孤立订单和 {null_count} 个无效订单', 'success')
        else:
            flash('没有发现需要修复的数据完整性问题', 'info')
    
    except Exception as e:
        db.session.rollback()
        flash(f'修复失败：{str(e)}', 'error')
    
    return redirect(url_for('admin'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
else:
    # 在Vercel等生产环境中初始化数据库
    with app.app_context():
        db.create_all() 