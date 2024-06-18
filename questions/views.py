import json
import os
import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Result

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('questions:dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'registration/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'ユーザー登録が完了しました。')
            return redirect('questions:dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'ログアウトしました。')
    return redirect('questions:index')

@login_required
def profile_view(request):
    return render(request, 'registration/profile.html')

@login_required
def dashboard_view(request):
    return render(request, 'registration/dashboard.html')

@login_required
def mock_exam_view(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_file_path = os.path.join(BASE_DIR, 'questions', 'data', 'part5_questions.json')

    with open(json_file_path, 'r', encoding='utf-8') as file:
        questions = json.load(file)

    selected_questions = random.sample(questions, 30)

    context = {
        'questions': selected_questions,
    }

    return render(request, 'questions/mock_exam.html', context)

@login_required
def submit_answer(request):
    if request.method == 'POST':
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_file_path = os.path.join(BASE_DIR, 'questions', 'data', 'part5_questions.json')

        with open(json_file_path, 'r', encoding='utf-8') as file:
            questions = json.load(file)

        score = 0
        user_answers = {}
        selected_questions = random.sample(questions, 30)  # ここで30問を選ぶ
        for question in selected_questions:
            q_id = f'question_{question["id"]}'
            user_answer = request.POST.get(q_id)
            if user_answer == question["correct_answer"]:
                score += 1
            user_answers[q_id] = user_answer

        results = []
        category_scores = {}  # カテゴリごとの正答数を保存するための辞書
        for question in selected_questions:
            q_id = f'question_{question["id"]}'
            results.append({
                'question_text': question["question_text"],
                'correct_answer': question["correct_answer"],
                'user_answer': user_answers[q_id],
                'explanation': question["explanation"],
                'category': question["category"]
            })
            category = question["category"]
            if category not in category_scores:
                category_scores[category] = {'correct': 0, 'total': 0}
            category_scores[category]['total'] += 1
            if user_answers[q_id] == question["correct_answer"]:
                category_scores[category]['correct'] += 1

        # カテゴリごとの正答率を計算
        for category in category_scores:
            category_scores[category]['percentage'] = (category_scores[category]['correct'] / category_scores[category]['total']) * 100

        # ユーザーの回答をResultモデルに保存
        Result.objects.create(user=request.user, score=score, user_answers=user_answers)

        return render(request, 'questions/results.html', {
            'score': score,
            'results': results,
            'category_scores': category_scores,
        })



@login_required
def results_view(request):
    results = Result.objects.filter(user=request.user).order_by('-date_taken')[:5]  # 直近5回の結果を取得
    scores = []
    all_categories = set()

    for result in results:
        user_answers = result.user_answers
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_file_path = os.path.join(BASE_DIR, 'questions', 'data', 'part5_questions.json')

        with open(json_file_path, 'r', encoding='utf-8') as file:
            questions = json.load(file)

        category_correct_counts = {}
        for question in questions:
            category = question["category"]
            all_categories.add(category)
            q_id = f'question_{question["id"]}'
            if user_answers.get(q_id) == question["correct_answer"]:
                if category not in category_correct_counts:
                    category_correct_counts[category] = 0
                category_correct_counts[category] += 1

        scores.append(category_correct_counts)

    all_categories = list(all_categories)

    return render(request, 'questions/results.html', {
        'results': results,
        'scores': scores,
        'categories': all_categories,
    })





@login_required
def review_mistakes_view(request):
    results = Result.objects.filter(user=request.user).latest('date_taken')
    
    user_answers = results.user_answers
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_file_path = os.path.join(BASE_DIR, 'questions', 'data', 'part5_questions.json')

    with open(json_file_path, 'r', encoding='utf-8') as file:
        questions = json.load(file)

    mistakes = []
    for question in questions:
        user_answer = user_answers.get(f'question_{question["id"]}')
        if user_answer != question["correct_answer"]:
            mistakes.append({
                "question_text": question["question_text"],
                "user_answer": user_answer,
                "correct_answer": question["correct_answer"]
            })

    return render(request, 'questions/review_mistakes.html', {'mistakes': mistakes})
