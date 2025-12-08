#!/usr/bin/env python3
"""
解析天翼云API文档抓取结果，提取详细的API信息
"""

import json
import re
from bs4 import BeautifulSoup

def parse_api_documentation():
    """解析抓取的API文档HTML文件"""

    try:
        # 读取抓取的JSON数据
        with open('api_documentation_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"解析API文档: {data['title']}")
        print(f"URL: {data['url']}")
        print("="*80)

        # 显示表格信息
        if data.get('tables'):
            print("\n📋 API参数信息:")
            for i, table in enumerate(data['tables']):
                if i == 0:
                    print(f"\n🔹 路径参数:")
                    headers = table['headers']
                    print(f"   {'参数':<20} {'必填':<6} {'类型':<10} {'说明'}")
                    print("   " + "-"*70)

                    for row in table['rows']:
                        param = row[0] if len(row) > 0 else ""
                        required = row[1] if len(row) > 1 else ""
                        param_type = row[2] if len(row) > 2 else ""
                        description = row[3] if len(row) > 3 else ""
                        print(f"   {param:<20} {required:<6} {param_type:<10} {description}")

                elif i == 1:
                    print(f"\n🔹 请求参数:")
                    headers = table['headers']
                    print(f"   {'参数':<15} {'必填':<6} {'类型':<10} {'说明'}")
                    print("   " + "-"*80)

                    for row in table['rows']:
                        param = row[0] if len(row) > 0 else ""
                        required = row[1] if len(row) > 1 else ""
                        param_type = row[2] if len(row) > 2 else ""
                        description = row[3] if len(row) > 3 else ""
                        example = row[4] if len(row) > 4 else ""
                        print(f"   {param:<15} {required:<6} {param_type:<10} {description}")
                        if example:
                            print(f"   {'':15} {'':6} {'':10} 示例: {example}")

                elif i == 2:
                    print(f"\n🔹 响应参数:")
                    headers = table['headers']
                    print(f"   {'参数':<15} {'类型':<10} {'说明'}")
                    print("   " + "-"*70)

                    for row in table['rows']:
                        param = row[0] if len(row) > 0 else ""
                        param_type = row[1] if len(row) > 1 else ""
                        description = row[2] if len(row) > 2 else ""
                        example = row[3] if len(row) > 3 else ""
                        print(f"   {param:<15} {param_type:<10} {description}")
                        if example:
                            print(f"   {'':15} {'':10} 示例: {example}")

        # 尝试解析HTML获取更多信息
        try:
            with open('api_documentation.html', 'r', encoding='utf-8') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # 查找API基本信息
            print(f"\n📖 详细信息:")

            # 查找API描述
            api_desc = soup.find('div', class_='api-description') or soup.find('div', class_='description')
            if api_desc:
                desc_text = api_desc.get_text(strip=True)
                print(f"   描述: {desc_text}")

            # 查找请求方法
            method_elements = soup.find_all(class_=re.compile(r'method|request|http'))
            for elem in method_elements:
                method_text = elem.get_text(strip=True)
                if re.search(r'GET|POST|PUT|DELETE|PATCH', method_text, re.IGNORECASE):
                    print(f"   请求方法: {method_text}")

            # 查找端点URL
            url_elements = soup.find_all(class_=re.compile(r'url|endpoint|path'))
            for elem in url_elements:
                url_text = elem.get_text(strip=True)
                if url_text.startswith('/') or 'ctapi.ctyun.cn' in url_text:
                    print(f"   API端点: {url_text}")

        except Exception as e:
            print(f"HTML解析失败: {e}")

        # 生成API使用示例
        print(f"\n🔧 API使用示例:")
        print(f"   GET /v1.1/cce/clusters/{{clusterId}}/namespaces/{{namespaceName}}/pods/{{podName}}")
        print(f"   Header: regionId=200000001852")
        print(f"   需要参数:")
        print(f"     - clusterId: 集群ID")
        print(f"     - namespaceName: 命名空间名称")
        print(f"     - podName: Pod名称")
        print(f"     - regionId: 资源池ID (如: 200000001852)")

        print(f"\n📝 响应格式:")
        print(f"   {")
        print(f"     \"statusCode\": 800,")
        print(f"     \"message\": \"success\",")
        print(f"     \"returnObj\": \"Pod详细信息\",")
        print(f"     \"requestId\": \"请求ID\"")
        print(f"   }")

        print(f"\n✅ 抓取完成!")
        print(f"   📄 完整数据: api_documentation_data.json")
        print(f"   🌐 页面截图: api_documentation_screenshot.png")
        print(f"   📜 HTML源码: api_documentation.html")

        return data

    except FileNotFoundError:
        print("❌ 错误: 未找到抓取的数据文件")
        print("   请先运行 scrape_api_doc.py 进行抓取")
        return None
    except Exception as e:
        print(f"❌ 解析过程中发生错误: {e}")
        return None

if __name__ == "__main__":
    result = parse_api_documentation()

    if result:
        # 生成简化版的API文档
        simplified_doc = {
            "api_name": "查询Pod",
            "api_endpoint": "/v1.1/cce/clusters/{clusterId}/namespaces/{namespaceName}/pods/{podName}",
            "http_method": "GET",
            "parameters": {
                "path_params": [
                    {"name": "clusterId", "type": "String", "required": True, "description": "集群ID"},
                    {"name": "namespaceName", "type": "String", "required": True, "description": "命名空间名称"},
                    {"name": "podName", "type": "String", "required": True, "description": "Pod名称"}
                ],
                "header_params": [
                    {"name": "regionId", "type": "String", "required": True, "description": "资源池ID", "example": "200000001852"}
                ]
            },
            "response": {
                "success_code": 800,
                "response_format": {
                    "statusCode": "Integer",
                    "message": "String",
                    "returnObj": "String",
                    "requestId": "String",
                    "error": "String"
                }
            },
            "source_url": result.get('url', '')
        }

        # 保存简化版文档
        with open('api_summary.json', 'w', encoding='utf-8') as f:
            json.dump(simplified_doc, f, ensure_ascii=False, indent=2)

        print(f"\n📋 已生成简化版API文档: api_summary.json")