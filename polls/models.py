import datetime

from django.contrib import admin
from django.db import models
from django.utils import timezone


class Question(models.Model):  # 数据表名称
    question_text = models.CharField(max_length=200)  # 数据表字段，字符串数据类型
    pub_date = models.DateTimeField('date published')  # 数据表字段，日期时间数据类型

    # def was_published_recently(self):
    #     return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    # 相当于直接在函数上设置一些属性（用原来的、较长的名字）
    # display(*, boolean=None, ordering=None, description=None, empty_value=None)
    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def __str__(self):
        """<Question: Question object (1)> 对于我们了解这个对象的细节没什么帮助。
        让我们通过编辑 Question 模型的代码（位于 polls/models.py 中）来修复这个问题。
        给 Question 和 Choice 增加 __str__() 方法。"""
        return self.question_text


class Choice(models.Model):
    # 定义关系，每个 Choice 对象都关联到一个 Question 对象。
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
