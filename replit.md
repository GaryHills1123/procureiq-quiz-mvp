# ProcureIQ Quiz MVP

## Overview

ProcureIQ Quiz MVP is a Streamlit-based educational application designed for procurement training. The system delivers case-study quizzes that help procurement students develop core buyer competencies through interactive scenarios. Each quiz presents 10 questions from a pool of 8-12 authored questions, covering real-world procurement challenges. Upon completion, students receive a radar chart visualization showing their performance across six core competencies, along with AI-powered improvement suggestions.

The application focuses on practical procurement skills including fact-checking, cost analysis, market knowledge, negotiation tactics, supplier strategy, and continuous improvement. The MVP operates as a session-only system without data persistence, making it ideal for educational environments where students can practice and learn without the complexity of user accounts or data storage.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses Streamlit as the primary web framework, providing a clean and interactive user interface. The main application logic resides in `app.py`, which orchestrates the quiz flow, handles user interactions, and manages session state. The interface supports both single-select and multi-select questions, with built-in validation that rejects incorrect answer counts for multi-select questions and prompts users to try again.

### Core Components
The system is built around three main architectural components:

**Quiz Engine (`quiz_engine.py`)**: Handles quiz data validation, question selection, and scoring logic. The engine validates quiz structure on initialization, selects questions based on configured delivery counts, and calculates competency-based scores. It implements the business rule of delivering exactly 10 questions from the available pool while maintaining fixed question order.

**AI Helper (`ai_helper.py`)**: Provides intelligent assistance without revealing answers directly. Uses OpenAI's GPT models to offer hints, clarify concepts, and guide students through problem-solving approaches. The helper is designed to be educational rather than solution-providing, maintaining the integrity of the assessment while offering meaningful support.

**Visualization Engine (`visualization.py`)**: Creates interactive radar charts using Plotly to display student performance across the six core competencies. The visualization normalizes scores for better comparison and provides immediate visual feedback on strengths and areas for improvement.

### Data Storage Design
The system uses a file-based content management approach with JSON files stored in a structured directory hierarchy. Each quiz lives in `/content/<slug>/quiz.json`, making content management straightforward and version-controllable. The JSON schema includes comprehensive quiz metadata, learning objectives, skills catalogs, improvement rubrics, and question pools with correct answers and competency mappings.

### Session Management
The application maintains all state in Streamlit's session state, including current question position, user answers, quiz progress, and AI helper instances. This session-only approach eliminates the need for databases or user authentication while providing a complete quiz experience within a single browser session.

### Scoring and Assessment Logic
The scoring system maps each question to specific competencies and calculates weighted scores based on correct answers. Multi-select questions enforce exact count matching, rejecting submissions with incorrect numbers of selections. The system provides detailed feedback through competency-specific improvement suggestions and explanations for missed questions.

## External Dependencies

### AI Services
- **OpenAI API**: Powers the AI helper functionality through the official OpenAI Python client. Requires `OPENAI_API_KEY` environment variable. The system defaults to using GPT-5 model but can be configured via `QUIZ_OPENAI_MODEL` environment variable.

### Python Libraries
- **Streamlit (v1.37.1)**: Web application framework providing the user interface and session management
- **Plotly**: Interactive visualization library for creating radar charts and performance displays
- **JSONSchema (v4.22.0+)**: Validates quiz data structure and ensures content integrity
- **python-dotenv (v1.0.1)**: Environment variable management for configuration

### Development Platform
- **Replit**: Cloud-based development and hosting environment with automatic port configuration and secret management for API keys

### Content Format Dependencies
The system relies on a specific JSON schema for quiz content, including structured fields for questions, competency mappings, scoring rules, and improvement rubrics. This design allows for easy content authoring and management without requiring database setup or complex content management systems.