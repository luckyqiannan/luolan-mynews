import os
import json
import requests
import datetime
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_caching import Cache
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# 设置BASE_ID和TABLE_ID，优先使用环境变量，否则使用配置文件中的默认值
app.config['BASE_ID'] = os.getenv('BASE_ID', Config.BASE_ID)
app.config['TABLE_ID'] = os.getenv('TABLE_ID', Config.TABLE_ID)

# 设置缓存
cache = Cache(app)

# 飞书API相关函数
def get_tenant_access_token():
    """获取飞书tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "app_id": app.config['FEISHU_APP_ID'],
        "app_secret": app.config['FEISHU_APP_SECRET']
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        token = result.get("tenant_access_token")
        if not token:
            return None
        return token
    except Exception as e:
        return None

def try_get_bitable_data(token):
    """尝试获取多维表格数据"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app.config['BASE_ID']}/tables/{app.config['TABLE_ID']}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        items = []
        
        for record in data.get('data', {}).get('items', []):
            fields = record.get('fields', {})
            
            # 处理文章链接字段
            original_url = fields.get('文章链接', '')
            
            # 检查链接格式，如果是字典或字典表示的字符串则提取实际URL
            if original_url and isinstance(original_url, str) and ('{' in original_url):
                try:
                    # 尝试解析为字典
                    import ast
                    link_dict = ast.literal_eval(original_url.replace("'", "\""))
                    if isinstance(link_dict, dict) and 'link' in link_dict:
                        original_url = link_dict.get('link', '')
                except Exception as e:
                    pass
            elif original_url and isinstance(original_url, dict) and 'link' in original_url:
                original_url = original_url.get('link', '')
            
            item = {
                'id': record.get('record_id'),
                'title': fields.get('标题', ''),
                'quote': fields.get('金句在这里', ''),
                'comment': fields.get('黄叔点评', ''),  # 如果这个字段存在的话
                'content': fields.get('概要内容在这里', '') or fields.get('全文内容提取', ''),
                'original_url': original_url
            }
            items.append(item)
        
        return items
    except Exception as e:
        return None

def try_get_wiki_data(token):
    """尝试获取知识库数据"""
    # 先获取知识库节点列表
    url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/{app.config['BASE_ID']}/nodes"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        items = []
        
        # 处理知识库数据
        for node in data.get('data', {}).get('items', []):
            # 获取节点详情
            node_token = node.get('node_token')
            if not node_token:
                continue
                
            detail_url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/{app.config['BASE_ID']}/nodes/{node_token}"
            detail_response = requests.get(detail_url, headers=headers)
            
            if detail_response.status_code != 200:
                continue
                
            detail_data = detail_response.json().get('data', {})
            
            item = {
                'id': node_token,
                'title': detail_data.get('title', ''),
                'quote': detail_data.get('summary', ''),  # 使用摘要作为金句
                'comment': '',  # 知识库可能没有点评字段
                'content': detail_data.get('content', '')  # 内容可能需要进一步处理
            }
            items.append(item)
        
        return items
    except Exception as e:
        return None

@cache.cached(timeout=7000, key_prefix='feishu_data')
def get_feishu_data():
    """获取飞书数据，尝试多种方式"""
    token = get_tenant_access_token()
    if not token:
        return []
    
    # 尝试获取多维表格数据
    items = try_get_bitable_data(token)
    if items:
        return items
    
    # 如果多维表格获取失败，尝试获取知识库数据
    items = try_get_wiki_data(token)
    if items:
        return items
    
    # 如果都失败，返回一些测试数据，避免页面空白
    return [
        {
            'id': 'test1',
            'title': '测试文章 - API连接失败',
            'quote': '当前无法连接到飞书API，这是测试数据',
            'comment': '请检查飞书应用配置和权限设置',
            'content': '这是一篇测试文章，因为无法连接到飞书API，所以显示此内容。可能的原因：1. BASE_ID或TABLE_ID不正确；2. 飞书应用权限不足；3. 飞书多维表格或知识库已被删除或移动。请参考控制台日志获取更多信息。'
        }
    ]

# 路由
@app.route('/')
def index():
    articles = get_feishu_data()
    
    # 添加临时调试输出
    print("首页文章链接情况:")
    for article in articles:
        print(f"标题: {article.get('title')}")
        print(f"链接类型: {type(article.get('original_url'))}")
        print(f"链接内容: {article.get('original_url')}")
        print("-" * 30)
    
    now = datetime.datetime.now()
    return render_template('index.html', articles=articles, now=now)

@app.route('/article/<article_id>')
def article_detail(article_id):
    articles = get_feishu_data()
    now = datetime.datetime.now()
    for article in articles:
        if article['id'] == article_id:
            return render_template('detail.html', article=article, now=now)
    abort(404)

@app.errorhandler(404)
def page_not_found(e):
    now = datetime.datetime.now()
    return render_template('404.html', now=now), 404

if __name__ == '__main__':
    # 确保templates目录存在
    os.makedirs('templates', exist_ok=True)
    # 确保static目录存在
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, port=5004)