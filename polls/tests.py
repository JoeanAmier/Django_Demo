import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question

# 运行测试: python manage.py test polls
"""
运行过程：
python manage.py test polls 将会寻找 polls 应用里的测试代码
它找到了 django.test.TestCase 的一个子类
它创建一个特殊的数据库供测试使用
它在类中寻找测试方法——以 test 开头的方法。
在 test_was_published_recently_with_future_question 方法中，它创建了一个 pub_date 值为 30 天后的 Question 实例。
接着使用 assertls() 方法，发现 was_published_recently() 返回了 True，而我们期望它返回 False。
"""


# 我们创建了一个 django.test.TestCase 的子类，并添加了一个方法
# 此方法创建一个 pub_date 时未来某天的 Question 实例。然后检查它的 was_published_recently() 方法的返回值——它 应该 是 False。
class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() 对于发布日期在将来的问题，返回False。
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() 对于发布日期早于1天的问题，返回False。
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() 对于发布日期在最后一天内的问题，返回True。
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    封装了创建投票的流程，减少了重复代码。
    用给定的“问题文本”创建一个问题，并发布到现在的给定“天数”
    （过去发布的问题为负数，尚未发布的问题为正数）。
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


# Django 提供了一个供测试使用的 Client 来模拟用户和视图层代码的交互。
# 我们能在 tests.py 甚至是 shell 中使用它。
class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        没有创建任何投票，它检查返回的网页上有没有 "No polls are available." 这段消息和 latest_question_list 是否为空。
        如果没有问题，则会显示相应的消息。
        django.test.TestCase 类提供了一些额外的 assertion 方法，在这个例子中，我们使用了 assertContains() 和 assertQuerysetEqual() 。
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        发布日期在过去的问题将显示在索引页上。
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        带有未来发布日期的问题不会显示在索引页上。
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        即使过去和将来的问题都存在，也只显示过去的问题。
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        问题索引页可能显示多个问题。
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        创建 pub_date 在未来某天的投票。数据库会在每次调用测试方法前被重置，所以第一个投票已经没了，所以主页中应该没有任何投票。
        具有未来发布日期的问题的详细视图返回404 not found。
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        创建了一个投票并检查它是否出现在列表中。
        发布日期在过去的问题的详细视图显示问题的文本。
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
