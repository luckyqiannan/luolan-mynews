import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # 飞书应用配置
    FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', 'cli_a74fdb29e66f500b')
    FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', 'cjymplvV5bihFBINCnNEEfB6cxUNR1SK')
    
    # 多维表格配置 - 使用新的链接参数
    # 原始URL: https://axigl4dmvb.feishu.cn/base/NxsdbqFV2a5Y7AsrTt4cQh5rnac?table=tbl3UvhF6vQDpOW3&view=vewSlwvklQ
    BASE_ID = os.getenv('BASE_ID', 'NxsdbqFV2a5Y7AsrTt4cQh5rnac')
    TABLE_ID = os.getenv('TABLE_ID', 'tbl3UvhF6vQDpOW3')
    
    # Flask应用配置
    SECRET_KEY = os.urandom(24)
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300