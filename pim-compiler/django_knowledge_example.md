# Django REST Framework 先验知识

## 概述

本文档包含生成 Django REST Framework API 的领域知识和最佳实践。

## 项目结构规范

### 标准 Django 项目结构

```
myproject/
├── manage.py                # Django 管理脚本
├── myproject/              # 项目配置目录
│   ├── __init__.py
│   ├── settings/           # 设置文件目录
│   │   ├── __init__.py
│   │   ├── base.py        # 基础设置
│   │   ├── development.py  # 开发环境设置
│   │   └── production.py   # 生产环境设置
│   ├── urls.py            # 主 URL 配置
│   ├── wsgi.py            # WSGI 配置
│   └── asgi.py            # ASGI 配置
├── apps/                   # 应用目录
│   ├── __init__.py
│   ├── users/             # 用户应用
│   │   ├── __init__.py
│   │   ├── models.py      # 数据模型
│   │   ├── views.py       # 视图
│   │   ├── serializers.py # 序列化器
│   │   ├── urls.py        # URL 路由
│   │   ├── admin.py       # 管理后台
│   │   ├── apps.py        # 应用配置
│   │   └── migrations/    # 数据库迁移
│   └── api/               # API 应用
│       ├── __init__.py
│       ├── v1/            # API 版本 1
│       │   ├── __init__.py
│       │   └── urls.py
│       └── v2/            # API 版本 2
├── static/                 # 静态文件
├── media/                  # 媒体文件
├── templates/              # 模板文件
├── requirements/           # 依赖管理
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── .env.example           # 环境变量示例
└── README.md              # 项目说明

```

## 代码生成规范

### 1. 设置文件 (settings/base.py)

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = []

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_filters',
]

LOCAL_APPS = [
    'apps.users',
    'apps.api',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

### 2. 模型定义 (apps/users/models.py)

```python
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
```

### 3. 序列化器 (apps/users/serializers.py)

```python
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm', 'first_name', 'last_name')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)
```

### 4. 视图 (apps/users/views.py)

```python
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer

User = get_user_model()

class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()
```

### 5. URL 配置 (apps/users/urls.py)

```python
from django.urls import path
from .views import UserListCreateAPIView, UserDetailAPIView

app_name = 'users'

urlpatterns = [
    path('', UserListCreateAPIView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('me/', UserDetailAPIView.as_view(), name='user-me'),
]
```

## 依赖管理

### requirements/base.txt

```
Django==4.2.0
djangorestframework==3.14.0
django-cors-headers==4.0.0
django-filter==23.2
python-dotenv==1.0.0
psycopg2-binary==2.9.6
gunicorn==20.1.0
```

### requirements/development.txt

```
-r base.txt
django-debug-toolbar==4.1.0
pytest==7.3.1
pytest-django==4.5.2
factory-boy==3.2.1
faker==18.9.0
```

## 生成流程

1. **创建项目结构**
   - 创建所有必要的目录
   - 创建 `__init__.py` 文件

2. **生成配置文件**
   - `settings/` 目录下的配置文件
   - `.env.example` 环境变量示例

3. **创建应用**
   - 使用 `python manage.py startapp` 的结构
   - 生成模型、视图、序列化器

4. **配置 URL**
   - 主 URL 配置
   - 各应用的 URL 配置

5. **创建迁移**
   - 生成初始迁移文件

6. **生成测试**
   - 单元测试
   - API 测试

## 执行命令

### 初始化项目
```bash
# 安装依赖
pip install -r requirements/development.txt

# 创建数据库
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 运行开发服务器
python manage.py runserver
```

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定应用测试
pytest apps/users/

# 显示覆盖率
pytest --cov=apps
```

## 最佳实践

1. **使用环境变量**
   - 敏感信息不要硬编码
   - 使用 `.env` 文件管理配置

2. **分离设置文件**
   - base.py: 通用设置
   - development.py: 开发环境
   - production.py: 生产环境

3. **API 版本控制**
   - 使用 URL 路径版本控制 `/api/v1/`
   - 保持向后兼容

4. **认证和权限**
   - 使用 Token 或 JWT 认证
   - 细粒度的权限控制

5. **序列化器分离**
   - 读写分离
   - 嵌套序列化器合理使用

6. **分页和过滤**
   - 默认启用分页
   - 提供灵活的过滤选项