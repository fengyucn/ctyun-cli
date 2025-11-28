"""
统一身份认证(IAM)命令行接口
"""

import click
from typing import Optional
from iam import IAMClient
from utils import OutputFormatter


def handle_error(func):
    """错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import sys
            click.echo(f"错误: {e}", err=True)
            sys.exit(1)
    return wrapper


def format_output(data, output_format='table'):
    """格式化输出"""
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
            import sys
            sys.exit(1)
    else:
        if isinstance(data, list) and data:
            headers = list(data[0].keys())
            table = OutputFormatter.format_table(data, headers)
            click.echo(table)
        elif isinstance(data, dict):
            headers = ['字段', '值']
            table_data = [[key, value] for key, value in data.items()]
            table = OutputFormatter.format_table(table_data, headers)
            click.echo(table)
        else:
            click.echo(data)


@click.group()
def iam():
    """统一身份认证(IAM)管理"""
    pass


@iam.command('list-projects')
@click.option('--account-id', required=True, help='账号ID')
@click.option('--page', default=1, type=int, help='当前页，默认1')
@click.option('--page-size', default=10, type=int, help='每页显示条数，默认10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_projects(ctx, account_id: str, page: int, page_size: int, output: Optional[str]):
    """查询企业项目列表"""
    try:
        client = ctx.obj['client']
        output_format = output or ctx.obj.get('output', 'table')
        
        iam_client = IAMClient(client)
        result = iam_client.list_enterprise_projects(
            account_id=account_id,
            current_page=page,
            page_size=page_size
        )
        
        if result.get('statusCode') != '800':
            error_msg = result.get('message', '未知错误')
            error_code = result.get('error', '')
            click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
            import sys
            sys.exit(1)
        
        return_obj = result.get('returnObj', {})
        record_list = return_obj.get('recordList', [])
        
        if output_format in ['json', 'yaml']:
            format_output(record_list, output_format)
        else:
            if record_list:
                from tabulate import tabulate
                from datetime import datetime
                
                table_data = []
                headers = ['项目ID', '项目名称', '状态', '描述', '创建时间']
                
                status_map = {
                    1: '启用',
                    0: '停用'
                }
                
                for project in record_list:
                    create_time = project.get('createTime', '')
                    if isinstance(create_time, int):
                        try:
                            create_time = datetime.fromtimestamp(create_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            create_time = str(create_time)
                    
                    status = project.get('status', 0)
                    status_text = status_map.get(status, str(status))
                    
                    description = project.get('description', '')
                    if len(description) > 40:
                        description = description[:37] + '...'
                    
                    table_data.append([
                        project.get('id', ''),
                        project.get('projectName', ''),
                        status_text,
                        description,
                        create_time
                    ])
                
                current_page = return_obj.get('currentPage', 1)
                page_count = return_obj.get('pageCount', 1)
                record_count = return_obj.get('recordCount', 0)
                
                click.echo(f"\n企业项目列表 (总计: {record_count} 个, 第{current_page}/{page_count}页)\n")
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(table)
                
                if current_page < page_count:
                    click.echo(f"\n提示: 使用 --page 参数查看其他页")
            else:
                click.echo("未找到企业项目")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@iam.command('get-project')
@click.option('--project-id', required=True, help='企业项目ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_project(ctx, project_id: str, output: Optional[str]):
    """查询企业项目详情"""
    try:
        client = ctx.obj['client']
        output_format = output or ctx.obj.get('output', 'table')

        iam_client = IAMClient(client)
        result = iam_client.get_enterprise_project(project_id=project_id)

        if result.get('statusCode') != '800':
            error_msg = result.get('message', '未知错误')
            error_code = result.get('error', '')
            click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
            import sys
            sys.exit(1)

        project = result.get('returnObj', {})

        if output_format in ['json', 'yaml']:
            format_output(project, output_format)
        else:
            if project:
                from datetime import datetime

                status_map = {
                    1: '启用',
                    0: '停用'
                }

                create_time = project.get('createTime', '')
                if isinstance(create_time, int):
                    try:
                        create_time = datetime.fromtimestamp(create_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        create_time = str(create_time)

                status = project.get('status', 0)
                status_text = status_map.get(status, str(status))

                click.echo(f"\n企业项目详情")
                click.echo("=" * 80)
                click.echo(f"项目ID: {project.get('id', '')}")
                click.echo(f"项目名称: {project.get('projectName', '')}")
                click.echo(f"状态: {status_text}")
                click.echo(f"华为项目ID: {project.get('hwProjectId', '')}")
                click.echo(f"描述: {project.get('description', '')}")
                click.echo(f"创建时间: {create_time}")
                click.echo("=" * 80)
            else:
                click.echo("未找到企业项目")

    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@iam.command('list-resources')
@click.option('--project-set-id', required=True, help='企业项目ID')
@click.option('--page', default=1, type=int, help='当前页，默认1')
@click.option('--page-size', default=10, type=int, help='每页显示条数，默认10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_resources(ctx, project_set_id: str, page: int, page_size: int, output: Optional[str]):
    """分页查询资源信息"""
    try:
        client = ctx.obj['client']
        output_format = output or ctx.obj.get('output', 'table')

        iam_client = IAMClient(client)
        result = iam_client.list_resources(
            project_set_id=project_set_id,
            page_num=page,
            page_size=page_size
        )

        if result.get('statusCode') != '800':
            error_msg = result.get('message', '未知错误')
            error_code = result.get('error', '')
            click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
            import sys
            sys.exit(1)

        return_obj = result.get('returnObj', {})
        record_list = return_obj.get('recordList', [])

        if output_format in ['json', 'yaml']:
            format_output(record_list, output_format)
        else:
            if record_list:
                from tabulate import tabulate

                table_data = []
                headers = ['账号ID', '企业项目ID', '资源ID', '资源名称', '产品名称', '资源类型', '服务Tag', '区域ID', '包周期', '规格代码']

                # 预处理资源列表数据
                processed_records = []
                for record in record_list:
                    if isinstance(record, str):
                        import json
                        try:
                            record = json.loads(record)
                        except:
                            continue
                    processed_records.append(record)

                for resource in processed_records:
                    account_id = resource.get('accountId', '')
                    project_set_id = resource.get('projectSetId', '')
                    resource_id = resource.get('resourceId', '')
                    resource_name = resource.get('resourceName', '')
                    product_name = resource.get('productName', '')
                    resource_type = resource.get('resourceType', '')
                    service_tag = resource.get('serviceTag', '')
                    region_id = resource.get('regionId', '')
                    resource_spec_code = resource.get('resourceSpecCode', '')

                    # 处理包周期信息
                    is_cycle = resource.get('isCycle', 0)
                    cycle_text = '是' if is_cycle == 1 else '否'

                    # 截断过长的字段
                    if len(resource_name) > 25:
                        resource_name = resource_name[:22] + '...'
                    if len(product_name) > 15:
                        product_name = product_name[:12] + '...'
                    if len(resource_type) > 15:
                        resource_type = resource_type[:12] + '...'
                    if len(resource_spec_code) > 15:
                        resource_spec_code = resource_spec_code[:12] + '...'

                    # 显示简化的账号ID和项目ID
                    if len(account_id) > 8:
                        account_id_short = account_id[:4] + '...' + account_id[-4:]
                    else:
                        account_id_short = account_id

                    if len(project_set_id) > 8:
                        project_set_id_short = project_set_id[:4] + '...' + project_set_id[-4:]
                    else:
                        project_set_id_short = project_set_id

                    table_data.append([
                        account_id_short,
                        project_set_id_short,
                        resource_id[:15] + '...' if len(resource_id) > 15 else resource_id,
                        resource_name,
                        product_name,
                        resource_type,
                        service_tag,
                        region_id,
                        cycle_text,
                        resource_spec_code
                    ])

                current_page = return_obj.get('pageNum', 1)
                total_pages = return_obj.get('pages', 1)
                total_count = return_obj.get('total', 0)

                click.echo(f"\n资源信息列表 (总计: {total_count} 个, 第{current_page}/{total_pages}页)\n")
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(table)

                if current_page < total_pages:
                    click.echo(f"\n提示: 使用 --page 参数查看其他页")
            else:
                click.echo("未找到资源信息")

    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()
