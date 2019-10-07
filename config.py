"""
这里创建自定义接口函数
"""

def get_auth_user_id(request):
    """返回当前用户的ID"""
    return request.session.get("_auth_user_id")

def creat_re_url(permission_data):
    """
    :param permission_data ： 传入的 PermissionData的对象
    :return:    不包含get参数的URL 如 ： /app01/data2/
    """
    print(permission_data)
    return "http://www.baidu.com"