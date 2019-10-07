"""
    自定义钩子函数

    传入参数为 request 对象,
    返回值必须为布尔值
"""


def vip_user(request):
    if request.GET.get("nid") == str(10):
        return True
    else:
        return False
