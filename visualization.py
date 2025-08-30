import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional

def create_radar_chart(scores: Dict[str, float], skills_catalog: List[Dict[str, Any]], quiz_questions: Optional[List[Dict[str, Any]]] = None) -> go.Figure:
    """Create a radar chart showing competency scores"""
    
    # Calculate maximum possible score for each competency
    max_possible_scores = {}
    if quiz_questions:
        for skill in skills_catalog:
            max_possible_scores[skill['key']] = 0.0
        
        for question in quiz_questions:
            for skill in question.get('skills', []):
                skill_key = skill['key']
                weight = skill.get('weight', 1.0)
                if skill_key in max_possible_scores:
                    max_possible_scores[skill_key] += weight
    
    # Prepare data for radar chart
    categories = []
    values = []
    
    for skill in skills_catalog:
        skill_key = skill['key']
        skill_label = skill['label']
        score = scores.get(skill_key, 0)
        max_possible = max_possible_scores.get(skill_key, 1) if quiz_questions else 1
        
        categories.append(skill_label)
        # Calculate percentage of possible score for this competency
        percentage = (score / max_possible * 100) if max_possible > 0 else 0
        values.append(percentage)
    
    # Close the radar chart by adding the first point at the end
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(0, 123, 255, 0.2)',
        line=dict(color='rgba(0, 123, 255, 1)', width=2),
        marker=dict(color='rgba(0, 123, 255, 1)', size=8),
        name='Your Performance'
    ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=20,
                ticksuffix='%'
            ),
            angularaxis=dict(
                tickfont=dict(size=12)
            )
        ),
        showlegend=True,
        title=dict(
            text="Procurement Competency Assessment",
            x=0.5,
            font=dict(size=16)
        ),
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_performance_bar_chart(scores: Dict[str, float], skills_catalog: List[Dict[str, Any]]) -> go.Figure:
    """Create a bar chart showing competency scores (alternative visualization)"""
    
    categories = []
    values = []
    
    for skill in skills_catalog:
        skill_key = skill['key']
        skill_label = skill['label']
        score = scores.get(skill_key, 0)
        
        categories.append(skill_label)
        values.append(score)
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color='rgba(0, 123, 255, 0.8)',
            text=values,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Competency Scores",
        xaxis_title="Competencies",
        yaxis_title="Score",
        height=400,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig
