
# ###################### settings可以是一个字典 或者 py文件 ######################

# ====================== HOOKS_DIRS ==========================================

# 钩子函数的地址
# 格式 ==> (("A.B.func_name", 22), ...)
# 数字为该函数的权重，数字越小越早执行
#
# 自定义钩子函数：
#   传入参数为
#       request对象
#   返回值必须为布尔值

# The address of the hook function
# Format ==> (("A.B.func_name", 22), ...)
# int is the weight of the function, the smaller the number, the earlier the execution

# Custom hook function:
#   Pass in parameter is
#       request object
#   Return value must be a boolean value

HOOKS_DIRS = (
    ("easyAdmin.permission.userhooks", 1),
)


# ====================== LOGIN_PATH_URL =======================================

# 未登录时要进行转跳
# LOGIN_PATH_URL为要登录页面的URL
# 注：没有用户返回值时，判断为未登录

# if you are not logged in
# LOGIN_PATH_URL is the URL of the page to be logged in
# Note: When there is no return use id, it is judged that it is not logged in

LOGIN_PATH_URL = "/login.html/"


# ====================== NOT_PERMISSION_PAGE_URL =============================

# 没权限时要显示的错误页面
# 要注意是否已经在 django 配置 TEMPLATES

# Error page to display when there is no permission
# Tip: Have you configured TEMPLATES in django?

NOT_PERMISSION_PAGE_URL = 'easyAdmin/page_403.html'


# ====================== MODEL_DIR ============================================

# 该 permission插件所需的models.py的路径
# 需要在models.py提供用户表作为关联
# 用户表的路径

# The path to the models.py required by the permission plugin
# Need to provide user table as association in models.py
# User table path

MODEL_DIR = "easyAdmin.models"


# ====================== RETURN_USER_ID =======================================

# 返回用户ID函数的路径，用于判断是否用户是否登录和产生权限信息

# Return the path of the user ID function to determine whether the user
# logs in and generates permission information.

RETURN_USER_ID = "easyAdmin.permission.config.get_auth_user_id"


# ====================== CREATE_MENU ==========================================

# 是否生成菜单标签

# Whether to generate menu labels?

CREATE_MENU = True


# ====================== CREATE_MENU_FUNC_NAME ================================

# 生成菜单标签具体到哪一个views函数， 不写或留空则为全部
# 如：views.py 下的 index 函数

# Generate menu tags to which view function, not write or leave blank for all
# E.g :  views.py ---> index()

CREATE_MENU_FUNC_NAME = ["index", ]


# ===> 未完成

# 是否生成日志， 默认不生成 ===========> 未完成

GENERATE_LOG = False


# 日志保存的路径

GENERATE_LOG_PATH = ""


# ====================== CREATE_RE_TYPE_URL ===================================

# 是否生成 re 的url， 默认不生成

# Whether to generate the re url, the default is not generated

CREATE_RE_TYPE_URL = False


# ====================== CREATE_RE_TYPE_URL_FUNC ==============================

# 注意：CREATE_RE_TYPE_URL必须为True，设置CREATE_RE_TYPE_URL_FUNC无效
# 要生成的re类型的url的函数，
# 传入的 PermissionData的对象，返回字符串

# Note: CREATE_RE_TYPE_URL must be True, setting CREATE_RE_TYPE_URL_FUNC is invalid
# To generate a function of the re type url,
# Incoming PermissionData object, returning a string

CREATE_RE_TYPE_URL_FUNC = "easyAdmin.permission.config.creat_re_url"