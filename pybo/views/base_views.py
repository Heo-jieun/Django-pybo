from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from ..models import Question
from django.db.models import Count

def index(request):
    sort = request.GET.get('sort', '')  # URL의 쿼리스트링을 가져온다. 없는 경우 공백을 리턴한다
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어

    # 기본 질문 목록 쿼리
    question_list = Question.objects.annotate(voter_count=Count('voter'))

    # 정렬 조건에 따른 질문 목록 정렬
    if sort == 'voter':
        question_list = question_list.order_by('-voter_count', '-create_date')
    elif sort == 'mypost' and request.user.is_authenticated:
        question_list = question_list.filter(author=request.user).order_by('-create_date')
    else:
        question_list = question_list.order_by('-create_date')

    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |  # 제목 검색
            Q(content__icontains=kw) |  # 내용 검색
            Q(answer__content__icontains=kw) |  # 답변 내용 검색
            Q(author__username__icontains=kw) |  # 질문 글쓴이 검색
            Q(answer__author__username__icontains=kw)  # 답변 글쓴이 검색
        ).distinct()

    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)
    context = {'question_list': page_obj, 'page': page, 'kw': kw, 'sort': sort}
    return render(request, 'pybo/question_list.html', context)

def detail(request, question_id ):
    question = get_object_or_404(Question, pk = question_id)
    context = {'question':question}
    return render(request, 'pybo/question_detail.html', context)
