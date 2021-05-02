from django.urls import path

from . import views

app_name = 'polls'  # 为 URL 名称添加命名空间

# question_id 定义了将被用于区分匹配模式的变量名
# int: 决定了应该以什么变量类型匹配这部分的 URL 路径
# urlpatterns = [
#     path('', views.index, name='index'),
#     path('<int:question_id>/', views.detail, name='detail'),
#     path('<int:question_id>/results/', views.results, name='results'),
#     path('<int:question_id>/vote/', views.vote, name='vote'),
# ]

# 改良 URLconf
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
