import re
import importlib
import time
import hashlib
import pickle
from django.shortcuts import render, redirect

__version__ = 1.0
__auth__ = "lczmx"


class EasyPermission:
    def __init__(self, settings):
        """
            self.is_menu = False
            self.create_re_type_url = None
            self.func_name = None
            self._current_permission = None
            self._perm_md5_list = []
            self.permission_list = []
        :param settings: 配置文件或字典
        """
        self.is_menu = False
        self.create_re_type_url = None
        self.func_name = None
        self._current_permission = None
        self._perm_md5_list = []
        self.permission_list = []
        check = Check(settings)  # 检验 settings 合法性
        self.settings = check.checked_settings
        self._import_module()

    def check_permission(self, func):
        self.func_name = func.__name__

        def inner(*args, **kwargs):
            request = args[0]  # 获取request对象
            auth_user_id = self.get_user_func(request)  # 获取用户的ID
            if not auth_user_id and auth_user_id != 0:  # 没有用户id，要求登录
                return redirect(self.settings.get("LOGIN_PATH_URL"))
            if not self.handle(request, auth_user_id, *args, **kwargs):
                return render(request, self.settings.get("NOT_PERMISSION_PAGE_URL"))  # 没有权限访问的提示页面
            return func(*args, **kwargs)

        return inner

    def format_user_permission_data(self, one_perm):
        """
        用去产生权限数据
        {
        "url":{ "is_re":1 , "method":"GET",,"detail" :{"user_id":"1"}， "hook":[hook1, ...], parent_id = 1,
         "name"="Mange" ,"status":False},}
         用于去重
         ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        返回 PermissionData对象， 里面封装一条权限数据
        """
        temp = {"url": one_perm.permission.url, "is_re": one_perm.permission.is_re, "method": one_perm.action.method,
                "parent_id": None, "name": one_perm.caption, "status": False, "detail": {}, "hook": []}
        if one_perm.permission.parent_id:
            #  插入parent_id
            temp["parent_id"] = one_perm.permission.parent_id
        if one_perm.action2permission2detail.all():
            detail_dic = {}
            for detail_objs in one_perm.action2permission2detail.all():
                detail_dic[detail_objs.detail.parameter] = detail_objs.detail.value
            temp["detail"] = detail_dic
        if one_perm.action2permission2hooks.all():
            hook_list = []
            for hook_obj in one_perm.action2permission2hooks.all():
                hook_list.append(hook_obj.hook.func_name)
            temp["hook"] = hook_list
        # 进行去重
        perm_md5 = self._make_md5(temp)
        if perm_md5 in self._perm_md5_list:
            return None
        self._perm_md5_list.append(perm_md5)
        permission_data = PermissionData(**temp)
        return permission_data

    def is_effective(self, one_perm, mode="u"):
        """
           检验权限是否过期
               假如过期了，将：
                    1、判断是否被允许删除 , 若为True ==> 删除该权限
                    2、return False
        """
        if mode == "u":
            obj = self.models.User2Action2Permission.objects.filter(action2Permission_id=one_perm.id).first()
        elif mode == "g":
            obj = self.models.Role2Action2Permission.objects.filter(action2Permission_id=one_perm.id).first()
        else:
            raise ValueError("mode 错误")
        effective_time = obj.effective_time
        if not effective_time:
            # 没有设置有效时间
            return True
        effective_time_str = str(effective_time)
        if time.mktime(time.strptime(effective_time_str, "%Y-%m-%d")) > time.time():
            self.is_menu = True
            return True
        else:
            self.is_menu = False
            if obj.is_del:
                obj.delete()

    def _make_md5(self, data):
        """返回MD5值，用做去重的标准"""
        m = hashlib.md5()
        m.update(pickle.dumps(data))
        return m.hexdigest()

    def distinct(self, one_perm, mode):
        """进行权限去重"""
        if not self.is_effective(one_perm, mode):  # 检验有效性
            return False
        permission = self.format_user_permission_data(one_perm)  # 格式化权限

        # 去重, 重复权限自动pass掉， 对于已经存在的会返回None
        if permission:
            self.permission_list.append(permission)

    def _import_module(self):
        """根据配置导入一些所必须的函数"""
        *get_user_path, get_user_func_name = self.settings.get("RETURN_USER_ID").split(".")
        get_user_module = importlib.import_module(".".join(get_user_path))
        self.models = importlib.import_module(self.settings.get("MODEL_DIR"))
        self.get_user_func = getattr(get_user_module, get_user_func_name)

    def _get_perm_from_database(self):
        # 获取当前用户的权限
        user_permissions = self.models.Action2Permission.objects. \
            filter(user2action2permission__user_id=self.auth_user_id).select_related()

        # 获取当前用户所在组（角色）的权限
        group_permissions = self.models.Action2Permission.objects. \
            filter(role2action2permission__role__role2user__user_id=self.auth_user_id).select_related()

        return user_permissions, group_permissions

    def handle(self, request, auth_user_id, *args, **kwargs):
        """ 根据 request 请求，匹配Url 和 method 最后 匹配 详细操作 和 自定义钩子函数"""
        self.auth_user_id = auth_user_id
        user_permissions, group_permissions = self._get_perm_from_database()

        for one_perm in user_permissions:  # 验证用户的个人权限
            self.distinct(one_perm, "u")
        for one_perm in group_permissions:  # 验证用户的组权限
            self.distinct(one_perm, "g")

        for permission in self.permission_list:
            self._current_permission = permission  # 每次都会覆盖上一次的 PermissionData对象
            if self.shunt(request):  # 开始正式验证
                if self.is_create_menus():  # 判断是否生成菜单
                    # 生成菜单 并 写入到request对象里
                    # 若匹配成了， 则 permission 则为当前url对应的对象

                    # 判断是否设置可以生成re类型的url
                    if self.settings.get("CREATE_RE_TYPE_URL"):
                        self.create_re_type_url = self.settings.get("CREATE_RE_TYPE_URL_FUNC")
                    Create_menu(request, models=self.models, is_create_re_type_url=self.create_re_type_url,
                                permission_list=self.permission_list, active_permission=permission)
                return True
        return False

    def shunt(self, request):
        """
            处理验证用户的个人权限 和 组权限
            一旦一个不通过则立刻 return False
        """

        if not self._matching_url(request):
            return False
        if not self._matching_method(request):
            return False
        if not self._matching_detail(request):
            return False
        if not self._matching_hook(request):
            return False
        return True

    def _matching_url(self, request):
        """ 判断Url有权访问 """
        url_path = request.path
        url = self._current_permission.url
        if self._current_permission.is_re:  # 使用re
            if re.match(url, url_path):
                return True
        else:
            if url == url_path:
                return True
        return False

    def _matching_method(self, request):
        """ 判断请求方式 """
        req_method = request.method
        if self._current_permission.method == req_method:
            return True
        return False

    def _matching_detail(self, request):
        """ 判断是否符合详细操作 """
        detail_dic = self._current_permission.detail
        if not detail_dic:  # 没有设置详细权限时，为表级别的权限
            return True
        req_detail_operation_dic = getattr(request, request.method)

        for parameter, value in detail_dic.items():
            if req_detail_operation_dic.get(parameter, None) != value:
                # 有一个不符合立即False,跳出循环
                return False
        return True

    def _matching_hook(self, request):
        """ 由于执行用户自定义钩子函数
            hook_list: 用户数据库中的hook函数名
        """
        hook_list = self._current_permission.hook
        if not hook_list or not self.settings.get("HOOKS_DIRS"):  # 没有定义钩子函数( 用户的权限或者 settings中 )
            return True

        try:
            hook_dirs = [h[0] for h in sorted(self.settings.get("HOOKS_DIRS"), key=lambda x: x[1])]  # 根据优先级排序
        except Exception as e:
            raise ValueError(
                "HOOKS_DIRS format error! Please refer to the settings file for the format.\
                \nHOOKS_DIRS 格式错误 !格式请参考settings文件")
        while hook_list:
            hook = hook_list.pop()
            for hook_dir in hook_dirs:
                try:
                    m = importlib.import_module(hook_dir)

                    if hasattr(m, hook):
                        func = getattr(m, hook)
                        if not func(request):  # 有一个不符合立即False,跳出循环
                            return False
                        break  # 找到一个hook_dir后将不会继续往下找, 继续下一个hook
                except ImportError as e:
                    print(e)
                    pass
        return True

    def is_create_menus(self):
        """判断是否生成菜单"""
        if self.settings.get("CREATE_MENU"):
            if hasattr(self.settings, "CREATE_MENU_FUNC_NAME"):  # 有指定的views函数，生成菜单标签
                if self.func_name not in self.settings.get("CREATE_MENU_FUNC_NAME") \
                        and self.settings.get("CREATE_MENU_FUNC_NAME"):
                    # 有指定的views函数名， 但却不符合
                    # 仅在此条件下不生成菜单标签
                    return False
                if self.settings.get("CREATE_RE_TYPE_URL"):
                    self.create_re_type_url = self.settings.get("CREATE_RE_TYPE_URL_FUNC")
            return True


class BaseData:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.parent_id = kwargs.get("parent_id")
        self.status = kwargs.get("status", False)


class PermissionData(BaseData):
    """
        用于产生具有格式的权限数据
    """

    def __init__(self, **kwargs):
        self.is_re = kwargs.get("is_re", False)
        self.url = kwargs.get("url", "/")
        self.method = kwargs.get("method", "GET")
        self.detail = kwargs.get("detail", {})
        self.hook = kwargs.get("hook", [])
        super().__init__(**kwargs)


class Menu_Data(BaseData):
    """
    用于产生具有格式菜单数据
    """

    def __init__(self, **kwargs):
        self.nid = kwargs.get("nid", False)
        self.has_children = False
        self.children = []
        super().__init__(**kwargs)


class Create_menu:
    """
    用于生成菜单

    """

    def __init__(self, request, models, permission_list, active_permission, is_create_re_type_url):
        """
        拿到所有的权限信息， 进行创建菜单，并写到request对象中

        :param request: 用于存储菜单数据
        :param models: 存储菜单数据的model对象
        :param permission_list: 权限列表
        :param active_permission: 当前url所在权限
        :param is_create_re_type_url: 可以处理re类型 URL 的对象
        """
        self._menu_list = []  # Menus 表里的数据
        self._active_permission_parent_id = None  # 当前权限的父级菜单id
        self._has_children_parent_id = set()  # 有权限对象的菜单的 parent_id
        self.menu_queryset = None
        self.permission_list = permission_list
        self.is_create_re_type_url = is_create_re_type_url
        self.models = models
        self._re_type_url_parent_id = set()
        self.active_permission = active_permission
        request._menu_str = self.active()

    def active(self):
        """
            主要处理 menu 数据 和 permission 数据格式的转变
        :return:  菜单标签的str
        """
        self.menu_queryset = self.models.Menu.objects.all()
        self._create_menu_data()
        self._add_perm_to_menu()
        self._add_menu_to_menu()
        self._change_menu_status()
        return self.process_result_tree()

    def _add_perm_to_menu(self):
        """将权限放入 menu_list, 并处理 menu_list"""
        for permission_obj in self.permission_list:
            for one_menu_obj in self._menu_list:
                #  把权限放入权限其父级菜单
                if permission_obj.parent_id == one_menu_obj.nid:
                    # 限定只能 GET,
                    #   若为正常的   ==> 直接通过
                    #   若为re类型的 ==> 是否是可以生成的re类型
                    if (permission_obj.method == "GET" and not permission_obj.is_re) or (
                            permission_obj.method == "GET" and permission_obj.is_re and self.is_create_re_type_url):

                        one_menu_obj.children.append(permission_obj)
                        one_menu_obj.has_children = True
                        if one_menu_obj.parent_id:
                            self._has_children_parent_id.add(one_menu_obj.parent_id)

    def _add_menu_to_menu(self):
        """ 处理菜单之间的关系"""
        for one_menu_obj in self._menu_list:
            for menu_obj in self._menu_list:
                if menu_obj.parent_id == one_menu_obj.nid and menu_obj not in one_menu_obj.children:
                    one_menu_obj.children.append(menu_obj)
                # 改变 has_children属性
                if menu_obj.nid in self._has_children_parent_id:
                    menu_obj.has_children = True
                    if menu_obj.parent_id:
                        self._has_children_parent_id.add(menu_obj.parent_id)

    def _change_menu_status(self):
        """ 进行修改父级的 status, 对应的父级菜单时执行，直到根节点 """
        while self._active_permission_parent_id:
            for one_menu_obj in self._menu_list:
                if one_menu_obj.nid == self._active_permission_parent_id:
                    one_menu_obj.status = True
                    self._active_permission_parent_id = one_menu_obj.parent_id

    def _create_menu_data(self):
        """格式化Menu表的数据"""
        for m_obj in self.menu_queryset:
            temp = {}
            temp["nid"] = m_obj.id
            temp["name"] = m_obj.caption
            temp["parent_id"] = m_obj.parent_id
            temp["status"] = False
            temp["is_re"] = False
            menu_data_obj = Menu_Data(**temp)
            self._menu_list.append(menu_data_obj)

    def process_result_content(self, content):
        """
            对不同的content进行处理
            list对象              ==>  继续迭代
            Menu_Data对象         ==>  生成非a标签
            PermissionData对象    ==>  生成a标签
        """
        if isinstance(content, list):  # 为 children 列表时
            for item in content:
                try:
                    if not item.has_children: continue
                except AttributeError:  # PermissionData 时会报错
                    pass
                self.process_result_content(item)

        if isinstance(content, Menu_Data):  # 菜单时
            if content.has_children:
                self._process_element(content, class_name="title")

        if isinstance(content, PermissionData):  # 处理最终的权限信息时
            if content.method.lower() == "get":  # 只会生成 GET请求的url
                url = content.url
                is_active = "active"
                if not content.status: is_active = ""
                if content.is_re:
                    # 生成Re_Url
                    *func_path, func_name = self.is_create_re_type_url.split(".")
                    m = importlib.import_module(".".join(func_path))
                    func = getattr(m, func_name)
                    url = func(content)

                if content.detail:  # 加入 get 参数
                    temp = ["?"]
                    temp.extend(
                        ["%s=%s&" % (detail_k, detail_v) for detail_k, detail_v in content.detail.items()])
                    url += "".join(temp)
                    url = url[:-1]
                self._tree_list.append("""<a class="%s menu" href='%s'>%s</a>""" % (is_active, url, content.name))

    def process_result_tree(self):
        """
        用于筛选多余的权限，并且产生根标签
        :return: 最终标签树的字符串
        """
        self._tree_list = []
        for item in self._menu_list:
            if not item.has_children or item.parent_id: continue  # 根 并且 有具体权限
            self._process_element(item, class_name="menu-item")
        return "".join(self._tree_list)

    def _process_element(self, item, class_name):
        """
            该函数用于产生除了a标签外的全部标签
            还负责继续往里生成子标签
        :param item: 非具体权限标签
        :param class_name: 类名（HTML的）
        """
        is_active = 'active'
        if not item.status: is_active = ''
        title = item.name
        self._tree_list.append(
            """<ul class="%s %s"><span>%s</span><li class="content">""" % (class_name, is_active, title))
        self.process_result_content(item.children)
        self._tree_list.append("</li></ul>")


class Log:
    """日志生成类"""

    def __init__(self):
        pass


class Check:
    """
        生成EasyPermission对象时， 检查用户的settings文件是否符合规范
    """

    def __init__(self, user_settings):
        self.user_settings = user_settings
        self.default_settings = self._create_default_settings()
        self.checked_settings = {}
        self.checking()

    def checking(self):
        for key, val in self.default_settings.items():
            if hasattr(self.user_settings, key):
                self.checked_settings[key] = getattr(self.user_settings, key)
            else:
                if val is None:  # 默认值为None为必须提供的值
                    raise ValueError(
                        "The incoming settings is missing the %s parameter!\n   传入的settings缺少 %s " % (key, key))
                else:
                    self.checked_settings[key] = val

    def _create_default_settings(self):
        """
            默认值为None为必须提供的值
        :return:  默认的settings字典
        """
        default_settings = {
            "LOGIN_PATH_URL": None, "NOT_PERMISSION_PAGE_URL": None, "MODEL_DIR": None, "RETURN_USER_ID": None,
            "HOOKS_DIRS": [], "CREATE_MENU": False, "CREATE_MENU_FUNC_NAME": [], "GENERATE_LOG": False,
            "GENERATE_LOG_PATH": "", "CREATE_RE_TYPE_URL": False, "CREATE_RE_TYPE_URL_FUNC": "",
        }
        return default_settings
