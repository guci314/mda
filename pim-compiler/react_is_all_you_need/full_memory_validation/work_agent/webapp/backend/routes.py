from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity
import jwt
from models import User, Post, Comment
from database import db
from auth import token_required
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化JWT
    jwt = JWTManager(app)
    
    # 创建所有表
    with app.app_context():
        db.create_all()
    
    # 用户注册
    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        # 检查必需字段
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Username, email, and password are required'}), 400
        
        # 检查用户是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400
            
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        # 创建新用户
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201
    
    # 用户登录
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # 生成访问令牌
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    # 获取当前用户信息
    @app.route('/api/user', methods=['GET'])
    @token_required
    def get_user(current_user):
        return jsonify(current_user.to_dict()), 200
    
    # 创建文章
    @app.route('/api/posts', methods=['POST'])
    @token_required
    def create_post(current_user):
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('content'):
            return jsonify({'message': 'Title and content are required'}), 400
        
        post = Post(
            title=data['title'],
            content=data['content'],
            author=current_user
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify(post.to_dict()), 201
    
    # 获取所有文章
    @app.route('/api/posts', methods=['GET'])
    def get_posts():
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return jsonify([post.to_dict() for post in posts]), 200
    
    # 获取单篇文章
    @app.route('/api/posts/<int:post_id>', methods=['GET'])
    def get_post(post_id):
        post = Post.query.get_or_404(post_id)
        return jsonify(post.to_dict()), 200
    
    # 更新文章
    @app.route('/api/posts/<int:post_id>', methods=['PUT'])
    @token_required
    def update_post(current_user, post_id):
        post = Post.query.get_or_404(post_id)
        
        if post.author_id != current_user.id:
            return jsonify({'message': 'Permission denied'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        
        db.session.commit()
        
        return jsonify(post.to_dict()), 200
    
    # 删除文章
    @app.route('/api/posts/<int:post_id>', methods=['DELETE'])
    @token_required
    def delete_post(current_user, post_id):
        post = Post.query.get_or_404(post_id)
        
        if post.author_id != current_user.id:
            return jsonify({'message': 'Permission denied'}), 403
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Post deleted successfully'}), 200
    
    # 创建评论
    @app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
    @token_required
    def create_comment(current_user, post_id):
        post = Post.query.get_or_404(post_id)
        
        data = request.get_json()
        
        if not data or not data.get('content'):
            return jsonify({'message': 'Content is required'}), 400
        
        comment = Comment(
            content=data['content'],
            author=current_user,
            post=post
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify(comment.to_dict()), 201
    
    # 获取文章的所有评论
    @app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
    def get_comments(post_id):
        post = Post.query.get_or_404(post_id)
        comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
        return jsonify([comment.to_dict() for comment in comments]), 200
    
    return app