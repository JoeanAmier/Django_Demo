from django.contrib import admin

from .models import Choice, Question


# 创建管理员账号: python manage.py createsuperuser
class ChoiceInline(admin.TabularInline):
    """通过 TabularInline （替代 StackedInline ），关联对象以一种表格式的方式展示，显得更加紧凑。"""
    model = Choice
    extra = 3  # 三个关联的选项插槽


class QuestionAdmin(admin.ModelAdmin):
    # 将表单分为几个字段集：
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    # 这会告诉 Django：“Choice 对象要在 Question 后台页面编辑。默认提供 3 个足够的选项字段。”
    inlines = [ChoiceInline]
    # 包含要显示的字段名的元组，在更改列表页中以列的形式展示这个对象。
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    # 优化 Question 变更页：过滤器。
    list_filter = ['pub_date']
    # 在列表的顶部增加一个搜索框。
    search_fields = ['question_text']


# 向管理页面中加入投票应用
admin.site.register(Question, QuestionAdmin)
