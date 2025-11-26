"""
云硬盘(EBS)命令行接口
"""

import click
from typing import Optional
from ebs import EBSClient
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
def ebs():
    """云硬盘(EBS)管理"""
    pass


@ebs.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=10, type=int, help='每页数量，默认10，最大300')
@click.option('--az-name', help='可用区')
@click.option('--project-id', help='企业项目ID')
@click.option('--disk-type', help='云硬盘类型（SATA/SAS/SSD/FAST-SSD）')
@click.option('--disk-mode', help='云硬盘模式（VBD/ISCSI/FCSAN）')
@click.option('--disk-status', help='云硬盘状态（in-use/available等）')
@click.option('--multi-attach', help='是否共享盘（true/false）')
@click.option('--is-system-volume', help='是否系统盘（true/false）')
@click.option('--is-encrypt', help='是否加密盘（true/false）')
@click.option('--query-content', help='模糊查询内容')
@click.option('--query-keys', help='模糊查询键（name,diskID,instanceID,instanceName）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_ebs(ctx, region_id: str, page: int, page_size: int,
             az_name: Optional[str], project_id: Optional[str],
             disk_type: Optional[str], disk_mode: Optional[str],
             disk_status: Optional[str], multi_attach: Optional[str],
             is_system_volume: Optional[str], is_encrypt: Optional[str],
             query_content: Optional[str], query_keys: Optional[str],
             output: Optional[str]):
    """查询云硬盘列表"""
    try:
        client = ctx.obj['client']
        output_format = output or ctx.obj.get('output', 'table')
        
        ebs_client = EBSClient(client)
        result = ebs_client.list_ebs(
            region_id=region_id,
            page_no=page,
            page_size=page_size,
            az_name=az_name,
            project_id=project_id,
            disk_type=disk_type,
            disk_mode=disk_mode,
            disk_status=disk_status,
            multi_attach=multi_attach,
            is_system_volume=is_system_volume,
            is_encrypt=is_encrypt,
            query_content=query_content,
            query_keys=query_keys
        )
        
        if result.get('statusCode') != 800:
            error_msg = result.get('message', '未知错误')
            click.echo(f"❌ 查询失败: {error_msg}", err=True)
            import sys
            sys.exit(1)
        
        return_obj = result.get('returnObj', {})
        disk_list = return_obj.get('diskList', [])
        
        if output_format in ['json', 'yaml']:
            format_output(disk_list, output_format)
        else:
            if disk_list:
                from tabulate import tabulate
                from datetime import datetime
                
                table_data = []
                headers = ['云硬盘ID', '名称', '大小(GB)', '类型', '状态', '挂载主机', '创建时间']
                
                for disk in disk_list:
                    disk_id = disk.get('diskID', '')
                    disk_name = disk.get('diskName', '')
                    disk_size = disk.get('diskSize', 0)
                    disk_type = disk.get('diskType', '')
                    disk_status = disk.get('diskStatus', '')
                    instance_name = disk.get('instanceName', '-')
                    
                    create_time = disk.get('createTime', 0)
                    if isinstance(create_time, int) and create_time > 0:
                        try:
                            create_time = datetime.fromtimestamp(create_time / 1000).strftime('%Y-%m-%d %H:%M')
                        except:
                            create_time = str(create_time)
                    else:
                        create_time = '-'
                    
                    table_data.append([
                        disk_id,
                        disk_name,
                        disk_size,
                        disk_type,
                        disk_status,
                        instance_name,
                        create_time
                    ])
                
                total_count = return_obj.get('totalCount', 0)
                current_count = return_obj.get('currentCount', len(disk_list))
                total_page = return_obj.get('totalPage', 1)
                
                click.echo(f"\n云硬盘列表 (总计: {total_count} 个, 当前页: {current_count} 个, 第{page}/{total_page}页)\n")
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(table)
                
                if page < total_page:
                    click.echo(f"\n提示: 使用 --page 参数查看其他页")
            else:
                click.echo("未找到云硬盘")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()
