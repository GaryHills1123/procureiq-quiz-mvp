import os
import json
from typing import Dict, Any, List
from openai import OpenAI

class AIHelper:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        # Use a reliable OpenAI model for production
        self.model = os.getenv("QUIZ_OPENAI_MODEL", "gpt-4o-mini")
    
    def get_help(self, question: Dict[str, Any], help_request: str) -> str:
        """Get AI-powered help for a specific question"""
        
        # Prepare context without revealing the answer
        context = f"""
        Question: {question['stem']}
        
        Options:
        """
        
        for i, option in enumerate(question['options']):
            context += f"{i + 1}. {option}\n"
        
        if question['type'] == 'multi':
            context += f"\nNote: This is a multi-select question. Select exactly {question['select_count']} options.\n"
        
        # Add hints if available
        if 'hints' in question and question['hints']:
            context += f"\nAvailable hints: {', '.join(question['hints'])}\n"
        
        prompt = f"""
        You are a procurement training assistant. A student is working on a procurement case study quiz and needs help with this question.
        
        {context}
        
        Student's request: {help_request}
        
        Provide helpful guidance without directly revealing the answer. You can:
        - Provide hints about the approach or reasoning
        - Clarify terminology or concepts
        - Explain the context or scenario
        - Point out important factors to consider
        
        Keep your response concise and educational. Do not directly state which option(s) are correct.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful procurement training assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else "Unable to provide help at this time."
            
        except Exception as e:
            raise Exception(f"Failed to get AI help: {e}")
    
    def get_improvement_suggestions(self, scores: Dict[str, float], skills_catalog: List[Dict[str, Any]], improvement_rubric: Dict[str, List[str]]) -> Dict[str, str]:
        """Generate personalized improvement suggestions based on performance"""
        
        # Calculate performance levels
        max_possible_per_skill = max(scores.values()) if scores.values() else 1
        performance_data = {}
        
        for skill in skills_catalog:
            skill_key = skill['key']
            skill_label = skill['label']
            score = scores.get(skill_key, 0)
            performance_level = (score / max_possible_per_skill * 100) if max_possible_per_skill > 0 else 0
            
            performance_data[skill_key] = {
                'label': skill_label,
                'score': score,
                'performance_level': performance_level,
                'rubric_items': improvement_rubric.get(skill_key, [])
            }
        
        prompt = f"""
        You are a procurement training expert. Analyze this student's quiz performance and provide personalized improvement suggestions.
        
        Performance Data:
        {json.dumps(performance_data, indent=2)}
        
        For each competency, provide specific, actionable improvement suggestions based on:
        1. The student's performance level in that area
        2. The improvement rubric items provided
        3. Your expertise in procurement best practices
        
        Focus on the 2-3 areas where improvement would have the most impact. Make suggestions practical and specific.
        
        Respond in JSON format with skill keys as top-level keys and improvement text as values:
        {{"skill_key": "specific improvement suggestion text", ...}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a procurement training expert providing personalized feedback."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=800,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            if content:
                suggestions = json.loads(content)
            else:
                suggestions = {}
            return suggestions
            
        except Exception as e:
            # Fallback to rubric-based suggestions if AI fails
            fallback_suggestions = {}
            for skill_key, data in performance_data.items():
                if data['performance_level'] < 70:  # Focus on lower performing areas
                    fallback_suggestions[skill_key] = f"Focus on: {', '.join(data['rubric_items'][:2])}"
            
            return fallback_suggestions if fallback_suggestions else {"general": "Continue practicing procurement case studies to improve overall performance."}
