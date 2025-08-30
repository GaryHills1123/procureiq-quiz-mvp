# ProcureIQ Quiz MVP

A Streamlit-based procurement training platform featuring case-study quizzes with AI-powered hints, competency assessment via radar charts, and personalized improvement suggestions.

## Features

- **Interactive Case Studies**: Scenario-based procurement training with real-world challenges
- **AI-Powered Assistance**: Contextual hints and guidance without revealing answers
- **Competency Assessment**: Performance tracking across 6 core procurement skills
- **Visual Analytics**: Radar chart visualization of competency scores
- **Personalized Learning**: AI-generated improvement suggestions based on performance

## Core Competencies Assessed

1. **Check the Facts** - Data verification and analysis skills
2. **Break Down the Costs** - Cost analysis and financial evaluation
3. **Know the Market** - Market research and industry knowledge
4. **Negotiate for Value** - Strategic negotiation techniques
5. **Choose the Right Supplier Strategy** - Supplier selection and management
6. **Learn and Improve** - Continuous improvement and adaptation

## Tech Stack

- **Frontend**: Streamlit
- **AI Integration**: OpenAI API (GPT-5)
- **Visualization**: Plotly
- **Data Validation**: JSONSchema
- **Environment**: Python 3.11+

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install streamlit openai plotly jsonschema python-dotenv
   ```
3. Set up environment variables:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```
4. Run the application:
   ```bash
   streamlit run app.py --server.port 5000 --server.address 0.0.0.0
   ```

## Project Structure

```
├── app.py                 # Main Streamlit application
├── quiz_engine.py         # Quiz logic and scoring engine
├── ai_helper.py          # OpenAI integration for hints and suggestions
├── visualization.py      # Radar chart generation
├── content/              # Quiz content directory
│   └── resisting-price-increases/
│       └── quiz.json     # Sample quiz data
└── .streamlit/
    └── config.toml       # Streamlit configuration
```

## Usage

1. **Start a Quiz**: Select from available case studies
2. **Answer Questions**: Navigate through scenario-based questions
3. **Get Help**: Use the AI assistant for hints and clarification
4. **View Results**: See competency scores and improvement suggestions
5. **Restart**: Take another quiz to continue learning

## Quiz Content Format

Quiz content is stored in JSON format with:
- Case study scenarios and context
- Multiple choice and multi-select questions
- Competency mappings for each question
- Detailed explanations and learning objectives
- Improvement rubrics for personalized feedback

## Contributing

This is an MVP designed for educational use. The system operates session-only without data persistence, making it ideal for training environments.

## License

MIT License