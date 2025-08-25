from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    """主页路由"""
    return render_template('index.html')

@app.route('/user/<username>')
def user_profile(username):
    """用户资料路由"""
    return render_template('profile.html', username=username)

@app.route('/api/hello')
def hello_api():
    """简单的API路由"""
    return jsonify({
        'message': 'Hello, World!',
        'status': 'success'
    })

@app.route('/api/echo', methods=['POST'])
def echo_api():
    """回显API路由"""
    data = request.get_json()
    return jsonify({
        'received': data,
        'status': 'success'
    })

@app.route('/submit', methods=['POST'])
def submit_form():
    """处理表单提交"""
    name = request.form.get('name')
    email = request.form.get('email')
    
    # 在实际应用中，这里可能会保存到数据库
    # 我们这里只是简单地返回一个成功消息
    
    return jsonify({
        'message': f'感谢提交，{name}！我们已收到您的信息。',
        'name': name,
        'email': email,
        'status': 'success'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)