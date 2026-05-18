"""
镜像管理服务 (IMS) CLI命令
"""

import json
from typing import Optional

import click

from core import CTYUNClient
from utils import OutputFormatter

from .client import IMSClient


def format_output(data, output_format='table'):
    """格式化输出"""
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("请安装 PyYAML: pip install PyYAML", err=True)
            click.echo(json.dumps(data, ensure_ascii=False, indent=2))


def _get_ims_client(ctx) -> IMSClient:
    """获取 IMSClient 实例"""
    if 'ims_client' not in ctx.obj:
        client: CTYUNClient = ctx.obj['client']
        ctx.obj['ims_client'] = IMSClient(client)
    return ctx.obj['ims_client']


# ========== 命令组 ==========

@click.group()
def ims():
    """镜像管理服务"""
    pass


# ========== 查询可以使用的镜像资源 ==========

@ims.command('list-available')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--az-name', help='可用区名称（仅多可用区资源池下物理机镜像）')
@click.option('--cwai-type', type=click.Choice(['control', 'node']),
              help='云骁智算云主机节点类型（仅公共镜像时生效）')
@click.option('--flavor-name', help='规格名称，如 s7.small.1')
@click.option('--image-name', help='镜像名称（仅私有镜像时生效）')
@click.option('--image-scene', type=click.Choice(['dev', 'ecommerce', 'gaming', 'website']),
              help='镜像场景（仅应用镜像时生效）')
@click.option('--image-status', type=click.Choice(['accepted', 'rejected', 'waiting']),
              help='镜像状态（仅共享镜像时生效）')
@click.option('--image-subcategory', type=click.Choice(['app', 'thin_app']),
              help='镜像子种类（仅应用镜像时生效）')
@click.option('--image-type', type=click.Choice(['data_disk_image', 'others']),
              help='镜像类型（仅私有镜像时生效）')
@click.option('--image-visibility-code', type=int,
              help='镜像可见类型代码：0=私有, 1=公共, 2=共享, 5=应用镜像')
@click.option('--os-type-code', type=click.Choice(['1', '2']),
              help='操作系统类型代码：1=Linux, 2=Windows（共享镜像时不生效）')
@click.option('--page-no', type=int, default=1, help='页码（默认1）')
@click.option('--page-size', type=int, default=10, help='每页数量（默认10，最大200）')
@click.option('--project-id', help='企业项目ID（仅私有镜像时生效）')
@click.option('--query-content', help='查询内容，支持模糊查询')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_available(ctx, region_id: str, az_name: Optional[str],
                   cwai_type: Optional[str], flavor_name: Optional[str],
                   image_name: Optional[str], image_scene: Optional[str],
                   image_status: Optional[str], image_subcategory: Optional[str],
                   image_type: Optional[str], image_visibility_code: Optional[int],
                   os_type_code: Optional[str], page_no: int, page_size: int,
                   project_id: Optional[str], query_content: Optional[str],
                   output: Optional[str]):
    """查询可以使用的镜像资源"""
    client = _get_ims_client(ctx)
    result = client.list_available_images(
        region_id=region_id,
        az_name=az_name,
        cwai_type=cwai_type,
        flavor_name=flavor_name,
        image_name=image_name,
        image_scene=image_scene,
        image_status=image_status,
        image_subcategory=image_subcategory,
        image_type=image_type,
        image_visibility_code=image_visibility_code,
        os_type_code=int(os_type_code) if os_type_code else None,
        page_no=page_no,
        page_size=page_size,
        project_id=project_id,
        query_content=query_content
    )
    if result.get('statusCode') not in (0, '0', 800):
        click.echo(f"错误: {result.get('message', '未知错误')}", err=True)
        return
    return_obj = result.get('returnObj', {})
    if output in ('json', 'yaml'):
        format_output(result, output)
    else:
        images = return_obj.get('images', [])
        total = return_obj.get('totalCount', 0)
        current_page = return_obj.get('currentPage', 1)
        total_page = return_obj.get('totalPage', 1)
        click.echo(f"可用镜像列表 (总计 {total} 条, 第 {current_page}/{total_page} 页)")
        click.echo("=" * 120)
        if images:
            for idx, img in enumerate(images, 1):
                click.echo(f"\n{idx}. 镜像ID: {img.get('imageID', 'N/A')}")
                click.echo(f"   名称: {img.get('imageName', 'N/A')}")
                display_name = img.get('imageDisplayName')
                if display_name:
                    click.echo(f"   展示名称: {display_name}")
                click.echo(f"   类别: {img.get('imageCategory', 'N/A')} / {img.get('imageClass', 'N/A')}")
                click.echo(f"   状态: {img.get('imageStatus', 'N/A')}")
                click.echo(f"   可见性: {img.get('imageVisibility', 'N/A')}")
                click.echo(f"   架构: {img.get('architecture', 'N/A')}")
                click.echo(f"   系统: {img.get('osDistro', 'N/A')} {img.get('osVersion', '')} ({img.get('osType', '')})")
                click.echo(f"   磁盘: {img.get('diskFormat', 'N/A')} / {img.get('diskSize', 'N/A')} GiB")
                image_size = img.get('imageSize', 0)
                if image_size:
                    click.echo(f"   大小: {image_size / 1024 / 1024 / 1024:.1f} GiB")
                click.echo(f"   创建时间: {img.get('createdTimeStr', 'N/A')}")
        else:
            click.echo("\n无可用镜像")


# ========== 查询镜像详细信息 ==========

@ims.command('describe')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--image-id', required=True, help='镜像ID')
@click.option('--error-free', is_flag=True, default=False,
              help='期望"零错误"响应（已弃用，不推荐使用）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def describe_image(ctx, region_id: str, image_id: str, error_free: bool, output: Optional[str]):
    """查询镜像详细信息"""
    client = _get_ims_client(ctx)
    result = client.get_image_detail(
        region_id=region_id,
        image_id=image_id,
        error_free=error_free if error_free else None
    )
    if result.get('statusCode') not in (0, '0', 800):
        click.echo(f"错误: {result.get('message', '未知错误')}", err=True)
        return
    return_obj = result.get('returnObj', {})
    images = return_obj.get('images', [])
    if output in ('json', 'yaml'):
        format_output(result, output)
    else:
        if images:
            img = images[0]
            click.echo("镜像详细信息")
            click.echo("=" * 80)
            click.echo(f"  镜像ID: {img.get('imageID', 'N/A')}")
            click.echo(f"  名称: {img.get('imageName', 'N/A')}")
            display_name = img.get('imageDisplayName')
            if display_name:
                click.echo(f"  展示名称: {display_name}")
            click.echo(f"  描述: {img.get('description', 'N/A')}")
            click.echo(f"  镜像类别: {img.get('imageClass', 'N/A')}")
            click.echo(f"  子类别: {img.get('imageSubcategory', 'N/A')}")
            click.echo(f"  状态: {img.get('imageStatus', 'N/A')}")
            click.echo(f"  可见性: {img.get('imageVisibility', 'N/A')}")
            click.echo(f"  架构: {img.get('architecture', 'N/A')}")
            boot_mode = img.get('bootMode')
            if boot_mode:
                click.echo(f"  启动方式: {boot_mode}")
            click.echo(f"  系统: {img.get('osDistro', 'N/A')} {img.get('osVersion', '')} ({img.get('osType', '')})")
            click.echo(f"  磁盘格式: {img.get('diskFormat', 'N/A')}")
            click.echo(f"  磁盘容量: {img.get('diskSize', 'N/A')} GiB")
            image_size = img.get('imageSize', 0)
            if image_size:
                click.echo(f"  镜像大小: {image_size / 1024 / 1024 / 1024:.1f} GiB")
            chargeable = img.get('chargeableImage')
            if chargeable is not None:
                click.echo(f"  收费镜像: {'是' if chargeable else '否'}")
            source = img.get('imageSource')
            if source:
                click.echo(f"  来源: {source}")
            source_server = img.get('sourceServerID')
            if source_server:
                click.echo(f"  源服务器: {source_server}")
            disk_id = img.get('diskID')
            if disk_id:
                click.echo(f"  来源磁盘: {disk_id}")
            click.echo(f"  创建时间: {img.get('createdTimeStr', 'N/A')}")
            click.echo(f"  更新时间: {img.get('updatedTimeStr', 'N/A')}")
            share_count = img.get('imageShareCount')
            if share_count is not None:
                click.echo(f"  共享次数: {share_count}")
        else:
            click.echo("未找到镜像信息")
