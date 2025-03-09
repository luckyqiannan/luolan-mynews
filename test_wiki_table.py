import requests
import json
import os
from config import Config

def test_wiki_table():
    """测试访问wiki中的表格"""
    # 获取配置
    config = Config()
    app_id = config.FEISHU_APP_ID
    app_secret = config.FEISHU_APP_SECRET
    base_id = config.BASE_ID  # 这应该是wiki空间ID
    table_id = config.TABLE_ID  # 这应该是表格ID
    
    print(f'使用的配置:\nAPP_ID: {app_id}\nBASE_ID: {base_id}\nTABLE_ID: {table_id}')
    
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
        
        # 尝试解析URL中的信息
        print("\n测试分解URL中的信息:")
        url_parts = "https://axigl4dmvb.feishu.cn/wiki/UhkYwpijYifSEckJKdkcILFrnmg?table=tbl0eSf2q4qcd2ny&view=vewSlwvklQ"
        print(f'完整URL: {url_parts}')
        
        # 从URL中提取wiki_id和table_id
        import re
        wiki_id_match = re.search(r'/wiki/([^?]+)', url_parts)
        table_id_match = re.search(r'table=([^&]+)', url_parts)
        
        if wiki_id_match and table_id_match:
            wiki_id = wiki_id_match.group(1)
            table_id_from_url = table_id_match.group(1)
            print(f'从URL解析: wiki_id={wiki_id}, table_id={table_id_from_url}')
        else:
            print('无法从URL解析出wiki_id和table_id')
            wiki_id = base_id
            table_id_from_url = table_id
        
        # 尝试多种不同的API端点
        
        # 1. 尝试直接访问wiki页面
        print("\n尝试1: 访问wiki页面")
        wiki_url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/{wiki_id}/nodes"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        wiki_response = requests.get(wiki_url, headers=headers)
        print(f'Wiki页面访问状态: {wiki_response.status_code}')
        print(f'响应内容: {wiki_response.text[:300]}')
        
        # 2. 尝试访问文档中的表格
        print("\n尝试2: 访问文档中的表格 - bitableId路径")
        doc_table_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{wiki_id}/tables/{table_id_from_url}/records"
        
        doc_table_response = requests.get(doc_table_url, headers=headers)
        print(f'文档表格访问状态: {doc_table_response.status_code}')
        print(f'响应内容: {doc_table_response.text[:300]}')
        
        # 3. 尝试新的API路径 - 先获取bitableId
        print("\n尝试3: 先获取bitableId")
        # 访问文档元数据
        metadata_url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/{wiki_id}/nodes/{wiki_id}"
        
        metadata_response = requests.get(metadata_url, headers=headers)
        print(f'元数据访问状态: {metadata_response.status_code}')
        print(f'响应内容: {metadata_response.text[:300]}')
        
        # 4. 尝试使用不同的API版本
        print("\n尝试4: 使用bitableId作为BASE_ID")
        # 假设wiki页面本身就有一个bitableId
        bitable_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{table_id_from_url}/tables"
        
        bitable_response = requests.get(bitable_url, headers=headers)
        print(f'Bitable访问状态: {bitable_response.status_code}')
        print(f'响应内容: {bitable_response.text[:300]}')
        
        # 5. 使用文档API
        print("\n尝试5: 使用文档API")
        doc_url = f"https://open.feishu.cn/open-apis/doc/v2/documents/{wiki_id}"
        
        doc_response = requests.get(doc_url, headers=headers)
        print(f'文档API访问状态: {doc_response.status_code}')
        print(f'响应内容: {doc_response.text[:300]}')
        
        # 6. 尝试直接使用表格ID
        print("\n尝试6: 直接使用表格ID")
        direct_table_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{table_id_from_url}"
        
        direct_table_response = requests.get(direct_table_url, headers=headers)
        print(f'直接表格访问状态: {direct_table_response.status_code}')
        print(f'响应内容: {direct_table_response.text[:300]}')
        
    except Exception as e:
        print(f'发生错误: {str(e)}')
        
    print("\n可能的解决方案:")
    print("1. 从飞书多维表格的桌面客户端或网页端直接复制API可用的链接")
    print("2. 检查飞书开发者文档中关于wiki表格的访问方式")
    print("3. 尝试将多维表格从wiki中导出为独立的多维表格应用")

if __name__ == '__main__':
    test_wiki_table()
