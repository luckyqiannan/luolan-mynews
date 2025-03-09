import requests
import json
import os

def test_feishu_connection():
    # 配置信息
    app_id = 'cli_a74fdb29e66f500b'
    app_secret = 'cjymplvV5bihFBINCnNEEfB6cxUNR1SK'
    base_id = 'UhkYwpijYifSEckJKdkcILFrnmg'
    table_id = 'tbl0eSf2q4qcd2ny'
    
    print(f'配置信息:\napp_id={app_id}\nbase_id={base_id}\ntable_id={table_id}')
    
    # 获取tenant_access_token
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    headers = {'Content-Type': 'application/json'}
    data = {'app_id': app_id, 'app_secret': app_secret}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f'\nToken获取状态: {response.status_code}')
        token_data = response.json()
        token = token_data.get('tenant_access_token')
        
        if not token:
            print(f'获取token失败: {token_data}')
            return
            
        print('成功获取token')
        print(f'Token值: {token[:10]}...')  # 只打印token的前10个字符，保护安全
        
        # 获取多维表格数据
        # 尝试使用不同的API路径
        print("\n尝试标准API路径:")
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{base_id}/tables/{table_id}/records'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        print(f'数据获取状态: {response.status_code}')
        print(f'响应内容: {response.text[:200]}')
        
        # 尝试使用wiki API路径
        print("\n尝试wiki API路径:")
        url = f'https://open.feishu.cn/open-apis/wiki/v2/spaces/{base_id}/nodes'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        print(f'数据获取状态: {response.status_code}')
        print(f'响应内容: {response.text[:200]}')
        
        # 打印完整的API文档链接，帮助排查
        print("\n参考信息:")
        print("飞书多维表格API文档: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/bitable-v1/bitable-overview")
        print("飞书知识库API文档: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/wiki-v2/wiki-overview")
            
    except Exception as e:
        print(f'发生错误: {str(e)}')

if __name__ == '__main__':
    test_feishu_connection()