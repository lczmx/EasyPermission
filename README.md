# EasyPermission-
适用于由Django开发的网站的通用权限框架，只要设置好配置文件就快速做好权限管理，而且还支持各种条件的自定制扩展。


功能：

1、权限验证：
  |
  |-- 简单权限筛选：一个url对应一个url（可以是具体的字符串或者是一个正则表达式）
  |
  |-- 稍微复杂的筛选：url可以参数
  |
  |-- 究极筛选：可以定义钩子函数传入的是request对象，只需返回一个布尔值就能确定是否通过能权限（注：需要自己扩展）
  |
  
2、生成菜单：根据权限信息生成的菜单，生成的菜单的可以有GET参数，视权限而定，还能生成由正则表达式构成的菜单（注：需要自己扩展）

    注：生成的菜单放入到request对象的_menu_str属性里，使用时只需request._menu_str取值即可



使用：

  1、下载easyPermission.py文件和 models.py文件，EasyPermission文件是主文件，models文件用于建立存放权限数据的数据库。
  
  2、根据models建立数据库，注：要提供用户表，作为其他表的关联
  
  3、用过Django的admin等方式为用户添加权限，具体是什么权限，那就要根据业务逻辑了
  
  4、在项目的views中导入easyPermission,实例化easyPermission.EasyPermission，此时要传入配置文件（怎么配置参看 settings_doc.py文件）
  
  5、使用对象的check_permission作为装饰器装饰函数（FBV、CBV）
  
  6、完成使用
