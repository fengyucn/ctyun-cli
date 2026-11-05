"""容器镜像服务(SWR)命令行接口"""

import click

from swr.client import SWRClient
from utils import OutputFormatter


def _format_output(data, output_format):
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
            raise SystemExit(1)
    else:
        if isinstance(data, list) and data:
            headers = list(data[0].keys())
            click.echo(OutputFormatter.format_table(data, headers))
        else:
            click.echo("没有数据")


@click.group()
def swr():
    """容器镜像服务(SWR)管理"""
    pass


# 实例状态字典（文档：CREATING 开通中 / CREATE_FAILED 开通失败 / RUNNING 运行中 ...）
_INSTANCE_STATE = {
    'CREATING': '开通中',
    'CREATE_FAILED': '开通失败',
    'RUNNING': '运行中',
    'EXPANDING': '变配中',
    'STOPPED': '已停用',
    'DELETING': '删除中',
    'UNSUBSCRIBED': '已退订'
}

_INSTANCE_TYPE = {
    'personal': '个人版',
    'enterprise-basic': '企业版'
}


def _fail(result):
    """输出错误详情（含错误码）"""
    message = result.get('message') or '未知错误'
    error = result.get('error')
    if error and error not in ('000000', ''):
        click.echo(f"查询失败 [{error}]: {message}", err=True)
    else:
        click.echo(f"查询失败: {message}", err=True)


_STORAGE_STATE = {
    'SUCCESS': '生效中/变更成功',
    'PENDING': '等待变更中',
    'RUNNING': '变更中',
    'FAILED': '变更失败'
}


def _paged_list(result, output_format, title, headers, mapper, page_num=1):
    """渲染分页列表（returnObj.records）"""
    ro = result.get('returnObj') or {}
    records = ro.get('records') or []
    if output_format != 'table':
        _format_output(records, output_format)
        return
    if not records:
        click.echo(f"{title}: 没有数据")
        return
    rows = [mapper(r) for r in records if isinstance(r, dict)]
    click.echo(f"\n{title} (共 {ro.get('total', len(records))} 条, "
               f"第 {ro.get('current', page_num)}/{ro.get('pages', 1)} 页)\n")
    click.echo(OutputFormatter.format_table(rows, headers))


def _detail_table(data, output_format, pairs):
    """渲染详情（pairs: [(中文标签, 字段名), ...]）"""
    if output_format != 'table':
        _format_output(data, output_format)
        return
    rows = [{'字段': label, '值': data.get(key, '')} for label, key in pairs]
    click.echo(OutputFormatter.format_table(rows, ['字段', '值']))


@swr.command('list-instances')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-name', help='实例名称（包含匹配）')
@click.option('--all-region', is_flag=True, help='查询所有资源池的实例')
@click.option('--page-num', type=int, default=1, help='页码（默认1）')
@click.option('--page-size', type=int, default=50, help='每页数量（默认50）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_instances(ctx, region_id: str, instance_name: str, all_region: bool,
                   page_num: int, page_size: int, output: str):
    """查询镜像实例列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).list_instances(
        region_id, instance_name, all_region, page_num, page_size)
    if result.get('statusCode') != 800:
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return
    records = (result.get('returnObj') or {}).get('records', [])
    total = (result.get('returnObj') or {}).get('total', len(records))
    if output_format == 'table':
        click.echo(f"SWR实例列表 (共 {total} 个，第 {page_num} 页):")
    _format_output(records, output_format)


@swr.command('list-repositories')
@click.option('--region-id', required=True, help='实例所属资源池ID（取实例列表返回的region）')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--page-num', type=int, default=1, help='页码（默认1）')
@click.option('--page-size', type=int, default=50, help='每页数量（默认50）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_repositories(ctx, region_id: str, instance_id: str,
                      page_num: int, page_size: int, output: str):
    """查询镜像仓库列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).list_repositories(
        region_id, instance_id, page_num, page_size)
    if result.get('statusCode') != 800:
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return
    records = (result.get('returnObj') or {}).get('records', [])
    total = (result.get('returnObj') or {}).get('total', len(records))
    if output_format == 'table':
        click.echo(f"SWR镜像仓库列表 (共 {total} 个，第 {page_num} 页):")
    _format_output(records, output_format)


@swr.command('get-instance')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_instance(ctx, region_id: str, instance_id: str, output: str):
    """查询实例详情"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).get_instance(region_id, instance_id)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    detail = result.get('returnObj') or {}
    if not detail:
        click.echo("未查询到实例详情")
        return
    if output_format != 'table':
        _format_output(detail, output_format)
        return
    instance_type = detail.get('instanceType', '')
    state = detail.get('state', '')
    rows = [
        {'字段': '实例ID', '值': detail.get('instanceId', '')},
        {'字段': '实例名称', '值': detail.get('instanceName', '')},
        {'字段': '实例类型', '值': _INSTANCE_TYPE.get(instance_type, instance_type)},
        {'字段': '用户名', '值': detail.get('userName', '')},
        {'字段': '企业项目', '值': detail.get('enterpriseProjectName', '')},
        {'字段': '资源池编码', '值': detail.get('region', '')},
        {'字段': '资源池名称', '值': detail.get('regionName', '')},
        {'字段': '公网访问地址', '值': detail.get('publicAddress', '')},
        {'字段': '内网访问地址', '值': detail.get('internalAddress', '')},
        {'字段': 'Chart地址', '值': detail.get('chartAddress', '')},
        {'字段': '访问协议', '值': detail.get('protocol', '')},
        {'字段': '计费模式', '值': detail.get('billMode', '')},
        {'字段': '实例状态', '值': _INSTANCE_STATE.get(state, state)},
        {'字段': '过期时间', '值': detail.get('expirationTime', '')},
        {'字段': '开通时间', '值': detail.get('createdTime', '')}
    ]
    click.echo("\n镜像实例详情\n")
    click.echo(OutputFormatter.format_table(rows, ['字段', '值']))


@swr.command('get-instance-usage')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_instance_usage(ctx, region_id: str, instance_id: str, output: str):
    """查询实例配额"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).get_instance_usage(region_id, instance_id)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    usage = result.get('returnObj') or []
    if isinstance(usage, dict):
        usage = [usage]
    if not usage:
        click.echo("未查询到实例配额")
        return
    if output_format != 'table':
        _format_output(usage, output_format)
        return
    rows = [{
        '实例ID': item.get('instanceId', ''),
        '命名空间配额': item.get('namespaceQuota', ''),
        '已用命名空间': item.get('namespaceUsed', ''),
        '仓库配额': item.get('repositoryQuota', ''),
        '已用仓库': item.get('repositoryUsed', ''),
        '存储配额': item.get('storageQuota', ''),
        '存储使用量': item.get('storageUsed', '')
    } for item in usage if isinstance(item, dict)]
    click.echo("\n镜像实例配额\n")
    click.echo(OutputFormatter.format_table(
        rows, ['实例ID', '命名空间配额', '已用命名空间', '仓库配额', '已用仓库',
               '存储配额', '存储使用量']))


@swr.command('list-instance-regions')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_instance_regions(ctx, region_id: str, output: str):
    """查询实例Region列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).list_instance_regions(region_id)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    regions = result.get('returnObj') or []
    if isinstance(regions, dict):
        regions = [regions]
    if not regions:
        click.echo("未查询到资源池列表")
        return
    if output_format != 'table':
        _format_output(regions, output_format)
        return
    rows = [{
        '资源池编码': r.get('regionId') or r.get('region', ''),
        '资源池代码': r.get('regionCode', ''),
        '资源池名称': r.get('regionName', '')
    } for r in regions if isinstance(r, dict)]
    click.echo(f"\n镜像实例资源池列表 (共 {len(rows)} 个)\n")
    click.echo(OutputFormatter.format_table(rows, ['资源池编码', '资源池代码', '资源池名称']))


@swr.command('get-instance-count')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--all-region', is_flag=True, help='统计所有资源池的实例')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_instance_count(ctx, region_id: str, all_region: bool, output: str):
    """查询用户实例个数"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).get_instance_count(region_id, all_region)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    count = result.get('returnObj')
    if output_format != 'table':
        _format_output(count, output_format)
        return
    scope = '全部资源池' if all_region else '当前资源池'
    click.echo(f"SWR 实例个数（{scope}）: {count}")


@swr.command('get-storage-config')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_storage_config(ctx, region_id: str, instance_id: str, output: str):
    """查询对象存储配置"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).get_storage_config(region_id, instance_id)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    data = result.get('returnObj') or {}
    if output_format == 'table':
        data = dict(data)
        state = data.get('state')
        if state:
            data['state'] = _STORAGE_STATE.get(state, state)
        click.echo("\n对象存储配置\n")
    _detail_table(data, output_format, [
        ('对象存储 Bucket', 'ossBucket'),
        ('对象存储 AccessKey', 'ossAccessKey'),
        ('委托模式', 'isDelegate'),
        ('配置状态', 'state')
    ])


@swr.command('list-namespaces')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--namespace-name', help='命名空间名称（模糊搜索）')
@click.option('--page-num', type=int, default=1, help='页码（默认1）')
@click.option('--page-size', type=int, default=10, help='每页条数（默认10，最大50）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_namespaces(ctx, region_id, instance_id, namespace_name,
                    page_num, page_size, output):
    """查询镜像命名空间列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).list_namespaces(
        region_id, instance_id, namespace_name, page_num, page_size)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    _paged_list(result, output_format, '镜像命名空间列表',
                ['命名空间', '命名空间ID', '仓库数', '推送自动建仓', '默认公开', '镜像加速', '创建时间'],
                lambda r: {
                    '命名空间': r.get('namespaceName', ''),
                    '命名空间ID': r.get('namespaceId', ''),
                    '仓库数': r.get('repositoryCount', ''),
                    '推送自动建仓': r.get('createRepoAuto', ''),
                    '默认公开': r.get('defaultRepoPublic', ''),
                    '镜像加速': r.get('accelerate', ''),
                    '创建时间': r.get('createdTime', '')
                }, page_num)


@swr.command('get-namespace')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--namespace-name', required=True, help='命名空间名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_namespace(ctx, region_id, instance_id, namespace_name, output):
    """查询镜像命名空间详情"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).get_namespace(region_id, instance_id, namespace_name)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    data = result.get('returnObj') or {}
    if not data:
        click.echo("未查询到命名空间")
        return
    _detail_table(data, output_format, [
        ('命名空间ID', 'namespaceId'),
        ('命名空间名称', 'namespaceName'),
        ('仓库数目', 'repositoryCount'),
        ('推送自动建仓', 'createRepoAuto'),
        ('默认公开', 'defaultRepoPublic'),
        ('镜像加速', 'accelerate'),
        ('创建时间', 'createdTime'),
        ('修改时间', 'modifiedTime')
    ])


@swr.command('get-repository')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--repository-id', required=True, help='镜像仓库ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_repository(ctx, region_id, instance_id, repository_id, output):
    """查询镜像仓库详情"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).get_repository(region_id, instance_id, repository_id)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    data = result.get('returnObj') or {}
    if not data:
        click.echo("未查询到镜像仓库")
        return
    _detail_table(data, output_format, [
        ('仓库ID', 'repositoryId'),
        ('命名空间', 'namespaceName'),
        ('仓库名称', 'repositoryName'),
        ('是否公开', 'isPublic'),
        ('镜像加速', 'accelerate'),
        ('资源池编码', 'regionId'),
        ('说明', 'description'),
        ('创建时间', 'createdTime'),
        ('修改时间', 'modifiedTime')
    ])


@swr.command('list-tags')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--repository-id', required=True, help='镜像仓库ID')
@click.option('--tag-name', help='镜像版本 Tag')
@click.option('--page-num', type=int, default=1, help='页码（默认1）')
@click.option('--page-size', type=int, default=10, help='每页条数（默认10，最大50）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_tags(ctx, region_id, instance_id, repository_id, tag_name,
              page_num, page_size, output):
    """查询镜像版本(Tag)列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).list_repo_tags(
        region_id, instance_id, repository_id, tag_name, page_num, page_size)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    _paged_list(result, output_format, '镜像版本列表',
                ['Tag', '架构', '操作系统', '大小', '推送时间', '摘要'],
                lambda r: {
                    'Tag': r.get('name', ''),
                    '架构': r.get('architecture', ''),
                    '操作系统': r.get('os', ''),
                    '大小': r.get('size', ''),
                    '推送时间': r.get('push_time', ''),
                    '摘要': r.get('digest', '')
                }, page_num)


@swr.command('get-tag')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--repository-id', required=True, help='镜像仓库ID')
@click.option('--tag-name', required=True, help='镜像版本 Tag')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_tag(ctx, region_id, instance_id, repository_id, tag_name, output):
    """查询指定版本镜像"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).get_repo_tag(
        region_id, instance_id, repository_id, tag_name)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    data = result.get('returnObj') or {}
    if not data:
        click.echo("未查询到镜像版本")
        return
    _detail_table(data, output_format, [
        ('Tag', 'name'),
        ('摘要', 'digest'),
        ('架构', 'architecture'),
        ('操作系统', 'os'),
        ('大小', 'size'),
        ('作者', 'author'),
        ('创建时间', 'created'),
        ('最近拉取', 'pull_time'),
        ('最近推送', 'push_time')
    ])


@swr.command('list-artifacts')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--repository-id', required=True, help='镜像仓库ID')
@click.option('--page-num', type=int, default=1, help='页码（默认1）')
@click.option('--page-size', type=int, default=10, help='每页条数（默认10，最大50）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_artifacts(ctx, region_id, instance_id, repository_id,
                   page_num, page_size, output):
    """查询制品列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).list_artifacts(
        region_id, instance_id, repository_id, page_num, page_size)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    _paged_list(result, output_format, '制品列表',
                ['制品ID', '类型', '大小', '推送时间', 'digest'],
                lambda r: {
                    '制品ID': r.get('id', ''),
                    '类型': r.get('type', ''),
                    '大小': r.get('size', ''),
                    '推送时间': r.get('push_time', ''),
                    'digest': r.get('digest', '')
                }, page_num)


@swr.command('get-artifact')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--repository-id', required=True, help='镜像仓库ID')
@click.option('--reference', required=True, help='制品 digest 或 tag')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_artifact(ctx, region_id, instance_id, repository_id, reference, output):
    """查询制品详情"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).get_artifact(
        region_id, instance_id, repository_id, reference)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    data = result.get('returnObj') or {}
    if not data:
        click.echo("未查询到制品")
        return
    _detail_table(data, output_format, [
        ('制品ID', 'id'),
        ('digest', 'digest'),
        ('命名空间', 'namespaceName'),
        ('仓库名称', 'repositoryName'),
        ('制品类型', 'type'),
        ('大小', 'size'),
        ('media_type', 'media_type'),
        ('manifest_media_type', 'manifest_media_type'),
        ('最近拉取', 'pull_time'),
        ('最近推送', 'push_time')
    ])


@swr.command('list-chart-namespaces')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--namespace-name', help='命名空间名称（模糊搜索）')
@click.option('--page-num', type=int, default=1, help='页码（默认1）')
@click.option('--page-size', type=int, default=10, help='每页条数（默认10，最大50）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_chart_namespaces(ctx, region_id, instance_id, namespace_name,
                          page_num, page_size, output):
    """查询HelmChart命名空间列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).list_chart_namespaces(
        region_id, instance_id, namespace_name, page_num, page_size)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    _paged_list(result, output_format, 'Chart 命名空间列表',
                ['命名空间', '命名空间ID', '仓库数', '推送自动建仓', '默认公开', '创建时间'],
                lambda r: {
                    '命名空间': r.get('namespaceName', ''),
                    '命名空间ID': r.get('namespaceId', ''),
                    '仓库数': r.get('repositoryCount', ''),
                    '推送自动建仓': r.get('createRepoAuto', ''),
                    '默认公开': r.get('defaultRepoPublic', ''),
                    '创建时间': r.get('createdTime', '')
                }, page_num)


@swr.command('get-chart-namespace')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--namespace-name', required=True, help='命名空间名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_chart_namespace(ctx, region_id, instance_id, namespace_name, output):
    """查询HelmChart命名空间详情"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).get_chart_namespace(
        region_id, instance_id, namespace_name)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    data = result.get('returnObj') or {}
    if not data:
        click.echo("未查询到 Chart 命名空间")
        return
    _detail_table(data, output_format, [
        ('命名空间ID', 'namespaceId'),
        ('命名空间名称', 'namespaceName'),
        ('仓库数目', 'repositoryCount'),
        ('推送自动建仓', 'createRepoAuto'),
        ('默认公开', 'defaultRepoPublic'),
        ('创建时间', 'createdTime'),
        ('修改时间', 'modifiedTime')
    ])


@swr.command('list-chart-repositories')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--namespace-name', help='命名空间名称')
@click.option('--repository-name', help='Chart 仓库名称（模糊搜索）')
@click.option('--page-num', type=int, default=1, help='页码（默认1）')
@click.option('--page-size', type=int, default=10, help='每页条数（默认10，最大50）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_chart_repositories(ctx, region_id, instance_id, namespace_name,
                            repository_name, page_num, page_size, output):
    """查询Chart仓库列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).list_chart_repositories(
        region_id, instance_id, namespace_name, repository_name, page_num, page_size)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    _paged_list(result, output_format, 'Chart 仓库列表',
                ['仓库ID', '命名空间', '仓库名称', '是否公开', '创建时间', '修改时间'],
                lambda r: {
                    '仓库ID': r.get('repositoryId', ''),
                    '命名空间': r.get('namespaceName', ''),
                    '仓库名称': r.get('repositoryName', ''),
                    '是否公开': r.get('isPublic', ''),
                    '创建时间': r.get('createdTime', ''),
                    '修改时间': r.get('modifiedTime', '')
                }, page_num)


@swr.command('list-chart-tags')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--repository-id', required=True, help='Chart 仓库ID')
@click.option('--tag-name', help='Chart 版本 Tag')
@click.option('--page-num', type=int, default=1, help='页码（默认1）')
@click.option('--page-size', type=int, default=10, help='每页条数（默认10，最大50）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_chart_tags(ctx, region_id, instance_id, repository_id, tag_name,
                    page_num, page_size, output):
    """查询Chart版本列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).list_chart_tags(
        region_id, instance_id, repository_id, tag_name, page_num, page_size)
    if result.get('statusCode') != 800:
        _fail(result)
        return
    _paged_list(result, output_format, 'Chart 版本列表',
                ['版本', '大小', '说明', '推送时间', '摘要'],
                lambda r: {
                    '版本': r.get('name', ''),
                    '大小': r.get('size', ''),
                    '说明': r.get('description', ''),
                    '推送时间': r.get('push_time', ''),
                    '摘要': r.get('digest', '')
                }, page_num)
