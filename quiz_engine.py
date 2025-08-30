import json
import random
from typing import Dict, List, Any
from jsonschema import validate, ValidationError

class QuizEngine:
    def __init__(self, quiz_data: Dict[str, Any]):
        self.quiz_data = quiz_data
        self.validate_quiz_data()
        self.selected_questions = self.select_questions()
    
    def validate_quiz_data(self):
        """Validate quiz data structure"""
        required_fields = ['questions', 'skills_catalog', 'scoring']
        for field in required_fields:
            if field not in self.quiz_data:
                raise ValueError(f"Missing required field: {field}")
        
        if len(self.quiz_data['questions']) < 8:
            raise ValueError("Quiz must have at least 8 questions")
    
    def select_questions(self) -> List[Dict[str, Any]]:
        """Select 10 questions from available pool and shuffle their options"""
        import random
        
        all_questions = self.quiz_data['questions'].copy()
        deliver_count = self.quiz_data['scoring'].get('deliver_count', 10)
        
        if len(all_questions) <= deliver_count:
            selected_questions = all_questions
        else:
            # For MVP, we'll keep questions in order but only take the first 10
            # This maintains the "fixed order" requirement mentioned in the spec
            selected_questions = all_questions[:deliver_count]
        
        # Shuffle answer options for each question to prevent patterns
        for question in selected_questions:
            self._shuffle_question_options(question)
            
        return selected_questions
    
    def _shuffle_question_options(self, question):
        """Shuffle answer options and update indices accordingly"""
        import random
        
        if question['type'] == 'single':
            # Create list of (option, is_correct) pairs
            options_with_correctness = [(option, i == question['answer_index']) 
                                       for i, option in enumerate(question['options'])]
            
            # Shuffle the pairs
            random.shuffle(options_with_correctness)
            
            # Extract shuffled options and find new correct index
            shuffled_options = [option for option, _ in options_with_correctness]
            new_answer_index = next(i for i, (_, is_correct) in enumerate(options_with_correctness) if is_correct)
            
            # Update question
            question['options'] = shuffled_options
            question['answer_index'] = new_answer_index
            
        elif question['type'] == 'multi':
            # Create list of (option, is_correct) pairs
            correct_indices = set(question['answer_indices'])
            options_with_correctness = [(option, i in correct_indices) 
                                       for i, option in enumerate(question['options'])]
            
            # Shuffle the pairs
            random.shuffle(options_with_correctness)
            
            # Extract shuffled options and find new correct indices
            shuffled_options = [option for option, _ in options_with_correctness]
            new_answer_indices = [i for i, (_, is_correct) in enumerate(options_with_correctness) if is_correct]
            
            # Update question
            question['options'] = shuffled_options
            question['answer_indices'] = new_answer_indices
    
    def calculate_scores(self, user_answers: Dict[str, Any]) -> Dict[str, float]:
        """Calculate scores by competency"""
        competency_scores = {}
        
        # Initialize scores for all competencies
        for skill in self.quiz_data['skills_catalog']:
            competency_scores[skill['key']] = 0.0
        
        for question in self.selected_questions:
            question_id = question['id']
            if question_id not in user_answers:
                continue
            
            user_answer = user_answers[question_id]
            is_correct = self.is_answer_correct(question, user_answer)
            
            if is_correct:
                # Distribute points based on skill weights
                for skill in question.get('skills', []):
                    skill_key = skill['key']
                    weight = skill.get('weight', 1.0)
                    if skill_key in competency_scores:
                        competency_scores[skill_key] += weight
        
        return competency_scores
    
    def is_answer_correct(self, question: Dict[str, Any], user_answer: Any) -> bool:
        """Check if user answer is correct"""
        if question['type'] == 'single':
            return user_answer == question['answer_index']
        elif question['type'] == 'multi':
            if not isinstance(user_answer, list):
                return False
            
            # Check if user selected exactly the right count
            if len(user_answer) != question['select_count']:
                return False
            
            # Check if all selected answers are correct
            correct_indices = set(question['answer_indices'])
            user_indices = set(user_answer)
            return user_indices == correct_indices
        
        return False
    
    def get_missed_questions(self, user_answers: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of questions user answered incorrectly"""
        missed = []
        
        for question in self.selected_questions:
            question_id = question['id']
            if question_id not in user_answers:
                continue
            
            user_answer = user_answers[question_id]
            if not self.is_answer_correct(question, user_answer):
                # Format missed question with additional info
                missed_q = question.copy()
                
                if question['type'] == 'single':
                    user_answer_text = question['options'][user_answer] if user_answer < len(question['options']) else "Invalid"
                    correct_answer_text = question['options'][question['answer_index']]
                elif question['type'] == 'multi':
                    user_answer_text = [question['options'][i] for i in user_answer if i < len(question['options'])]
                    correct_answer_text = [question['options'][i] for i in question['answer_indices']]
                else:
                    user_answer_text = "Unknown"
                    correct_answer_text = "Unknown"
                
                missed_q['user_answer_text'] = user_answer_text
                missed_q['correct_answer_text'] = correct_answer_text
                
                missed.append(missed_q)
        
        return missed
