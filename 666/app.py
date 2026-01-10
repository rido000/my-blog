from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Link, Category, SiteConfig
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.context_processor
def inject_site_config():
    # Defaults
    config = {
        'contact_email': 'contact@example.com',
        'site_title': '数字花园',
        'site_description': '欢迎来到我的私人导航站。这里汇集了互联网上最优质的工具、资源与灵感。即使身处繁杂的信息洪流，也能保持高效与专注。',
        'site_brand': 'ForestNav',
        'site_tutorial_url': '#',
        'site_youtube_url': 'https://youtube.com',
        'site_github_url': 'https://github.com'
    }
    
    try:
        # Fetch all configs from DB
        db_configs = SiteConfig.query.all()
        for cfg in db_configs:
            if cfg.key in config:
                config[cfg.key] = cfg.value
    except:
        pass
        
    return config

@app.cli.command("init-db")
def init_db_command():
    """Create database tables and a default admin user."""
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin')
            user.set_password('admin')  # Default password, change immediately!
            db.session.add(user)
            
            # Default Categories
            c1 = Category(name="常用工具", order=1)
            c2 = Category(name="学习资源", order=2)
            c3 = Category(name="娱乐休闲", order=3)
            db.session.add_all([c1, c2, c3])
            
            db.session.commit()
            print("Initialized database with default admin user (admin/admin).")
        else:
            print("Database already initialized.")

@app.route('/')
def index():
    categories = Category.query.order_by(Category.order).all()
    
    # Logic for Hot Tools
    top_links = Link.query.order_by(Link.clicks.desc()).limit(10).all()
    # Filter out links with 0 clicks if you want, or keep them to show something initially
    # top_links = [l for l in top_links if l.clicks > 0] 
    
    if top_links:
        # Create a pseudo-category object using a simple class or dict wrapper
        class MockQuery:
            def __init__(self, items):
                self.items = items
            def __iter__(self):
                return iter(self.items)
            def count(self):
                return len(self.items)

        class HotCategory:
            id = 'hot'
            name = '🔥 热门工具'
            links = MockQuery(top_links)
        
        # Insert at beginning
        categories.insert(0, HotCategory())

    total_links = Link.query.count()
    return render_template('index.html', categories=categories, total_links=total_links)

@app.route('/visit/<int:link_id>')
def visit_link(link_id):
    link = Link.query.get_or_404(link_id)
    link.clicks += 1
    db.session.commit()
    return redirect(link.url)

@app.route('/rd/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('用户名或密码错误', 'error')
    
    return render_template('login.html')

@app.route('/rd/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/rd/dashboard')
@login_required
def dashboard():
    categories = Category.query.order_by(Category.order).all()
    return render_template('dashboard.html', categories=categories)

def get_icon_for_url(url):
    url = url.lower()
    mapping = {
        'github.com': 'fab fa-github',
        'youtube.com': 'fab fa-youtube',
        'youtu.be': 'fab fa-youtube',
        'twitter.com': 'fab fa-twitter',
        'x.com': 'fab fa-x-twitter',
        'facebook.com': 'fab fa-facebook',
        'instagram.com': 'fab fa-instagram',
        'linkedin.com': 'fab fa-linkedin',
        'discord.com': 'fab fa-discord',
        'discord.gg': 'fab fa-discord',
        'reddit.com': 'fab fa-reddit',
        'weixin.qq.com': 'fab fa-weixin',
        'wechat.com': 'fab fa-weixin',
        'weibo.com': 'fab fa-weibo',
        'bilibili.com': 'fab fa-bilibili',
        'stackoverflow.com': 'fab fa-stack-overflow',
        'google.com': 'fab fa-google',
        'telegram.org': 'fab fa-telegram',
        't.me': 'fab fa-telegram',
        'docker.com': 'fab fa-docker',
        'openai.com': 'fas fa-robot',
        'chatgpt.com': 'fas fa-robot',
        'wikipedia.org': 'fab fa-wikipedia-w',
        'amazon': 'fab fa-amazon',
        'apple.com': 'fab fa-apple',
        'microsoft.com': 'fab fa-microsoft',
        'zhihu.com': 'fas fa-book-open',
        'douban.com': 'fas fa-book',
        'taobao.com': 'fas fa-shopping-bag',
        'jd.com': 'fas fa-shopping-cart'
    }
    
    for key, icon in mapping.items():
        if key in url:
            return icon
            
    return 'fas fa-globe'

@app.route('/link/add', methods=['POST'])
@login_required
def add_link():
    title = request.form.get('title')
    url = request.form.get('url')
    description = request.form.get('description')
    icon = request.form.get('icon')
    category_id = request.form.get('category_id')
    
    if not (title and url and category_id):
        flash('请填写必要信息', 'error')
        return redirect(url_for('dashboard'))
        
    if not icon:
        icon = get_icon_for_url(url)
        
    link = Link(title=title, url=url, description=description, icon=icon, category_id=category_id)
    db.session.add(link)
    db.session.commit()
    flash('链接添加成功', 'success')
    return redirect(url_for('dashboard'))

@app.route('/link/delete/<int:id>', methods=['POST'])
@login_required
def delete_link(id):
    link = Link.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    flash('链接已删除', 'success')
    return redirect(url_for('dashboard'))

@app.route('/category/add', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name')
    if name:
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('分类添加成功', 'success')
    return redirect(url_for('dashboard'))

@app.route('/category/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('分类已删除', 'success')
    return redirect(url_for('dashboard'))
@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    fields = ['contact_email', 'site_title', 'site_description', 'site_brand', 'site_tutorial_url', 'site_youtube_url', 'site_github_url']
    
    for field in fields:
        value = request.form.get(field)
        value = request.form.get(field)
        if value: # Only update if value is present (or clear if empty string provided? usually we want to allow empty but not none)
            # Actually, let's treat existing keys updates. 
            # Note: HTML forms submit empty strings for empty inputs.
            
            cfg = SiteConfig.query.get(field)
            if not cfg:
                cfg = SiteConfig(key=field, value=value)
                db.session.add(cfg)
            else:
                cfg.value = value
                
    db.session.commit()
    flash('站点设置已更新', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        # Ensure tables exist (including new SiteConfig)
        db.create_all()
    app.run(debug=True)
