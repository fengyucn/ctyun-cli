"""
统一身份认证(IAM)命令行接口
"""

import click
from typing import Optional, List
from iam import IAMClient
from utils import OutputFormatter


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
        click.echo(OutputFormatter.format_json(data))


def format_table(data, headers, title=None):
    """表格输出"""
    if not data:
        click.echo("无数据")
        return
    from tabulate import tabulate
    if title:
        click.echo(f"\n{title}\n")
    click.echo(tabulate(data, headers=headers, tablefmt='grid'))


def get_client(ctx):
    """获取IAM客户端实例"""
    client = ctx.obj['client']
    return IAMClient(client)


def check_result(result):
    """检查API返回结果，成功返回returnObj，失败返回None"""
    if result.get('statusCode') != '800':
        error_msg = result.get('message', '未知错误')
        error_code = result.get('error', '')
        click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    return result.get('returnObj', {})


@click.group()
def iam():
    """统一身份认证(IAM)管理"""
    pass


# ==================== 企业项目管理 (3 existing) ====================

@iam.command('list-projects')
@click.option('--account-id', required=True, help='账号ID')
@click.option('--page', default=1, type=int, help='当前页，默认1')
@click.option('--page-size', default=10, type=int, help='每页显示条数，默认10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_projects(ctx, account_id: str, page: int, page_size: int, output: Optional[str]):
    """查询企业项目列表"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_enterprise_projects(
        account_id=account_id, current_page=page, page_size=page_size
    )
    return_obj = check_result(result)
    record_list = return_obj.get('recordList', [])

    if output_format in ['json', 'yaml']:
        format_output(record_list, output_format)
    else:
        if record_list:
            from datetime import datetime
            table_data = []
            headers = ['项目ID', '项目名称', '状态', '描述', '创建时间']
            status_map = {1: '启用', 0: '停用'}
            for p in record_list:
                ct = p.get('createTime', '')
                if isinstance(ct, int):
                    try:
                        ct = datetime.fromtimestamp(ct / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        ct = str(ct)
                desc = p.get('description', '')
                table_data.append([
                    p.get('id', ''), p.get('projectName', ''),
                    status_map.get(p.get('status', 0), str(p.get('status', 0))),
                    desc, ct
                ])
            cur = return_obj.get('currentPage', 1)
            total_p = return_obj.get('pageCount', 1)
            total = return_obj.get('recordCount', 0)
            format_table(table_data, headers,
                         f"企业项目列表 (总计: {total} 个, 第{cur}/{total_p}页)")
        else:
            click.echo("未找到企业项目")


@iam.command('get-project')
@click.option('--project-id', required=True, help='企业项目ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_project(ctx, project_id: str, output: Optional[str]):
    """查询企业项目详情"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.get_enterprise_project(project_id=project_id)
    project = check_result(result)

    if output_format in ['json', 'yaml']:
        format_output(project, output_format)
    else:
        if project:
            from datetime import datetime
            ct = project.get('createTime', '')
            if isinstance(ct, int):
                try:
                    ct = datetime.fromtimestamp(ct / 1000).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    ct = str(ct)
            status_map = {1: '启用', 0: '停用'}
            click.echo(f"\n企业项目详情")
            click.echo("=" * 60)
            click.echo(f"项目ID: {project.get('id', '')}")
            click.echo(f"项目名称: {project.get('projectName', '')}")
            click.echo(f"状态: {status_map.get(project.get('status', 0), str(project.get('status', 0)))}")
            click.echo(f"华为项目ID: {project.get('hwProjectId', '')}")
            click.echo(f"描述: {project.get('description', '')}")
            click.echo(f"创建时间: {ct}")
            click.echo("=" * 60)
        else:
            click.echo("未找到企业项目")


@iam.command('list-resources')
@click.option('--project-set-id', required=True, help='企业项目ID')
@click.option('--page', default=1, type=int, help='当前页，默认1')
@click.option('--page-size', default=10, type=int, help='每页显示条数，默认10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_resources(ctx, project_set_id: str, page: int, page_size: int, output: Optional[str]):
    """分页查询资源信息"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_resources(
        project_set_id=project_set_id, page_num=page, page_size=page_size
    )
    return_obj = check_result(result)
    record_list = return_obj.get('recordList', [])

    if output_format in ['json', 'yaml']:
        format_output(record_list, output_format)
    else:
        if record_list:
            table_data = []
            headers = ['账号ID', '企业项目ID', '资源ID', '资源名称', '产品名称',
                       '资源类型', '服务Tag', '区域ID', '包周期', '规格代码']
            processed = []
            for r in record_list:
                if isinstance(r, str):
                    import json as j
                    try:
                        r = j.loads(r)
                    except Exception:
                        continue
                processed.append(r)
            for r in processed:
                aid = r.get('accountId', '')
                pid = r.get('projectSetId', '')
                table_data.append([
                    aid[:8] + '...' if len(aid) > 8 else aid,
                    pid[:8] + '...' if len(pid) > 8 else pid,
                    r.get('resourceId', '')[:15] + '...' if len(r.get('resourceId', '')) > 15 else r.get('resourceId', ''),
                    r.get('resourceName', ''),
                    r.get('productName', ''),
                    r.get('resourceType', ''),
                    r.get('serviceTag', ''),
                    r.get('regionId', ''),
                    '是' if r.get('isCycle') == 1 else '否',
                    r.get('resourceSpecCode', '')
                ])
            cur = return_obj.get('pageNum', 1)
            total_p = return_obj.get('pages', 1)
            total = return_obj.get('total', 0)
            format_table(table_data, headers,
                         f"资源信息列表 (总计: {total} 个, 第{cur}/{total_p}页)")
        else:
            click.echo("未找到资源信息")


# ==================== 用户管理 ====================

@iam.command('query-login-config')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def query_login_config(ctx, user_id: str, output: Optional[str]):
    """用户登录设置_查询配置"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.query_login_config(user_id=user_id)
    return_obj = check_result(result)
    if output_format in ['json', 'yaml']:
        format_output(return_obj, output_format)
    else:
        authen_code = return_obj.get('authenCode', '')
        desc = '下次登录必须重置密码' if authen_code == '10001' else '无需重置密码'
        click.echo(f"登录认证配置:")
        click.echo(f"  authenCode: {authen_code} ({desc})")


@iam.command('get-user')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_user(ctx, user_id: str, output: Optional[str]):
    """根据id查询用户详情"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.get_user_detail(user_id=user_id)
    user = check_result(result)
    if output_format in ['json', 'yaml']:
        format_output(user, output_format)
    else:
        if user:
            click.echo(f"\n用户详情")
            click.echo("=" * 60)
            click.echo(f"用户名: {user.get('userName', '')}")
            click.echo(f"登录名: {user.get('loginName', '')}")
            click.echo(f"邮箱: {user.get('loginEmail', '')}")
            click.echo(f"手机号: {user.get('mobilePhone', '')}")
            click.echo(f"账号ID: {user.get('accountId', '')}")
            click.echo(f"描述: {user.get('remark', '')}")
            click.echo(f"虚拟邮箱: {user.get('virtualEmail', '')}")
            click.echo(f"用户昵称: {user.get('userNickName', '')}")
            groups = user.get('groups', [])
            if groups:
                click.echo(f"用户组: {', '.join([g.get('id', '') for g in groups])}")
            click.echo("=" * 60)
        else:
            click.echo("未找到用户")


@iam.command('list-users')
@click.option('--page', default=1, type=int, help='页数，默认1')
@click.option('--page-size', default=10, type=int, help='每页条数，默认10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_users(ctx, page: int, page_size: int, output: Optional[str]):
    """分页查询用户"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_users(page_num=page, page_size=page_size)
    return_obj = check_result(result)
    user_list = return_obj.get('result', [])

    if output_format in ['json', 'yaml']:
        format_output(user_list, output_format)
    else:
        if user_list:
            table_data = []
            headers = ['用户ID', '用户名', '邮箱', '手机号', '描述', '是否主用户', '状态']
            for u in user_list:
                is_root = '是' if u.get('isRoot') == '1' or u.get('isRoot') == 1 else '否'
                prohibit = '禁用' if u.get('prohibit') == 1 else '启用'
                table_data.append([
                    u.get('userId', ''), u.get('userName', ''),
                    u.get('loginEmail', ''), u.get('mobilePhone', ''),
                    u.get('remark', ''), is_root, prohibit
                ])
            total = return_obj.get('total', 0)
            pages_n = return_obj.get('pages', 1)
            format_table(table_data, headers,
                         f"用户列表 (总计: {total} 个, 第{page}/{pages_n}页)")
        else:
            click.echo("未找到用户")


@iam.command('query-access-control')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def query_access_control(ctx, user_id: str, output: Optional[str]):
    """查询控制台和api编程式访问配置"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.query_access_control(user_id=user_id)
    return_obj = check_result(result)
    if output_format in ['json', 'yaml']:
        format_output(return_obj, output_format)
    else:
        disabled = return_obj.get('disableLoginPortal', '')
        desc = '已禁用登录' if disabled == 'PUB_100_02_0001' else '未禁用登录'
        click.echo(f"访问控制配置:")
        click.echo(f"  disableLoginPortal: {disabled} ({desc})")


# ==================== 用户组管理 ====================

@iam.command('get-group')
@click.option('--group-id', required=True, help='用户组ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_group(ctx, group_id: str, output: Optional[str]):
    """根据用户组ID查询用户组信息"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.get_group_info(group_id=group_id)
    group = check_result(result)
    if output_format in ['json', 'yaml']:
        format_output(group, output_format)
    else:
        if group:
            from datetime import datetime
            ct = group.get('createTime', '')
            if isinstance(ct, int):
                try:
                    ct = datetime.fromtimestamp(ct / 1000).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    ct = str(ct)
            click.echo(f"\n用户组信息")
            click.echo("=" * 60)
            click.echo(f"用户组ID: {group.get('id', '')}")
            click.echo(f"用户组名称: {group.get('groupName', '')}")
            click.echo(f"账号ID: {group.get('accountId', '')}")
            click.echo(f"描述: {group.get('groupIntro', '')}")
            click.echo(f"华为组ID: {group.get('hwGroupId', '')}")
            click.echo(f"创建时间: {ct}")
            click.echo("=" * 60)
        else:
            click.echo("未找到用户组")


@iam.command('list-group-users')
@click.option('--group-id', required=True, multiple=True, help='用户组ID（可重复）')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=10, type=int, help='每页条数，默认10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_group_users(ctx, group_id: List[str], page: int, page_size: int,
                     output: Optional[str]):
    """分页查询用户组下的用户"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_group_users(
        page_num=page, page_size=page_size, group_ids=list(group_id)
    )
    return_obj = check_result(result)
    user_list = return_obj.get('result', [])

    if output_format in ['json', 'yaml']:
        format_output(user_list, output_format)
    else:
        if user_list:
            table_data = []
            headers = ['用户ID', '用户名', '邮箱', '手机号', '描述']
            for u in user_list:
                table_data.append([
                    u.get('userId', ''), u.get('userName', ''),
                    u.get('loginEmail', ''), u.get('mobilePhone', ''),
                    u.get('remark', '')
                ])
            total = return_obj.get('total', 0)
            pages_n = return_obj.get('pages', 1)
            format_table(table_data, headers,
                         f"用户组下用户列表 (总计: {total} 个, 第{page}/{pages_n}页)")
        else:
            click.echo("该用户组下无用户")


@iam.command('list-groups')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=10, type=int, help='每页条数，默认10')
@click.option('--group-name', help='用户组名称（可选过滤）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_groups(ctx, page: int, page_size: int, group_name: Optional[str],
                output: Optional[str]):
    """分页查询用户组"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_groups(
        page_num=page, page_size=page_size, group_name=group_name
    )
    return_obj = check_result(result)
    group_list = return_obj.get('result', [])

    if output_format in ['json', 'yaml']:
        format_output(group_list, output_format)
    else:
        if group_list:
            from datetime import datetime
            table_data = []
            headers = ['用户组ID', '名称', '描述', '用户数', '是否Root', '创建时间']
            for g in group_list:
                ct = g.get('createTime', '')
                if isinstance(ct, int):
                    try:
                        ct = datetime.fromtimestamp(ct / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        ct = str(ct)
                table_data.append([
                    g.get('id', ''), g.get('groupName', ''),
                    g.get('groupIntro', ''), g.get('userCount', ''),
                    '是' if g.get('isRoot') in ('1', 1) else '否',
                    ct
                ])
            total = return_obj.get('total', 0)
            pages_n = return_obj.get('pages', 1)
            format_table(table_data, headers,
                         f"用户组列表 (总计: {total} 个, 第{page}/{pages_n}页)")
        else:
            click.echo("未找到用户组")


# ==================== 权限管理 ====================

@iam.command('list-permissions')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=10, type=int, help='每页条数，默认10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_permissions(ctx, page: int, page_size: int, output: Optional[str]):
    """通过账户ID分页查询权限"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_permissions_by_account(
        page_num=page, page_size=page_size
    )
    return_obj = check_result(result)
    perm_list = return_obj.get('list', [])

    if output_format in ['json', 'yaml']:
        format_output(perm_list, output_format)
    else:
        if perm_list:
            table_data = []
            headers = ['权限ID', '策略名称', '策略描述', '用户组', '授权范围', '创建时间']
            for p in perm_list:
                table_data.append([
                    p.get('id', ''), p.get('policyName', ''),
                    p.get('policyDescription', ''),
                    p.get('groupName', ''), p.get('rangeType', ''),
                    p.get('createTime', '')
                ])
            total = return_obj.get('total', 0)
            pages_n = return_obj.get('pages', 1)
            format_table(table_data, headers,
                         f"权限列表 (总计: {total} 个, 第{page}/{pages_n}页)")
        else:
            click.echo("未找到权限")


@iam.command('list-user-policies')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_user_policies(ctx, user_id: str, output: Optional[str]):
    """通过用户ID查询权限"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_user_policies(user_id=user_id)
    return_obj = check_result(result)
    perm_list = return_obj.get('permissions', [])

    if output_format in ['json', 'yaml']:
        format_output(perm_list, output_format)
    else:
        if perm_list:
            table_data = []
            headers = ['权限ID', '策略名称', '策略描述', '用户组', '授权范围']
            for p in perm_list:
                table_data.append([
                    p.get('id', ''), p.get('policyName', ''),
                    p.get('policyDescription', ''),
                    p.get('groupName', ''), p.get('rangeType', '')
                ])
            format_table(table_data, headers, "用户权限列表")
        else:
            click.echo("该用户无权限")


@iam.command('list-group-policies')
@click.option('--group-id', required=True, help='用户组ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_group_policies(ctx, group_id: str, output: Optional[str]):
    """通过用户组ID查询权限"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_group_policies(group_id=group_id)
    return_obj = check_result(result)
    perm_list = return_obj.get('permissions', [])

    if output_format in ['json', 'yaml']:
        format_output(perm_list, output_format)
    else:
        if perm_list:
            table_data = []
            headers = ['权限ID', '策略名称', '策略描述', '用户组', '授权范围', '资源池']
            for p in perm_list:
                table_data.append([
                    p.get('id', ''), p.get('policyName', ''),
                    p.get('policyDescription', ''),
                    p.get('groupName', ''), p.get('rangeType', ''),
                    p.get('regionName', '')
                ])
            format_table(table_data, headers, "用户组权限列表")
        else:
            click.echo("该用户组无权限")


@iam.command('get-privilege')
@click.option('--privilege-id', required=True, help='授权策略ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_privilege(ctx, privilege_id: str, output: Optional[str]):
    """根据授权id查询授权信息"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.get_privilege_by_id(privilege_id=privilege_id)
    priv = check_result(result)
    if output_format in ['json', 'yaml']:
        format_output(priv, output_format)
    else:
        if priv:
            click.echo(f"\n授权信息")
            click.echo("=" * 60)
            click.echo(f"授权ID: {priv.get('privilegeId', '')}")
            click.echo(f"资源池ID: {priv.get('regionId', '')}")
            click.echo(f"账号ID: {priv.get('accountId', '')}")
            click.echo(f"策略ID: {priv.get('policyId', '')}")
            click.echo(f"授权主体ID: {priv.get('id', '')}")
            click.echo(f"授权类型: {priv.get('principalType', '')}")
            click.echo("=" * 60)
        else:
            click.echo("未找到授权信息")


@iam.command('list-user-own-policies')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_user_own_policies(ctx, user_id: str, output: Optional[str]):
    """查询用户自身权限"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_user_own_policies(user_id=user_id)
    return_obj = check_result(result)
    perm_list = return_obj.get('permissions', [])

    if output_format in ['json', 'yaml']:
        format_output(perm_list, output_format)
    else:
        if perm_list:
            table_data = []
            headers = ['权限ID', '策略名称', '授权范围', '资源池']
            for p in perm_list:
                table_data.append([
                    p.get('id', ''), p.get('policyName', ''),
                    p.get('rangeType', ''), p.get('regionName', '')
                ])
            format_table(table_data, headers, "用户自身权限列表")
        else:
            click.echo("该用户无自身权限")


@iam.command('list-user-inherited-policies')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_user_inherited_policies(ctx, user_id: str, output: Optional[str]):
    """查询用户继承用户组的权限"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_user_inherited_policies(user_id=user_id)
    return_obj = check_result(result)
    perm_list = return_obj.get('permissions', [])

    if output_format in ['json', 'yaml']:
        format_output(perm_list, output_format)
    else:
        if perm_list:
            table_data = []
            headers = ['权限ID', '策略名称', '策略描述', '用户组', '授权范围', '资源池']
            for p in perm_list:
                table_data.append([
                    p.get('id', ''), p.get('policyName', ''),
                    p.get('policyDescription', ''),
                    p.get('groupName', ''), p.get('rangeType', ''),
                    p.get('regionName', '')
                ])
            format_table(table_data, headers, "用户继承权限列表")
        else:
            click.echo("该用户无继承权限")


# ==================== 策略管理 ====================

@iam.command('list-policies')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=10, type=int, help='每页条数，默认10')
@click.option('--policy-type', type=int, help='策略类型 (1:系统策略, 2:自定义策略)')
@click.option('--policy-range', type=int, help='策略范围 (1:资源池, 2:全局)')
@click.option('--policy-name', help='策略名称（过滤）')
@click.option('--policy-description', help='策略描述（过滤）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_policies(ctx, page: int, page_size: int,
                  policy_type: Optional[int], policy_range: Optional[int],
                  policy_name: Optional[str], policy_description: Optional[str],
                  output: Optional[str]):
    """根据账户ID查询所有策略"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_policies(
        page_num=page, page_size=page_size,
        policy_type=policy_type, policy_range=policy_range,
        policy_name=policy_name, policy_description=policy_description
    )
    return_obj = check_result(result)
    policy_list = return_obj.get('list', [])

    if output_format in ['json', 'yaml']:
        format_output(policy_list, output_format)
    else:
        if policy_list:
            table_data = []
            headers = ['策略ID', '名称', '类型', '范围', '描述', '产品']
            for p in policy_list:
                ptype = '系统策略' if p.get('policyType') == '1' else '自定义策略' if p.get('policyType') == '2' else p.get('policyType', '')
                prange = '资源池' if p.get('policyRange') == '1' else '全局' if p.get('policyRange') == '2' else p.get('policyRange', '')
                table_data.append([
                    p.get('id', ''), p.get('policyName', ''),
                    ptype, prange,
                    p.get('policyDescription', ''), p.get('productName', '')
                ])
            total = return_obj.get('total', 0)
            pages_n = return_obj.get('pages', 1)
            format_table(table_data, headers,
                         f"策略列表 (总计: {total} 个, 第{page}/{pages_n}页)")
        else:
            click.echo("未找到策略")


@iam.command('get-policy')
@click.option('--policy-id', required=True, help='策略ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_policy(ctx, policy_id: str, output: Optional[str]):
    """查询策略详情"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.get_policy_detail(policy_id=policy_id)
    policy = check_result(result)
    if output_format in ['json', 'yaml']:
        format_output(policy, output_format)
    else:
        if policy:
            from datetime import datetime
            ct = policy.get('createTime', '')
            if isinstance(ct, int):
                try:
                    ct = datetime.fromtimestamp(ct / 1000).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    ct = str(ct)
            ptype = '系统策略' if policy.get('policyType') == 1 else '自定义策略' if policy.get('policyType') == 2 else str(policy.get('policyType', ''))
            prange = '资源池' if policy.get('policyRange') == 1 else '全局' if policy.get('policyRange') == 2 else str(policy.get('policyRange', ''))
            click.echo(f"\n策略详情")
            click.echo("=" * 60)
            click.echo(f"策略ID: {policy.get('id', '')}")
            click.echo(f"策略名称: {policy.get('policyName', '')}")
            click.echo(f"策略类型: {ptype}")
            click.echo(f"策略范围: {prange}")
            click.echo(f"描述: {policy.get('policyDescription', '')}")
            click.echo(f"策略内容: {policy.get('policyContent', '')}")
            click.echo(f"创建时间: {ct}")
            click.echo("=" * 60)
        else:
            click.echo("未找到策略")


# ==================== 委托管理 ====================

@iam.command('get-delegate-role')
@click.option('--delegate-id', required=True, help='委托ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_delegate_role(ctx, delegate_id: str, output: Optional[str]):
    """根据id查询委托角色详情"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.get_delegate_role_detail(delegate_id=delegate_id)
    role = check_result(result)
    if output_format in ['json', 'yaml']:
        format_output(role, output_format)
    else:
        if role:
            from datetime import datetime
            ct = role.get('createTime', '')
            if isinstance(ct, int):
                try:
                    ct = datetime.fromtimestamp(ct / 1000).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    ct = str(ct)
            click.echo(f"\n委托角色详情")
            click.echo("=" * 60)
            click.echo(f"委托ID: {role.get('id', '')}")
            click.echo(f"名称: {role.get('name', '')}")
            click.echo(f"账号ID: {role.get('accountId', '')}")
            click.echo(f"委托账号ID: {role.get('assumeAccountId', '')}")
            click.echo(f"委托用户ID: {role.get('assumeUserId', '')}")
            click.echo(f"类型: {role.get('type', '')}")
            click.echo(f"描述: {role.get('remark', '')}")
            click.echo(f"状态: {role.get('status', '')}")
            click.echo(f"创建时间: {ct}")
            click.echo("=" * 60)
        else:
            click.echo("未找到委托角色")


@iam.command('query-delegate-list')
@click.option('--account-id', required=True, help='账户ID')
@click.option('--service-code', help='服务编码')
@click.option('--type', 'delegate_type', type=int, help='类型 (1:云服务委托, 3:服务内联委托)')
@click.option('--name', help='委托名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def query_delegate_list(ctx, account_id: str, service_code: Optional[str],
                        delegate_type: Optional[int], name: Optional[str],
                        output: Optional[str]):
    """查询指定账号下的云服务委托或内联委托列表"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.query_delegate_list(
        account_id=account_id, service_code=service_code,
        delegate_type=delegate_type, name=name
    )
    return_obj = check_result(result)
    delegate_list = return_obj.get('result', [])

    if output_format in ['json', 'yaml']:
        format_output(delegate_list, output_format)
    else:
        if delegate_list:
            table_data = []
            headers = ['名称', '委托账号', '被委托用户ID', '类型', '创建时间']
            for d in delegate_list:
                from datetime import datetime
                ct = d.get('createTime', '')
                if isinstance(ct, int):
                    try:
                        ct = datetime.fromtimestamp(ct / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        ct = str(ct)
                table_data.append([
                    d.get('name', ''), d.get('accountId', ''),
                    d.get('assumeUserId', ''), d.get('type', ''),
                    ct
                ])
            format_table(table_data, headers, "委托列表")
        else:
            click.echo("未找到委托")


@iam.command('list-delegate-roles')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=10, type=int, help='每页条数，默认10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_delegate_roles(ctx, page: int, page_size: int, output: Optional[str]):
    """查询委托角色分页信息"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_delegate_roles(page_num=page, page_size=page_size)
    return_obj = check_result(result)
    role_list = return_obj.get('list', [])

    if output_format in ['json', 'yaml']:
        format_output(role_list, output_format)
    else:
        if role_list:
            from datetime import datetime
            table_data = []
            headers = ['委托ID', '名称', '委托账号', '委托用户ID', '类型', '状态', '创建时间']
            for r in role_list:
                ct = r.get('createTime', '')
                if isinstance(ct, int):
                    try:
                        ct = datetime.fromtimestamp(ct / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        ct = str(ct)
                table_data.append([
                    r.get('id', ''), r.get('name', ''),
                    r.get('assumeAccountId', ''), r.get('assumeUserId', ''),
                    r.get('type', ''), r.get('status', ''),
                    ct
                ])
            total = return_obj.get('total', 0)
            pages_n = return_obj.get('pages', 1)
            format_table(table_data, headers,
                         f"委托角色列表 (总计: {total} 个, 第{page}/{pages_n}页)")
        else:
            click.echo("未找到委托角色")


# ==================== 企业项目扩展 ====================

@iam.command('list-ep-groups')
@click.option('--project-id', required=True, help='企业项目ID')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=10, type=int, help='每页条数，默认10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_ep_groups(ctx, project_id: str, page: int, page_size: int,
                   output: Optional[str]):
    """企业项目关联用户组分页查询"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_ep_group_page(
        project_id=project_id, page_num=page, page_size=page_size
    )
    return_obj = check_result(result)
    group_list = return_obj.get('list', [])

    if output_format in ['json', 'yaml']:
        format_output(group_list, output_format)
    else:
        if group_list:
            from datetime import datetime
            table_data = []
            headers = ['用户组ID', '用户组名称', '描述', '用户数量', '策略数量', '创建时间']
            for g in group_list:
                ct = g.get('createTime', '')
                if isinstance(ct, int):
                    try:
                        ct = datetime.fromtimestamp(ct / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        ct = str(ct)
                table_data.append([
                    g.get('groupId', ''), g.get('groupName', ''),
                    g.get('description', ''), g.get('userCount', ''),
                    g.get('ployCount', ''), ct
                ])
            total = return_obj.get('total', 0)
            pages_n = return_obj.get('pages', 1)
            format_table(table_data, headers,
                         f"企业项目关联用户组 (总计: {total} 个, 第{page}/{pages_n}页)")
        else:
            click.echo("未找到关联用户组")


@iam.command('get-ep-policies')
@click.option('--project-id', required=True, help='企业项目ID')
@click.option('--group-id', required=True, help='用户组ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_ep_policies(ctx, project_id: str, group_id: str, output: Optional[str]):
    """查询企业项目用户组策略"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.get_ep_group_policies(
        project_id=project_id, group_id=group_id
    )
    return_obj = check_result(result)
    policy_list = return_obj.get('list', [])

    if output_format in ['json', 'yaml']:
        format_output(policy_list, output_format)
    else:
        if policy_list:
            table_data = []
            headers = ['ID', '策略名称', '策略类型', '策略范围', '产品名称']
            for p in policy_list:
                ptype = '系统策略' if p.get('ployType') == 1 else '自定义策略' if p.get('ployType') == 2 else str(p.get('ployType', ''))
                prange = '项目级' if p.get('ployRange') == 1 else '全局' if p.get('ployRange') == 2 else str(p.get('ployRange', ''))
                table_data.append([
                    p.get('id', ''), p.get('ployName', ''),
                    ptype, prange, p.get('productName', '')
                ])
            format_table(table_data, headers, "企业项目用户组策略列表")
        else:
            click.echo("未找到策略")


# ==================== AK/SK管理 ====================

@iam.command('list-access-keys')
@click.option('--user-id', required=True, multiple=True, help='用户ID（可重复）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_access_keys(ctx, user_id: List[str], output: Optional[str]):
    """查询密钥"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_access_keys(user_id_list=list(user_id))
    return_obj = check_result(result)
    ak_list = return_obj.get('accessKeyUserList', [])

    if output_format in ['json', 'yaml']:
        format_output(ak_list, output_format)
    else:
        if ak_list:
            table_data = []
            headers = ['用户ID', 'AK', 'SK(加密)', '状态', '创建时间']
            for u in ak_list:
                for ak in u.get('accessKeyList', []):
                    status = '启用' if ak.get('status') == '1000' else '禁用' if ak.get('status') == '1001' else ak.get('status', '')
                    table_data.append([
                        u.get('userId', ''), ak.get('accessKey', ''),
                        ak.get('secretKey', ''), status,
                        ak.get('createdTime', '')
                    ])
            format_table(table_data, headers, "密钥列表")
        else:
            click.echo("未找到密钥")


@iam.command('list-recycle-bin-aks')
@click.option('--user-id', required=True, multiple=True, help='用户ID（可重复）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_recycle_bin_aks(ctx, user_id: List[str], output: Optional[str]):
    """查询回收站ak"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_recycle_bin_aks(user_id_list=list(user_id))
    return_obj = check_result(result)
    recycle_list = return_obj.get('recycleBinAkList', [])

    if output_format in ['json', 'yaml']:
        format_output(recycle_list, output_format)
    else:
        if recycle_list:
            table_data = []
            headers = ['用户ID', 'AK', 'AK创建时间', '回收时间', '清理时间']
            for u in recycle_list:
                for ak in u.get('recycleBinList', []):
                    table_data.append([
                        u.get('userId', ''),
                        ak.get('ak', ''),
                        ak.get('akCreatedTime', ''),
                        ak.get('recoveryTime', ''),
                        ak.get('clearTime', '')
                    ])
            format_table(table_data, headers, "回收站AK列表")
        else:
            click.echo("回收站无AK")


# ==================== 身份供应商 ====================

@iam.command('list-identity-providers')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=10, type=int, help='每页条数，默认10')
@click.option('--name', help='身份提供商名称（模糊搜索）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_identity_providers(ctx, page: int, page_size: int,
                            name: Optional[str], output: Optional[str]):
    """分页查询身份供应商"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.list_identity_providers(
        page_num=page, page_size=page_size, name=name
    )
    return_obj = check_result(result)
    provider_list = return_obj.get('list', [])

    if output_format in ['json', 'yaml']:
        format_output(provider_list, output_format)
    else:
        if provider_list:
            from datetime import datetime
            table_data = []
            headers = ['ID', '名称', '类型', '协议', '描述', '状态', '创建时间']
            type_map = {0: '虚拟用户SSO', 1: 'IAM用户SSO'}
            proto_map = {0: 'SAML', 1: 'OIDC'}
            for p in provider_list:
                ct = p.get('createTime', '')
                if isinstance(ct, int):
                    try:
                        ct = datetime.fromtimestamp(ct / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        ct = str(ct)
                table_data.append([
                    p.get('id', ''), p.get('name', ''),
                    type_map.get(p.get('type', ''), p.get('type', '')),
                    proto_map.get(p.get('protocol', ''), p.get('protocol', '')),
                    p.get('remark', ''), p.get('status', ''),
                    ct
                ])
            total = return_obj.get('total', 0)
            pages_n = return_obj.get('pages', 1)
            format_table(table_data, headers,
                         f"身份供应商列表 (总计: {total} 个, 第{page}/{pages_n}页)")
        else:
            click.echo("未找到身份供应商")


@iam.command('get-identity-provider-info')
@click.option('--idp-id', required=True, help='身份供应商ID')
@click.option('--entity-id', required=True, help='实体ID')
@click.option('--name-id', required=True, help='用户ID')
@click.option('--login-email', help='登录邮箱（与name-id二选一）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_identity_provider_info(ctx, idp_id: str, entity_id: str,
                               name_id: str, login_email: Optional[str],
                               output: Optional[str]):
    """查询身份供应商和关联用户信息"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.get_identity_provider_info(
        id_p_id=idp_id, entity_id=entity_id,
        name_id=name_id, login_email=login_email
    )
    info = check_result(result)
    if output_format in ['json', 'yaml']:
        format_output(info, output_format)
    else:
        if info:
            click.echo(f"\n身份供应商信息")
            click.echo("=" * 60)
            click.echo(f"供应商ID: {info.get('idPId', '')}")
            click.echo(f"类型: {'IAM用户' if info.get('type') == '1' else '虚用户'}")
            click.echo(f"实体ID: {info.get('entityId', '')}")
            click.echo(f"登录地址: {info.get('loginLocation', '')}")
            click.echo(f"登出地址: {info.get('logoutLocation', '')}")
            users = info.get('userList', [])
            if users:
                click.echo(f"\n关联用户:")
                for u in users:
                    click.echo(f"  - 用户名: {u.get('userName', '')}, "
                               f"用户ID: {u.get('userId', '')}, "
                               f"邮箱: {u.get('email', '')}")
            click.echo("=" * 60)
        else:
            click.echo("未找到身份供应商信息")


# ==================== MFA管理 ====================

@iam.command('check-totp')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def check_totp(ctx, output: Optional[str]):
    """查询虚拟MFA是否绑定"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.check_totp_effective()
    if output_format in ['json', 'yaml']:
        format_output(result, output_format)
    else:
        click.echo(f"虚拟MFA绑定状态: {result}")


# ==================== 敏感操作 ====================

@iam.command('query-sensitive-events')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=10, type=int, help='每页条数，默认10')
@click.option('--start-time', required=True, help='开始时间 (GMT+8, 格式: 2024-03-19 15:27:42)')
@click.option('--end-time', required=True, help='结束时间 (GMT+8, 格式: 2024-03-26 15:27:42)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def query_sensitive_events(ctx, page: int, page_size: int,
                           start_time: str, end_time: str,
                           output: Optional[str]):
    """查询敏感操作分页信息"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.query_sensitive_events(
        page_num=page, page_size=page_size,
        start_time=start_time, end_time=end_time
    )
    return_obj = check_result(result)
    event_list = return_obj.get('list', [])

    if output_format in ['json', 'yaml']:
        format_output(event_list, output_format)
    else:
        if event_list:
            table_data = []
            headers = ['TraceID', '权限码', '状态码', '操作用户', '来源IP', '邮箱', '时间']
            for e in event_list:
                table_data.append([
                    e.get('traceId', ''), e.get('traceName', ''),
                    e.get('code', ''), e.get('operateUser', ''),
                    e.get('sourceIp', ''), e.get('email', ''),
                    e.get('createTime', '')
                ])
            total = return_obj.get('total', 0)
            pages_n = return_obj.get('pages', 1)
            format_table(table_data, headers,
                         f"敏感操作记录 (总计: {total} 条, 第{page}/{pages_n}页)")
        else:
            click.echo("未找到敏感操作记录")


@iam.command('query-op-verify')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def query_op_verify(ctx, output: Optional[str]):
    """查询敏感操作保护"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.query_op_verify()
    return_obj = check_result(result)
    if output_format in ['json', 'yaml']:
        format_output(return_obj, output_format)
    else:
        op = return_obj.get('opVerify', '')
        desc_map = {
            '0': '关闭敏感操作',
            '1': '开启用户级敏感操作',
            '2': '开启账号级敏感操作'
        }
        click.echo(f"敏感操作保护状态: {desc_map.get(op, '未知')} (opVerify={op})")


# ==================== 服务管理 ====================

@iam.command('query-service-authorities')
@click.option('--service-id', required=True, type=int, help='云服务ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def query_service_authorities(ctx, service_id: int, output: Optional[str]):
    """根据云服务ID查询云服务权限点"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.query_service_authorities(service_id=service_id)
    return_obj = check_result(result)
    auth_list = return_obj.get('authorityList', [])

    if output_format in ['json', 'yaml']:
        format_output(auth_list, output_format)
    else:
        if auth_list:
            table_data = []
            headers = ['服务ID', '权限点名称', '编码', '描述']
            for a in auth_list:
                table_data.append([
                    a.get('serviceId', ''), a.get('name', ''),
                    a.get('code', ''), a.get('description', '')
                ])
            format_table(table_data, headers, "云服务权限点列表")
        else:
            click.echo("未找到权限点")


@iam.command('query-services')
@click.option('--service-name', help='服务名称（中文）')
@click.option('--service-type', type=int, help='服务类型 (1:资源池级, 2:全局级)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def query_services(ctx, service_name: Optional[str],
                   service_type: Optional[int], output: Optional[str]):
    """根据条件查询云服务产品"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.query_services_by_condition(
        service_name=service_name, service_type=service_type
    )
    return_obj = check_result(result)
    service_list = return_obj.get('serviceList', [])

    if output_format in ['json', 'yaml']:
        format_output(service_list, output_format)
    else:
        if service_list:
            table_data = []
            headers = ['ID', '服务编码', '服务名称', '类型', '描述']
            type_map = {1: '资源池级', 2: '全局级'}
            for s in service_list:
                table_data.append([
                    s.get('id', ''), s.get('serviceCode', ''),
                    s.get('mainServiceName', ''),
                    type_map.get(s.get('serviceType', ''), s.get('serviceType', '')),
                    s.get('serviceDesc', '')
                ])
            format_table(table_data, headers, "云服务产品列表")
        else:
            click.echo("未找到云服务产品")


# ==================== 其他 ====================

@iam.command('query-quota')
@click.option('--type', 'quota_type', required=True, type=int,
              help='配额类型 (1:用户, 2:用户组, 3:策略)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def query_quota(ctx, quota_type: int, output: Optional[str]):
    """根据配额类型查询配额列表"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.query_quota_by_type(quota_type=quota_type)
    quota = check_result(result)
    if output_format in ['json', 'yaml']:
        format_output(quota, output_format)
    else:
        if quota:
            type_names = {1: '用户配额', 2: '用户组配额', 3: '策略配额'}
            click.echo(f"\n{type_names.get(quota_type, '配额')}")
            click.echo("=" * 60)
            click.echo(f"配额ID: {quota.get('id', '')}")
            click.echo(f"配额类型: {quota.get('quotaType', '')}")
            click.echo(f"总配额: {quota.get('totalQuota', '')}")
            click.echo(f"已用配额: {quota.get('useQuota', '')}")
            click.echo(f"状态: {quota.get('status', '')}")
            click.echo("=" * 60)
        else:
            click.echo("未找到配额信息")


@iam.command('query-regions')
@click.option('--zone-name', help='资源池名称')
@click.option('--zone-id', help='资源池ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def query_regions(ctx, zone_name: Optional[str], zone_id: Optional[str],
                  output: Optional[str]):
    """查询账户资源池"""
    iam_client = get_client(ctx)
    output_format = output or ctx.obj.get('output', 'table')
    result = iam_client.query_regions(zone_name=zone_name, zone_id=zone_id)
    return_obj = check_result(result)
    region_list = return_obj.get('regionList', [])

    if output_format in ['json', 'yaml']:
        format_output(region_list, output_format)
    else:
        if region_list:
            table_data = []
            headers = ['资源池ID', '资源池名称']
            for r in region_list:
                table_data.append([
                    r.get('zoneId', ''), r.get('zoneName', '')
                ])
            format_table(table_data, headers, "账户资源池列表")
        else:
            click.echo("未找到资源池")
