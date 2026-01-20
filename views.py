from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Course, Lesson, Question, Choice, Submission


@login_required
def submit(request, course_id):
    """
    Handles exam submission and saves selected choices.
    """
    course = get_object_or_404(Course, pk=course_id)

    # Create a new submission for the logged-in user
    submission = Submission.objects.create(user=request.user)

    # Get selected choices from POST data
    selected_choice_ids = request.POST.getlist('choice')

    for choice_id in selected_choice_ids:
        choice = get_object_or_404(Choice, pk=choice_id)
        submission.choices.add(choice)

    submission.save()

    # Redirect to exam result page
    return HttpResponseRedirect(
        reverse('onlinecourse:exam_result', args=(course.id, submission.id))
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    """
    Evaluates the exam and displays result.
    """
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    total_score = 0
    score = 0

    questions = Question.objects.filter(lesson__course=course)

    for question in questions:
        total_score += question.grade

        correct_choices = question.choices.filter(is_correct=True)
        selected_choices = submission.choices.filter(question=question)

        # Check if selected choices exactly match correct choices
        if set(correct_choices) == set(selected_choices):
            score += question.grade

    context = {
        'course': course,
        'score': score,
        'total_score': total_score,
        'passed': score >= total_score * 0.5
    }

    return render(request, 'course/exam_result.html', context)
