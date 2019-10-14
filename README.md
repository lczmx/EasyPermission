# EasyPermission
适用于由Django开发的网站的通用权限框架，只要设置好配置文件就快速做好权限管理，而且还支持各种条件的自定制扩展。


## 功能：

### 1、权限验证 -- 支持添加临时权限

 支持临时分配权限
  
 简单权限筛选：一个url对应一个url（可以是具体的字符串或者是一个正则表达式）
  
 稍微复杂的筛选：url可以参数
  
 究极筛选：可以定义钩子函数传入的是request对象，只需返回一个布尔值就能确定是否通过能权限（注：需要自己扩展）
  
  
### 2、可以检验是否登录
  
  没有登录时会跳转到登录页面
  

### 3、生成菜单
根据权限信息生成的菜单，生成的菜单的可以有GET参数，视权限而定，还能生成由正则表达式构成的菜单（注：需要自己扩展）

 注：生成的菜单放入到request对象的_menu_str属性里，使用时只需request._menu_str取值即可
    



## 使用：

  1、下载easyPermission.py文件和 models.py文件，EasyPermission文件是主文件，models文件用于建立存放权限数据的数据库。
  
  2、根据models建立数据库，注：要提供用户表，作为其他表的关联
  
  3、用过Django的admin等方式为用户添加权限，具体是什么权限，那就要根据业务逻辑了
  
  4、在项目的views中导入easyPermission,实例化easyPermission.EasyPermission，此时要传入配置文件（怎么配置参看 settings_doc.py文件）
  
  5、使用对象的check_permission作为装饰器装饰函数（FBV、CBV）
  
  6、完成使用


## modeles.py的表说明

由于定义表的时候没有命名好，所以只能口述一波了

注：这个权限的基本原理是角色分配权限和用户分配权限

一个角色可以理解成一个组


Role --角色表 ：分配权限的单位，一个角色拥有某些特定的权限

Role2User --用户分配角色表：用于用户表和角色表相关联

Action --提交方式表：记录提交方式的。如GET，POST

Permission -- url表：记录没有参数的绝对地址的url

Detail --详细操作表：定义url的GET参数

Hooks --钩子函数表：钩子函数的函数名，验证时会根据配置文件和函数名来找到对应的钩子函数

Action2Permission --权限表：对URL和提交方式进行绑定，这是一个最简单的权限

Action2Permission2Detail --权限分配详细操作表：为权限绑定GET参数

Action2Permission2Hooks --权限分配钩子表：为权限绑定钩子函数

Role2Action2Permission --角色分配权限：正式为角色绑定权限

User2Action2Permission --用户分配权限表：也可以直接为某些用户分配特殊的权限

Menu --菜单表：用于生成菜单，用于给URL（Permission表）绑定



