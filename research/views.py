from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import (
    ResearchSession,
    ClarificationQuestion,
    UserResponse,
    ResearchResponse,
    ResearchNote
)
from ai_service.client_factory import get_claude_client
from ai_service.models import TokenUsageLog
from ai_service.utils import calculate_cost
import json
import logging
import markdown

logger = logging.getLogger(__name__)


def home(request):
    """Home page with question form"""
    recent_sessions = ResearchSession.objects.all()[:5]
    return render(request, 'research/home.html', {
        'recent_sessions': recent_sessions
    })


def ask_question(request):
    """Handle question submission and generate clarifications"""
    if request.method != 'POST':
        return redirect('research:home')

    question = request.POST.get('question', '').strip()

    if not question:
        return render(request, 'research/home.html', {
            'error': 'Please enter a question.',
            'question': question
        })

    # Create research session
    session = ResearchSession.objects.create(
        title=question[:200],  # Use first 200 chars as title
        original_question=question,
        status='in_progress'
    )

    # Generate clarifications using AI client
    client = get_claude_client()
    response = client.generate_clarifications(question)

    if not response.success:
        logger.error(f"Failed to generate clarifications: {response.error_message}")
        return render(request, 'research/home.html', {
            'error': f'Error generating clarifications: {response.error_message}',
            'question': question
        })

    # Log token usage
    TokenUsageLog.objects.create(
        endpoint='clarify',
        model=response.token_usage.model,
        prompt_tokens=response.token_usage.prompt_tokens,
        completion_tokens=response.token_usage.completion_tokens,
        total_tokens=response.token_usage.total_tokens,
        cost_estimate=calculate_cost(response.token_usage),
        session=session
    )

    # Parse clarifications and create questions
    try:
        clarifications = json.loads(response.content)
        for i, q_text in enumerate(clarifications, 1):
            ClarificationQuestion.objects.create(
                session=session,
                question_text=q_text,
                order=i
            )
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse clarifications JSON: {e}")
        return render(request, 'research/home.html', {
            'error': 'Error processing AI response. Please try again.',
            'question': question
        })

    # Redirect to clarification page
    return redirect('research:clarifications', session_id=session.id)


def clarifications(request, session_id):
    """Display clarification questions"""
    session = get_object_or_404(ResearchSession, id=session_id)
    clarifications = session.clarifications.all()

    return render(request, 'research/clarifications.html', {
        'session': session,
        'clarifications': clarifications
    })


def submit_clarifications(request, session_id):
    """Handle clarification responses and generate research"""
    if request.method != 'POST':
        return redirect('research:clarifications', session_id=session_id)

    session = get_object_or_404(ResearchSession, id=session_id)
    clarifications = session.clarifications.all()

    # Save user responses
    user_context = []
    for clarification in clarifications:
        answer_key = f'answer_{clarification.id}'
        answer = request.POST.get(answer_key, '').strip()

        if not answer:
            return render(request, 'research/clarifications.html', {
                'session': session,
                'clarifications': clarifications,
                'error': 'Please answer all questions.'
            })

        # Save response
        UserResponse.objects.create(
            clarification=clarification,
            response_text=answer
        )

        user_context.append({
            'question': clarification.question_text,
            'answer': answer
        })

    # Generate research response
    client = get_claude_client()
    response = client.generate_response(session.original_question, user_context)

    if not response.success:
        logger.error(f"Failed to generate response: {response.error_message}")
        return render(request, 'research/clarifications.html', {
            'session': session,
            'clarifications': clarifications,
            'error': f'Error generating research: {response.error_message}'
        })

    # Log token usage
    TokenUsageLog.objects.create(
        endpoint='respond',
        model=response.token_usage.model,
        prompt_tokens=response.token_usage.prompt_tokens,
        completion_tokens=response.token_usage.completion_tokens,
        total_tokens=response.token_usage.total_tokens,
        cost_estimate=calculate_cost(response.token_usage),
        session=session
    )

    # Parse and save response
    try:
        data = json.loads(response.content)

        # Convert markdown to HTML for detailed response
        md = markdown.Markdown(extensions=['extra', 'nl2br'])
        detailed_html = md.convert(data.get('analysis', ''))

        ResearchResponse.objects.create(
            session=session,
            summary=data.get('summary', ''),
            detailed_response=detailed_html,
            links=data.get('links', []),
            token_count=response.token_usage.total_tokens
        )

        # Mark session as completed
        session.status = 'completed'
        session.save()

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse response JSON: {e}")
        return render(request, 'research/clarifications.html', {
            'session': session,
            'clarifications': clarifications,
            'error': 'Error processing AI response. Please try again.'
        })

    # Redirect to response page
    return redirect('research:session_detail', session_id=session.id)


def session_detail(request, session_id):
    """Display session and response"""
    session = get_object_or_404(ResearchSession, id=session_id)

    if not hasattr(session, 'response'):
        # Session not completed yet
        if session.clarifications.exists():
            return redirect('research:clarifications', session_id=session.id)
        else:
            return redirect('research:home')

    return render(request, 'research/response.html', {
        'session': session,
        'response': session.response
    })


def session_list(request):
    """List all research sessions"""
    sessions = ResearchSession.objects.all()
    return render(request, 'research/session_list.html', {
        'sessions': sessions
    })


def add_note(request, session_id):
    """Add a note to a research session"""
    if request.method != 'POST':
        return redirect('research:session_detail', session_id=session_id)

    session = get_object_or_404(ResearchSession, id=session_id)
    note_text = request.POST.get('note_text', '').strip()

    if note_text:
        ResearchNote.objects.create(
            session=session,
            note_text=note_text
        )

    return redirect('research:session_detail', session_id=session.id)
