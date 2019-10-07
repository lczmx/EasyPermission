from django.db import models
import importlib

# 用户表的路径
USER_MODEL_DIR = "autoApp.models.UserInfo"

*user_dir, model_name = USER_MODEL_DIR.split(".")
user = importlib.import_module(".".join(user_dir))

User = getattr(user, model_name)


class Role(models.Model):
    caption = models.CharField(max_length=32, verbose_name="角色名称")

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = "角色表"


class Role2User(models.Model):
    user = models.ForeignKey(User, related_name="role2user", on_delete=models.CASCADE)
    role = models.ForeignKey("Role", related_name="role2user", on_delete=models.CASCADE)

    def __str__(self):
        return "%s -- %s" % (self.user, self.role.caption)

    class Meta:
        unique_together = [("user", "role"), ]
        verbose_name_plural = "用户分配角色"


class Action(models.Model):
    """提交方式表"""
    caption = models.CharField(max_length=32, verbose_name="提交方式名")
    method = models.CharField(max_length=16)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = "提交方式表"


class Permission(models.Model):
    """url表"""
    caption = models.CharField(max_length=32)
    is_re_choices = ((0, "url不使用正则表达式"), (1, "url使用正则表达式"))
    is_re = models.BooleanField(choices=is_re_choices, default=0)
    url = models.CharField("URL", max_length=64)
    parent = models.ForeignKey("Menu", on_delete=models.CASCADE, null=True, blank=True, related_name="permission")

    def __str__(self):
        return "%s--%s" % (self.caption, self.url)

    class Meta:
        verbose_name_plural = "url表"


class Detail(models.Model):
    caption = models.CharField(max_length=32)
    parameter = models.CharField("参数名", max_length=16)
    value = models.CharField("参数值", max_length=16)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = "详细操作表"


class Hooks(models.Model):
    """自定义钩子函数表"""
    caption = models.CharField("名称", max_length=32)
    func_name = models.CharField("函数名", max_length=16)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = "钩子函数表"


class Action2Permission(models.Model):
    """权限表"""
    caption = models.CharField(max_length=32)
    action = models.ForeignKey("Action", related_name="Action2Permission", on_delete=models.CASCADE)
    permission = models.ForeignKey("Permission", related_name="Action2Permission", on_delete=models.CASCADE)

    def __str__(self):
        return self.caption

    class Meta:
        unique_together = [("action", "permission", "action"), ]
        verbose_name_plural = "权限表"


class Action2Permission2Detail(models.Model):
    """权限分配详细操作"""
    action2Permission = models.ForeignKey("Action2Permission", related_name="action2permission2detail",
                                          on_delete=models.CASCADE)
    detail = models.ForeignKey("Detail", related_name="action2permission2detail", on_delete=models.CASCADE)

    class Meta:
        unique_together = [("action2Permission", "detail"), ]
        verbose_name_plural = "权限分配详细操作表"


class Action2Permission2Hooks(models.Model):
    """权限分配钩子表"""
    action2Permission = models.ForeignKey("Action2Permission", verbose_name="权限",
                                          related_name="action2permission2hooks", on_delete=models.CASCADE)
    hook = models.ForeignKey("Hooks", verbose_name="钩子函数",
                             related_name="action2permission2hooks", on_delete=models.CASCADE)

    class Meta:
        unique_together = [("action2Permission", "hook"), ]
        verbose_name_plural = "权限分配钩子表"


class Role2Action2Permission(models.Model):
    """角色分配权限表"""
    role = models.ForeignKey("Role", verbose_name="角色",
                             related_name="role2action2permission", on_delete=models.CASCADE)
    action2Permission = models.ForeignKey("Action2Permission", verbose_name="权限",
                                          related_name="role2action2permission", on_delete=models.CASCADE)
    effective_time = models.DateField(verbose_name="有效时间（默认为永久有效）", default=None, null=True, blank=True)
    is_del = models.BooleanField(default=0, verbose_name="到期时是否自动删除")
    is_menu = models.BooleanField(default=1, verbose_name="是否加入菜单")


    def __str__(self):
        return "%s-%s:%s?t=%s  (%s)" % (self.role.caption, self.action2Permission.permission.caption,
                                        self.action2Permission.permission.url, self.action2Permission.action.method,
                                        self.action2Permission.action.caption)

    class Meta:
        unique_together = [("role", "action2Permission"), ]
        verbose_name_plural = "角色分配权限"


class User2Action2Permission(models.Model):
    """用户分配权限表"""
    user = models.ForeignKey(User, related_name="user2action2permission", on_delete=models.CASCADE)
    action2Permission = models.ForeignKey("Action2Permission", verbose_name="权限",
                                          related_name="user2action2permission", on_delete=models.CASCADE)
    effective_time = models.DateField(verbose_name="有效时间（默认为永久有效）", default=None, null=True, blank=True)
    is_del = models.BooleanField(default=0, verbose_name="到期时是否自动删除")
    is_menu = models.BooleanField(default=1, verbose_name="是否加入菜单")


    def __str__(self):
        return "%s-%s" % (self.user, self.action2Permission)

    class Meta:
        unique_together = [("user", "action2Permission"), ]
        verbose_name_plural = "用户分配权限"


class Menu(models.Model):
    """菜单表"""
    caption = models.CharField(verbose_name="菜单名称", max_length=32)
    parent = models.ForeignKey("Menu", verbose_name="父级菜单", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = "菜单表"
