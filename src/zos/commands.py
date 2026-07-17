"""对象存储(ZOS)命令行接口"""

import click
import sys
from typing import Optional
from utils import OutputFormatter


@click.group()
def zos():
    """对象存储(ZOS)管理"""
    pass


def format_zos_output(result, output_format='table'):
    """格式化ZOS查询结果输出"""
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(result))
        return
    if output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
            sys.exit(1)
        return
    if result.get('statusCode') != 800:
        msg = result.get('description') or result.get('message', '未知错误')
        click.echo(f"❌ 查询失败: {msg}", err=True)
        sys.exit(1)
    return_obj = result.get('returnObj', {}) or {}
    if isinstance(return_obj, list):
        click.echo(OutputFormatter.format_table(return_obj, list(return_obj[0].keys()) if return_obj else []))
    elif isinstance(return_obj, dict):
        if any(isinstance(v, (list, dict)) for v in return_obj.values()):
            click.echo(OutputFormatter.format_json(return_obj))
        else:
            table_data = [[k, v] for k, v in return_obj.items()]
            click.echo(OutputFormatter.format_table(table_data, ['字段', '值']))
    else:
        click.echo(return_obj)


# ==================== 桶查询命令 ====================


@zos.command('list-buckets')
@click.option('--region-id', required=True, help='区域ID。传public返回所有公共资源池的桶')
@click.option('--project-id', help='企业项目ID，多个用逗号分隔')
@click.option('--page-size', type=int, help='页大小，默认10，范围1~50')
@click.option('--page-no', type=int, help='页码，默认1')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def list_buckets(ctx, region_id, project_id, page_size, page_no, output):
    """查询所有桶"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).list_buckets(
        region_id=region_id, project_id=project_id,
        page_size=page_size, page_no=page_no,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-bucket-info')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='存储桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_bucket_info(ctx, region_id, bucket, output):
    """查询桶信息"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_bucket_info(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-bucket-location')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_bucket_location(ctx, region_id, bucket, output):
    """查询桶位置信息"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_bucket_location(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-bucket-statistics')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--start-time', required=True, help='开始时间(日期-小时, UTC时区)')
@click.option('--end-time', required=True, help='结束时间(日期-小时, UTC时区)')
@click.option('--bucket', help='存储桶名(可选)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_bucket_statistics(ctx, region_id, start_time, end_time, bucket, output):
    """查询桶统计信息"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_bucket_statistics(
        region_id, start_time, end_time, bucket=bucket,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('head-bucket')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def head_bucket(ctx, region_id, bucket, output):
    """查询桶访问权限"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).head_bucket(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-bucket-versioning')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_bucket_versioning(ctx, region_id, bucket, output):
    """查询桶版本控制配置"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_bucket_versioning(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-bucket-tagging')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_bucket_tagging(ctx, region_id, bucket, output):
    """查询桶标签"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_bucket_tagging(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-bucket-policy')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_bucket_policy(ctx, region_id, bucket, output):
    """查询桶策略"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_bucket_policy(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-bucket-encryption')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_bucket_encryption(ctx, region_id, bucket, output):
    """查询桶的加密配置"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_bucket_encryption(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-bucket-logging')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_bucket_logging(ctx, region_id, bucket, output):
    """查询桶日志转存配置"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_bucket_logging(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-bucket-lifecycle')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_bucket_lifecycle(ctx, region_id, bucket, output):
    """查询桶生命周期配置"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_bucket_lifecycle(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-object-num')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='存储桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_object_num(ctx, region_id, bucket, output):
    """查询对象桶对象数量(不含碎片)"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_object_num(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-fragment-num')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='存储桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_fragment_num(ctx, region_id, bucket, output):
    """查询对象桶碎片数量"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_fragment_num(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-bucket-acl')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_bucket_acl(ctx, region_id, bucket, output):
    """获取桶ACL"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_bucket_acl(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-object-lock-conf')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_object_lock_conf(ctx, region_id, bucket, output):
    """获取桶的合规保留策略"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_object_lock_conf(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


# ==================== 对象查询命令 ====================


@zos.command('list-objects')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--delimiter', help='定界符，用来对键进行分组的字符')
@click.option('--marker', help='从哪个对象开始列出')
@click.option('--max-keys', type=int, help='一次返回keys的最大数目(默认和上限1000)')
@click.option('--prefix', help='返回key的前缀')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def list_objects(ctx, region_id, bucket, delimiter, marker, max_keys, prefix, output):
    """查看对象列表"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).list_objects(
        region_id, bucket, delimiter=delimiter, marker=marker,
        max_keys=max_keys, prefix=prefix,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('list-object-versions')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--key-marker', help='从哪个键之后开始列出')
@click.option('--prefix', help='返回key的前缀')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def list_object_versions(ctx, region_id, bucket, key_marker, prefix, output):
    """查询对象版本信息"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).list_object_versions(
        region_id, bucket, key_marker=key_marker, prefix=prefix,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('head-object')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--key', required=True, help='对象名')
@click.option('--version-id', help='版本ID(开启多版本时可使用)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def head_object(ctx, region_id, bucket, key, version_id, output):
    """查询对象是否存在"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).head_object(
        region_id, bucket, key, version_id=version_id,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-object-tagging')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--key', required=True, help='对象名')
@click.option('--version-id', help='版本ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_object_tagging(ctx, region_id, bucket, key, version_id, output):
    """查询对象标签"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_object_tagging(
        region_id, bucket, key, version_id=version_id,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-object-acl')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--key', required=True, help='对象名')
@click.option('--version-id', help='版本ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_object_acl(ctx, region_id, bucket, key, version_id, output):
    """获取对象ACL"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_object_acl(
        region_id, bucket, key, version_id=version_id,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-object-retention')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--key', required=True, help='对象名称')
@click.option('--version-id', required=True, help='版本ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_object_retention(ctx, region_id, bucket, key, version_id, output):
    """获取对象保留期限配置"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_object_retention(
        region_id, bucket, key, version_id,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('list-all-parts')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--page', type=int, help='页码，默认1')
@click.option('--page-size', type=int, help='每页展示最大分段数量(1~50)，默认10')
@click.option('--page-no', type=int, help='页码(若与page同时存在以pageNo为准)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def list_all_parts(ctx, region_id, bucket, page, page_size, page_no, output):
    """查询桶内碎片列表"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).list_all_parts(
        region_id, bucket, page=page, page_size=page_size, page_no=page_no,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('list-multipart-uploads')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--key-marker', help='键标记')
@click.option('--upload-id-marker', help='uploadID标记(仅设置了keyMarker时有效)')
@click.option('--max-uploads', type=int, help='单次最多返回的分段上传数据(1-1000)')
@click.option('--prefix', help='Key的前缀')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def list_multipart_uploads(ctx, region_id, bucket, key_marker, upload_id_marker,
                           max_uploads, prefix, output):
    """查询正在进行中的分段上传"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).list_multipart_uploads(
        region_id, bucket, key_marker=key_marker, upload_id_marker=upload_id_marker,
        max_uploads=max_uploads, prefix=prefix,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('list-parts')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--key', required=True, help='对象名')
@click.option('--upload-id', required=True, help='uploadID')
@click.option('--max-parts', type=int, help='返回最大分块数(默认和上限1000)')
@click.option('--part-number-marker', type=int, help='列表开始位置(列出比此编号更高的分块)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def list_parts(ctx, region_id, bucket, key, upload_id, max_parts, part_number_marker, output):
    """列出上传对象的全部分段"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).list_parts(
        region_id, bucket, key, upload_id,
        max_parts=max_parts, part_number_marker=part_number_marker,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('list-migration-failed-detail')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--migration-id', required=True, help='迁移任务ID')
@click.option('--page-size', type=int, help='页大小(1~50)，默认10')
@click.option('--page-no', type=int, help='页码，默认1')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def list_migration_failed_detail(ctx, region_id, migration_id, page_size, page_no, output):
    """查询迁移任务的失败对象列表"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).list_migration_failed_detail(
        region_id, migration_id, page_size=page_size, page_no=page_no,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-endpoint')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_endpoint(ctx, region_id, output):
    """查询访问控制endpoint"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_endpoint(region_id)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


# ==================== 权限/资源池查询命令 ====================


@zos.command('get-keys')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_keys(ctx, region_id, output):
    """查询ACCESS_KEY以及SECRET_KEY"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_keys(region_id)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('list-roles')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--keyword', help='模糊查询角色名(不区分大小写)')
@click.option('--page-size', type=int, help='单页数量(1~50)，默认10')
@click.option('--page', type=int, help='页码(若与pageNo同时存在以pageNo为准)')
@click.option('--page-no', type=int, help='页码，默认1')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def list_roles(ctx, region_id, keyword, page_size, page, page_no, output):
    """查询角色列表"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).list_roles(
        region_id, keyword=keyword, page_size=page_size, page=page, page_no=page_no,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-role-detail')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--role-name', required=True, help='角色名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_role_detail(ctx, region_id, role_name, output):
    """查询角色详情"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_role_detail(region_id, role_name)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('list-policies')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--keyword', help='模糊查询策略名(不区分大小写)')
@click.option('--page-size', type=int, help='单页数量(1~50)，默认10')
@click.option('--page', type=int, help='页码(若与pageNo同时存在以pageNo为准)')
@click.option('--page-no', type=int, help='页码，默认1')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def list_policies(ctx, region_id, keyword, page_size, page, page_no, output):
    """查询策略列表"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).list_policies(
        region_id, keyword=keyword, page_size=page_size, page=page, page_no=page_no,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-policy-detail')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--policy-name', required=True, help='策略名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_policy_detail(ctx, region_id, policy_name, output):
    """查询策略详情"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_policy_detail(region_id, policy_name)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('list-regions')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def list_regions(ctx, output):
    """查询所有对象存储资源池"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).list_regions()
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


# ==================== 服务管理查询命令 ====================


@zos.command('get-service-status')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_service_status(ctx, region_id, output):
    """查询对象存储开通状态"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_oss_service_status(region_id)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('get-user-event-bridge')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def get_user_event_bridge(ctx, region_id, output):
    """获取对象存储用户级事件总线状态"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).get_user_event_bridge(region_id)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


# ==================== 标签管理命令 ====================


def _parse_tags(tag_options):
    """将 --tag key=value 列表解析为 [{key, value}, ...]"""
    tags = []
    for t in tag_options:
        if '=' not in t:
            click.echo(f"错误: 标签格式应为 key=value，收到: {t}", err=True)
            sys.exit(1)
        k, v = t.split('=', 1)
        tags.append({'key': k, 'value': v})
    return tags


@zos.command('put-bucket-tagging')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--tag', multiple=True, required=True,
              help='标签键值对(格式 key=value，可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def put_bucket_tagging(ctx, region_id, bucket, tag, output):
    """设置桶标签"""
    from zos.client import ZOSClient
    tags = _parse_tags(tag)
    result = ZOSClient(client=ctx.obj['client']).put_bucket_tagging(region_id, bucket, tags)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('put-object-tagging')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--key', required=True, help='对象名')
@click.option('--version-id', help='版本ID')
@click.option('--tag', multiple=True, required=True,
              help='标签键值对(格式 key=value，可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def put_object_tagging(ctx, region_id, bucket, key, version_id, tag, output):
    """设置对象标签"""
    from zos.client import ZOSClient
    tags = _parse_tags(tag)
    result = ZOSClient(client=ctx.obj['client']).put_object_tagging(
        region_id, bucket, key, tags, version_id=version_id,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('delete-bucket-tagging')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def delete_bucket_tagging(ctx, region_id, bucket, output):
    """删除桶标签"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).delete_bucket_tagging(region_id, bucket)
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('delete-object-tagging')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bucket', required=True, help='桶名')
@click.option('--key', required=True, help='对象名')
@click.option('--version-id', help='版本ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def delete_object_tagging(ctx, region_id, bucket, key, version_id, output):
    """删除对象标签"""
    from zos.client import ZOSClient
    result = ZOSClient(client=ctx.obj['client']).delete_object_tagging(
        region_id, bucket, key, version_id=version_id,
    )
    format_zos_output(result, output or ctx.obj.get('output', 'table'))


@zos.command('query-price')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--pkg-type', required=True,
              type=click.Choice(['zosSize', 'zosMzSize', 'zosBytesSend',
                                 'zosRequest', 'zosRetrievalFlow', 'zosRetrievalFrequency']),
              help='资源包类型。zosSize=存储空间包, zosMzSize=多AZ存储空间包, '
                   'zosBytesSend=流出流量包, zosRequest=请求次数包, '
                   'zosRetrievalFlow=数据取回流量包, zosRetrievalFrequency=数据取回次数包')
@click.option('--pkg-spec-type', required=True,
              type=click.Choice(['fixed', 'defined']),
              help='资源包规格类型。fixed=固定规格, defined=自定义规格')
@click.option('--pkg-spec', required=True, type=int,
              help='资源包规格大小(GB)，请求次数包和数据取回次数包单位为万次')
@click.option('--cycle-cnt', required=True, type=int,
              help='订购周期 (month:1-36, year:1-3)')
@click.option('--cycle-type', required=True,
              type=click.Choice(['month', 'year']),
              help='订购周期类型 month(月) / year(年)')
@click.option('--order-num', required=True, type=int,
              help='订购数量(最大50)')
@click.option('--storage-class', required=True,
              type=click.Choice(['STANDARD', 'STANDARD_IA', 'GLACIER']),
              help='存储类型。STANDARD=标准存储, STANDARD_IA=低频存储, GLACIER=归档存储')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def query_price(ctx, region_id: str, pkg_type: str, pkg_spec_type: str,
                pkg_spec: int, cycle_cnt: int, cycle_type: str,
                order_num: int, storage_class: str, output: Optional[str]):
    """询价ZOS资源包"""
    from zos.client import ZOSClient

    client = ctx.obj['client']
    zos_client = ZOSClient(client)

    result = zos_client.query_resource_package_price(
        region_id=region_id,
        pkg_type=pkg_type,
        pkg_spec_type=pkg_spec_type,
        pkg_spec=pkg_spec,
        cycle_cnt=cycle_cnt,
        cycle_type=cycle_type,
        order_num=order_num,
        storage_class=storage_class,
    )

    output_format = output or ctx.obj.get('output', 'table')

    if output_format == 'json':
        click.echo(OutputFormatter.format_json(result))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
    else:
        if result.get('statusCode') != 800:
            error_msg = result.get('description') or result.get('message', '未知错误')
            click.echo(f"❌ 询价失败: {error_msg}", err=True)
            sys.exit(1)

        return_obj = result.get('returnObj', {}) or {}
        total_price = return_obj.get('totalPrice', '-')
        discount_price = return_obj.get('discountPrice', '-')
        final_price = return_obj.get('finalPrice', '-')
        sub_orders = return_obj.get('subOrderPrices', [])

        pkg_type_names = {
            'zosSize': 'ZOS存储空间包', 'zosMzSize': 'ZOS多AZ存储空间包',
            'zosBytesSend': 'ZOS流出流量包', 'zosRequest': 'ZOS请求次数包',
            'zosRetrievalFlow': 'ZOS数据取回流量包', 'zosRetrievalFrequency': 'ZOS数据取回次数包'
        }

        click.echo("=" * 60)
        click.echo(f"ZOS资源包询价  {pkg_type_names.get(pkg_type, pkg_type)}")
        click.echo("=" * 60)
        click.echo(f"  {'规格':<14}: {pkg_spec} ({pkg_spec_type})")
        click.echo(f"  {'存储类型':<14}: {storage_class}")
        click.echo(f"  {'订购周期':<14}: {cycle_cnt}{cycle_type} x {order_num}")
        click.echo(f"  {'总价 (CNY)':<14}: {total_price}")
        click.echo(f"  {'折后价 (CNY)':<14}: {discount_price}")
        click.echo(f"  {'最终价 (CNY)':<14}: {final_price}")

        if sub_orders:
            click.echo("\n子订单明细:")
            click.echo("-" * 60)
            for sub in sub_orders:
                click.echo(f"  服务标签: {sub.get('serviceTag', '-')}  "
                           f"总价: {sub.get('totalPrice', '-')}  "
                           f"最终价: {sub.get('finalPrice', '-')} CNY")
                for item in sub.get('orderItemPrices', []):
                    click.echo(f"    [{item.get('resourceType', '-')}] "
                               f"套数: {item.get('instanceCnt', '-')}  "
                               f"总价: {item.get('totalPrice', '-')}  "
                               f"最终价: {item.get('finalPrice', '-')} CNY")
