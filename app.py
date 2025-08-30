import streamlit as st
import json
import os
import random
from pathlib import Path
from quiz_engine import QuizEngine
from ai_helper import AIHelper
from visualization import create_radar_chart

# Configure page
st.set_page_config(
    page_title="ProcureIQ Quiz MVP",
    page_icon="📋",
    layout="wide"
)

def load_available_quizzes():
    """Load all available quiz files from content directory"""
    content_dir = Path("content")
    quizzes = {}
    
    if content_dir.exists():
        for quiz_dir in content_dir.iterdir():
            if quiz_dir.is_dir():
                quiz_file = quiz_dir / "quiz.json"
                if quiz_file.exists():
                    try:
                        with open(quiz_file, 'r') as f:
                            quiz_data = json.load(f)
                        quizzes[quiz_data['slug']] = {
                            'title': quiz_data['title'],
                            'file_path': str(quiz_file),
                            'data': quiz_data
                        }
                    except Exception as e:
                        st.error(f"Error loading quiz from {quiz_file}: {e}")
    
    return quizzes

def initialize_session_state():
    """Initialize session state variables"""
    if 'quiz_engine' not in st.session_state:
        st.session_state.quiz_engine = None
    if 'ai_helper' not in st.session_state:
        try:
            st.session_state.ai_helper = AIHelper()
            st.session_state.ai_helper_error = None
        except Exception as e:
            st.session_state.ai_helper = None
            st.session_state.ai_helper_error = str(e)
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'selected_quiz' not in st.session_state:
        st.session_state.selected_quiz = None
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = "test user"

def reset_quiz_state():
    """Reset quiz-related session state"""
    st.session_state.current_question = 0
    st.session_state.user_answers = {}
    st.session_state.quiz_completed = False
    st.session_state.quiz_started = False
    st.session_state.quiz_engine = None

def display_quiz_selection(available_quizzes):
    """Display quiz selection interface"""
    st.title("ProcureIQ Quiz MVP")
    
    # Intro to ProcureIQ
    st.subheader("Intro to ProcureIQ")
    st.write("""
    Welcome to ProcureIQ, your interactive procurement training platform! Our case-study quizzes help you develop essential buyer competencies through real-world scenarios.
    
    **What you'll learn:**
    - **Check the Facts** - Data verification and analysis skills
    - **Break Down the Costs** - Cost analysis and financial evaluation  
    - **Know the Market** - Market research and industry knowledge
    - **Negotiate for Value** - Strategic negotiation techniques
    - **Choose the Right Supplier Strategy** - Supplier selection and management
    - **Learn and Improve** - Continuous improvement and adaptation
    
    Each quiz presents 10 questions that test your procurement decision-making. You'll receive a competency assessment with visual feedback and personalized improvement suggestions.
    """)
    
    st.write("Select a case study quiz to begin your procurement training.")
    
    if not available_quizzes:
        st.error("No quiz files found. Please ensure quiz data is available in the content directory.")
        return
    
    quiz_options = {quiz['title']: slug for slug, quiz in available_quizzes.items()}
    
    selected_title = st.selectbox(
        "Choose a case study:",
        options=list(quiz_options.keys()),
        key="quiz_selector"
    )
    
    if selected_title:
        selected_slug = quiz_options[selected_title]
        quiz_data = available_quizzes[selected_slug]['data']
        
        if st.button("Start Quiz", type="primary"):
            st.session_state.selected_quiz = selected_slug
            st.session_state.quiz_engine = QuizEngine(quiz_data)
            # Reset only the quiz progress, not the started state
            st.session_state.current_question = 0
            st.session_state.user_answers = {}
            st.session_state.quiz_completed = False
            st.session_state.quiz_started = True
            st.rerun()

def display_question():
    """Display current question with options"""
    quiz_engine = st.session_state.quiz_engine
    current_q_idx = st.session_state.current_question
    
    # Safety check - if quiz engine is not ready, return to selection
    if quiz_engine is None:
        st.error("Quiz not properly initialized. Please select a quiz again.")
        reset_quiz_state()
        st.rerun()
        return
    
    if current_q_idx >= len(quiz_engine.selected_questions):
        st.session_state.quiz_completed = True
        st.rerun()
        return
    
    question = quiz_engine.selected_questions[current_q_idx]
    
    # Progress bar
    progress = (current_q_idx + 1) / len(quiz_engine.selected_questions)
    st.progress(progress)
    st.write(f"Question {current_q_idx + 1} of {len(quiz_engine.selected_questions)}")
    
    # Display scenario context
    with st.expander("📋 Case Study Scenario (Click to view)", expanded=current_q_idx == 0):
        st.write("**Scenario:**")
        st.write(quiz_engine.quiz_data['scenario'])
        
        st.write("**Learning Objectives:**")
        for objective in quiz_engine.quiz_data['learning_objectives']:
            st.write(f"• {objective}")
            
        # Display data tables if available
        if 'data_tables' in quiz_engine.quiz_data:
            st.write("**📊 Reference Data:**")
            for table in quiz_engine.quiz_data['data_tables']:
                with st.expander(f"📈 {table['title']}", expanded=False):
                    st.write(f"*{table['description']}*")
                    
                    # Create DataFrame for better display
                    import pandas as pd
                    df = pd.DataFrame(table['rows'], columns=table['headers'])
                    st.dataframe(df, width='stretch')
    
    # Question stem
    st.subheader(question['stem'])
    
    # Display options based on question type
    if question['type'] == 'single':
        # Single select with default "choose one" option
        options_with_default = [-1] + list(range(len(question['options'])))
        
        def format_option(x):
            if x == -1:
                return "— Choose one of the following —"
            return question['options'][x]
        
        answer = st.radio(
            "Select one option:",
            options=options_with_default,
            format_func=format_option,
            key=f"q_{question['id']}"
        )
        
        # Only save valid answers (not the default)
        if answer != -1:
            st.session_state.user_answers[question['id']] = answer
        elif question['id'] in st.session_state.user_answers:
            # Remove any previous answer if back to default
            del st.session_state.user_answers[question['id']]
        
    elif question['type'] == 'multi':
        # Multi select
        st.write(f"Select exactly {question['select_count']} options:")
        answers = []
        for i, option in enumerate(question['options']):
            if st.checkbox(option, key=f"q_{question['id']}_option_{i}"):
                answers.append(i)
        
        # Validate selection count
        if len(answers) != question['select_count'] and len(answers) > 0:
            st.warning(f"Please select exactly {question['select_count']} options. You have selected {len(answers)}.")
        
        st.session_state.user_answers[question['id']] = answers
    
    # AI Helper section
    st.subheader("Need Help?")
    
    # Check if AI helper is available
    if st.session_state.ai_helper_error:
        st.error(f"AI Help not available: {st.session_state.ai_helper_error}")
        return
    
    if not st.session_state.ai_helper:
        st.error("AI Helper not initialized. Please refresh the page.")
        return
    
    # Use a form so Enter key submits the help request
    with st.form(key=f"help_form_{question['id']}"):
        help_request = st.text_input(
            "Ask for a hint or clarification:",
            placeholder="e.g., 'provide a hint', 'clarify option 2', 'explain the context'"
        )
        help_submitted = st.form_submit_button("Get Help")
        
        if help_submitted:
            if not help_request.strip():
                st.error("Please enter a question or request for help.")
            else:
                with st.spinner("Getting AI assistance..."):
                    try:
                        help_response = st.session_state.ai_helper.get_help(question, help_request)
                        st.success("AI Response:")
                        st.info(help_response)
                    except Exception as e:
                        st.error(f"Error getting AI help: {str(e)}")
                        st.write("Please try again or contact support if the issue persists.")
    
    # Navigation buttons - always visible for consistency
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # Check if current question has a valid answer
    has_valid_answer = False
    if question['id'] in st.session_state.user_answers:
        answer = st.session_state.user_answers[question['id']]
        if question['type'] == 'multi':
            has_valid_answer = len(answer) == question['select_count']
        else:
            has_valid_answer = True
    
    with col1:
        if st.button("Previous", disabled=current_q_idx == 0):
            st.session_state.current_question -= 1
            st.rerun()
    
    with col2:
        is_last_question = current_q_idx >= len(quiz_engine.selected_questions) - 1
        if st.button("Next", disabled=is_last_question or not has_valid_answer):
            st.session_state.current_question += 1
            st.rerun()
    
    with col3:
        if st.button("Finish Quiz", disabled=not has_valid_answer):
            st.session_state.quiz_completed = True
            st.rerun()
    
    # Show helpful message if answer not selected
    if not has_valid_answer:
        if question['type'] == 'multi':
            st.info(f"💡 Please select exactly {question['select_count']} options to proceed.")
        else:
            st.info("💡 Please select an answer to proceed.")

def display_results():
    """Display quiz results with radar chart and improvement suggestions"""
    quiz_engine = st.session_state.quiz_engine
    
    # Calculate scores
    scores = quiz_engine.calculate_scores(st.session_state.user_answers)
    
    st.title("Quiz Results")
    
    # Overall score
    total_score = sum(scores.values())
    max_possible = len(quiz_engine.selected_questions)
    percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0
    
    st.metric("Overall Score", f"{total_score}/{max_possible}", f"{percentage:.1f}%")
    
    # Radar chart
    st.subheader("Competency Assessment")
    fig = create_radar_chart(scores, quiz_engine.quiz_data['skills_catalog'], quiz_engine.selected_questions)
    st.plotly_chart(fig, use_container_width=True)
    
    # AI-generated improvement suggestions (only for scores 90% or below)
    if percentage <= 90:
        st.subheader("Improvement Suggestions")
        with st.spinner("Generating personalized improvement suggestions..."):
            try:
                suggestions = st.session_state.ai_helper.get_improvement_suggestions(
                    scores, 
                    quiz_engine.quiz_data['skills_catalog'],
                    quiz_engine.quiz_data['improvement_rubric']
                )
                
                for skill_key, suggestion in suggestions.items():
                    skill_label = next(
                        (skill['label'] for skill in quiz_engine.quiz_data['skills_catalog'] 
                         if skill['key'] == skill_key), 
                        skill_key
                    )
                    st.write(f"**{skill_label}:**")
                    st.write(suggestion)
                    st.write("")
                    
            except Exception as e:
                st.error(f"Error generating improvement suggestions: {e}")
    else:
        st.success("🌟 Excellent performance! You've demonstrated strong competency across all areas.")
    
    # Quiz completion analysis
    st.subheader("Review")
    missed_questions = quiz_engine.get_missed_questions(st.session_state.user_answers)
    total_questions = len(quiz_engine.selected_questions)
    answered_questions = len(st.session_state.user_answers)
    
    if answered_questions == total_questions and len(missed_questions) == 0:
        st.success("🎉 Congratulations! You answered all questions correctly!")
    elif answered_questions < total_questions:
        st.info(f"📝 Quiz completed early - you answered {answered_questions} out of {total_questions} questions.")
        if missed_questions:
            st.write("**Questions you got wrong:**")
            for question in missed_questions:
                with st.expander(f"Question: {question['stem']}"):
                    st.write(f"**Your answer:** {question['user_answer_text']}")
                    st.write(f"**Correct answer:** {question['correct_answer_text']}")
                    st.write(f"**Explanation:** {question['explain']}")
    else:
        st.write("**Questions you got wrong:**")
        for question in missed_questions:
            with st.expander(f"Question: {question['stem']}"):
                st.write(f"**Your answer:** {question['user_answer_text']}")
                st.write(f"**Correct answer:** {question['correct_answer_text']}")
                st.write(f"**Explanation:** {question['explain']}")
    
    # Restart option
    if st.button("Take Another Quiz"):
        reset_quiz_state()
        st.rerun()

def main():
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        # User identification
        user_name = st.text_input("User Name:", value=st.session_state.user_name, key="user_name_input")
        st.session_state.user_name = user_name
        
        available_quizzes = load_available_quizzes()
        
        if st.session_state.quiz_started and st.session_state.selected_quiz:
            quiz_title = available_quizzes[st.session_state.selected_quiz]['title']
            st.write(f"**Current Quiz:** {quiz_title}")
            
            if not st.session_state.quiz_completed and st.session_state.quiz_engine:
                st.write(f"**Progress:** {st.session_state.current_question + 1}/{len(st.session_state.quiz_engine.selected_questions)}")
            
            if st.button("Return to Quiz Selection"):
                reset_quiz_state()
                st.rerun()
        
        st.write("---")
        st.write("**Core Competencies:**")
        competencies = [
            "Check the Facts",
            "Break Down the Costs", 
            "Know the Market",
            "Negotiate for Value",
            "Choose the Right Supplier Strategy",
            "Learn and Improve"
        ]
        for comp in competencies:
            st.write(f"• {comp}")
    
    # Main content
    if not st.session_state.quiz_started:
        display_quiz_selection(available_quizzes)
    elif st.session_state.quiz_completed:
        display_results()
    else:
        display_question()

if __name__ == "__main__":
    main()
