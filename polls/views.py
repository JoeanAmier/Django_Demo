from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Choice, Question


# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'polls/index.html', context)
#
#
# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})
#
#
# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/results.html', {'question': question})


def vote(request, question_id):
    """我们的 vote() 视图代码有一个小问题。代码首先从数据库中获取了 selected_choice 对象，接着计算 vote 的新值，最后把值存回数据库。
    如果网站有两个方可同时投票在 同一时间 ，可能会导致问题。同样的值，42，会被 votes 返回。然后，对于两个用户，新值43计算完毕，并被保存，但是期望值是44。
    这个问题被称为 竞争条件 。如果你对此有兴趣，你可以阅读 使用 F() 避免竞争条件 来学习如何解决这个问题。"""
    # 尝试用 get() 函数获取一个对象，如果不存在就抛出 Http404 错误
    # 也有 get_list_or_404() 函数，工作原理和 get_object_or_404() 一样，除了 get() 函数被换成了
    # filter() 函数。如果列表为空的话会抛出 Http404 异常。
    question = get_object_or_404(Question, pk=question_id)
    try:
        # request.POST 是一个类字典对象
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    # 如果在 request.POST['choice'] 数据中没有提供 choice ，POST 将引发一个 KeyError 。
    except (KeyError, Choice.DoesNotExist):
        # 重新显示问题投票窗体。
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # 总是在成功处理后返回HttpResponseRedirect
        # 带POST数据。这可以防止在用户点击后退按钮时两次发布数据。
        return HttpResponseRedirect(
            # reverse() 函数避免了我们在视图函数中硬编码 URL。
            # 它需要我们给出我们想要跳转的视图的名字和该视图所对应的 URL 模式中需要给该视图提供的参数。
            reverse(
                'polls:results', args=(
                    question.id,)))


# 改良视图，删除旧的 index, detail, 和 results 视图，并用 Django 的通用视图代替。
# 使用两个通用视图： ListView 和 DetailView 。
# 这两个视图分别抽象“显示一个对象列表”和“显示一个特定类型对象的详细信息页面”这两种概念。
class IndexView(generic.ListView):
    # 默认情况下，通用视图 DetailView 使用一个叫做 <app name>/<model name>_detail.html 的模板。
    # 在我们的例子中，它将使用 "polls/question_detail.html" 模板。template_name 属性是用来告诉 Django 使用一个指定的模板名字，而不是自动生成的默认名字。
    # 类似地，ListView 使用一个叫做 <app name>/<model name>_list.html 的默认模板。
    # 我们使用 template_name 来告诉 ListView 使用我们创建的已经存在的 "polls/index.html" 模板。
    template_name = 'polls/index.html'
    # 对于 ListView，自动生成的 context 变量是 question_list。为了覆盖这个行为，我们提供
    # context_object_name 属性，表示我们想使用 latest_question_list。
    context_object_name = 'latest_question_list'

    # def get_queryset(self):
    #     """返回最后五个已发布的问题。"""
    #     return Question.objects.order_by('-pub_date')[:5]

    def get_queryset(self):
        """
        返回最后五个已发布的问题（不包括将来将要发布的问题）。
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    # 每个通用视图需要知道它将作用于哪个模型。这由 model 属性提供。
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        就算在发布日期时未来的那些投票不会在目录页 index 里出现，但是如果用户知道或者猜到正确的 URL ，还是可以访问到它们。
        所以我们得在 DetailView 里增加一些约束：
        排除任何尚未发表的问题。
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'
