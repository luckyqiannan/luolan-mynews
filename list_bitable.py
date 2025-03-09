import requests
import json
import os
from config import Config

def list_all_bitables():
    """列出所有可访问的多维表格"""
    # 获取配置
    config = Config()
    app_id = config.FEISHU_APP_ID
    app_secret = config.FEISHU_APP_SECRET
    
    print(f'使用的APP_ID: {app_id}')
    
    # 获取tenant_access_token
    token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    token_headers = {'Content-Type': 'application/json'}
    token_data = {'app_id': app_id, 'app_secret': app_secret}
    
    try:
        token_response = requests.post(token_url, headers=token_headers, data=json.dumps(token_data))
        print(f'Token获取状态: {token_response.status_code}')
        token_result = token_response.json()
        token = token_result.get("tenant_access_token")
        
        if not token:
            print(f'获取token失败: {token_result}')
            return
            
        print('成功获取token')
        
        # 列出所有应用
        print("\n尝试列出所有应用:")
        app_url = "https://open.feishu.cn/open-apis/bitable/v1/apps"
        app_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        app_response = requests.get(app_url, headers=app_headers)
        print(f'应用列表获取状态: {app_response.status_code}')
        
        if app_response.status_code == 200:
            app_data = app_response.json()
            apps = app_data.get('data', {}).get('items', [])
            print(f'找到 {len(apps)} 个应用')
            
            for i, app in enumerate(apps):
                app_id = app.get('app_id')
                app_name = app.get('name')
                print(f'\n应用 {i+1}: {app_name} (ID: {app_id})')
                
                # 获取该应用下的所有表格
                tables_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_id}/tables"
                tables_response = requests.get(tables_url, headers=app_headers)
                
                if tables_response.status_code == 200:
                    tables_data = tables_response.json()
                    tables = tables_data.get('data', {}).get('items', [])
                    print(f'  找到 {len(tables)} 个表格')
                    
                    for j, table in enumerate(tables):
                        table_id = table.get('table_id')
                        table_name = table.get('name')
                        print(f'  表格 {j+1}: {table_name} (ID: {table_id})')
                        print(f'  访问URL: https://open.feishu.cn/open-apis/bitable/v1/apps/{app_id}/tables/{table_id}/records')
                else:
                    print(f'  获取表格列表失败: {tables_response.text[:200]}')
        else:
            print(f'获取应用列表失败: {app_response.text[:200]}')
            
        # 尝试使用wiki API
        print("\n尝试列出所有知识空间:")
        wiki_url = "https://open.feishu.cn/open-apis/wiki/v2/spaces"
        wiki_response = requests.get(wiki_url, headers=app_headers)
        print(f'知识空间列表获取状态: {wiki_response.status_code}')
        print(f'响应内容: {wiki_response.text[:200]}')
        
        # 尝试使用文档API
        print("\n尝试列出所有文档:")
        docs_url = "https://open.feishu.cn/open-apis/drive/v1/files"
        docs_response = requests.get(docs_url, headers=app_headers)
        print(f'文档列表获取状态: {docs_response.status_code}')
        print(f'响应内容: {docs_response.text[:200]}')
        
    except Exception as e:
        print(f'发生错误: {str(e)}')
        
    print("\n解决方案建议:")
    print("1. 确保飞书应用已添加以下权限:")
    print("   - bitable:app:read - 读取多维表格应用")
    print("   - bitable:table:readonly - 读取多维表格内容")
    print("2. 确保多维表格已与应用共享或对应用可见")
    print("3. 尝试在飞书开发者平台重新获取正确的BASE_ID和TABLE_ID")
    print("4. 参考飞书API文档: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/bitable-v1/bitable-overview")

if __name__ == '__main__':
    list_all_bitables()
