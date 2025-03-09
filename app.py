import streamlit as st
import os
import json
import time
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Page configuration
st.set_page_config(
    page_title="Agent Assisted Discovery",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def local_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    local_css("style.css")
except FileNotFoundError:
    st.warning("style.css not found. Using default styling.")

# Static questions for technical context
STATIC_QUESTIONS = [
    "Can you describe the general layout of your organization's IT infrastructure and key technologies currently in use?",
    "How are your current technologies integrated, and are there any legacy systems in use? How do these systems coexist and communicate?",
    "What strategies do you employ for data management and security, and how do you handle data compliance?",
    "How does your organization approach and adapt to new technological changes or trends?",
    "What are the most significant IT challenges your organization faces, and how are you addressing them?",
    "How does your IT strategy align with your overall business objectives?",
    "What does your future technology roadmap look like, and what key upgrades or changes are you planning?"
]

# Initialize session state variables
if 'initialized' not in st.session_state:
    st.session_state.qa_pairs = []
    st.session_state.generated_questions = []
    st.session_state.global_context = ""
    st.session_state.dynamic_context = ""
    st.session_state.set_iteration = 1
    st.session_state.summary = ""
    st.session_state.next_steps = ""
    st.session_state.model = "gpt-4o"  # Default model
    st.session_state.initialized = True

# Function to generate questions, summaries, or next steps using OpenAI
def generate_content(context, request_type):
    if not openai.api_key:
        return "Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
    
    prompts = {
        'summary': "Provide a concise technical summary of the following information, highlighting key system architectures, technological integrations, and any potential areas of improvement:\n\n{}",
        'next_steps': "Outline the next steps a Systems Engineer should take considering the current technical infrastructure, focusing on areas like system upgrades, integration challenges, and potential technological advancements:\n\n{}",
        'questions': "Generate exactly 7 targeted technical discovery questions based on this information, focusing on system architecture, data security, and technology management. Ensure each question is concise, specific, and requires only a single-part answer. Format each question on a new line with a question mark at the end:\n\n{}"
    }
    
    formatted_prompt = prompts[request_type].format(context)
    
    try:
        with st.spinner(f"Generating {request_type}..."):
            response = openai.chat.completions.create(
                model=st.session_state.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical discovery assistant helping IT professionals gather information about client systems."},
                    {"role": "user", "content": formatted_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            if request_type == 'questions':
                questions = [line.strip() for line in response_text.split('\n') if line.strip() and '?' in line][:7]
                return questions
            else:
                return response_text
    except Exception as e:
        st.error(f"Error generating content: {e}")
        return "Error generating content. Please try again."

# Function to get combined context from all sources
def get_combined_context():
    background = st.session_state.get('background', '')
    notes = st.session_state.get('notes', '')
    global_context = st.session_state.get('global_context', '')
    dynamic_context = st.session_state.get('dynamic_context', '')
    
    # Extract QA pairs as context
    qa_context = ""
    for set_idx in range(0, len(st.session_state.generated_questions), 7):
        for idx in range(set_idx, min(set_idx + 7, len(st.session_state.generated_questions))):
            question = st.session_state.generated_questions[idx]
            answer = st.session_state.get(f"question_{idx}", "")
            if answer:
                qa_context += f"\n{question} - {answer}"
    
    combined_context = f"{background}\n\n{notes}\n\n{global_context}\n\n{dynamic_context}\n\n{qa_context}"
    return combined_context.strip()

# Function to rephrase QA pairs into statements using OpenAI
def rephrase_qa_pairs(questions, answers):
    if not openai.api_key:
        return ["Error: OpenAI API key not found"]
    
    statements = []
    
    for q, a in zip(questions, answers):
        if q and a:
            try:
                response = openai.chat.completions.create(
                    model=st.session_state.model,
                    messages=[
                        {"role": "system", "content": "You are an expert technical writer creating documentation from interview notes."},
                        {"role": "user", "content": f"Rephrase this Question and Answer into a coherent statement for technical documentation. Do not add any commentary. Question: {q} Answer: {a}"}
                    ],
                    temperature=0.3,
                    max_tokens=250
                )
                statement = response.choices[0].message.content.strip()
                statements.append(statement)
            except Exception as e:
                st.error(f"Error rephrasing QA pair: {e}")
                statements.append(f"{q} - {a}")
    
    return statements

# Function to update context with new QA pairs
def update_context(questions, answers, context_key):
    if not all(questions) or not all(answers):
        return
        
    statements = rephrase_qa_pairs(questions, answers)
    updated_context = "\n".join(statements)
    
    if updated_context:
        current_context = st.session_state.get(context_key, "")
        st.session_state[context_key] = (current_context + "\n" + updated_context).strip()
        return True
    return False

# UI Components
def render_sidebar():
    st.sidebar.title("Discovery Assistant")
    
    st.sidebar.header("Client Information")
    st.session_state.background = st.sidebar.text_area("Client Background", 
                                                     value=st.session_state.get('background', ''))
    
    st.sidebar.header("Meeting Notes")
    st.session_state.notes = st.sidebar.text_area("Add Notes", 
                                                value=st.session_state.get('notes', ''))
    
    # Context display in sidebar (collapsible)
    with st.sidebar.expander("Current Context"):
        combined_context = get_combined_context()
        if combined_context:
            st.text_area("All collected information", combined_context, height=300)
        else:
            st.info("No information collected yet.")

def render_main_content():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("Agent Assisted Discovery 🔍")
        st.markdown("*Real-time assistance for technical discovery calls*")
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "Technical Discovery", 
            "Generated Questions", 
            "Summary", 
            "Next Steps"
        ])
        
        # Tab 1: Technical Discovery (Static Questions)
        with tab1:
            st.header("Technical Static Questions")
            with st.form("static_questions_form"):
                static_answers = []
                for idx, question in enumerate(STATIC_QUESTIONS):
                    answer = st.text_area(question, key=f"static_{idx}", height=80)
                    static_answers.append(answer)
                
                submit_static = st.form_submit_button("Submit Technical Discovery Answers")
                
                if submit_static:
                    with st.spinner("Processing responses..."):
                        success = update_context(
                            STATIC_QUESTIONS, 
                            static_answers, 
                            'global_context'
                        )
                        if success:
                            st.success("Responses submitted and context updated!")
        
        # Tab 2: Generated Questions
        with tab2:
            st.header("AI Generated Questions")
            
            col_q1, col_q2 = st.columns([5, 1])
            with col_q1:
                st.markdown("Generate follow-up questions based on the current context.")
            with col_q2:
                if st.button(f"Generate Questions", key="gen_questions"):
                    with st.spinner("Generating new questions..."):
                        # Save answers from any existing generated questions first
                        for idx, q in enumerate(st.session_state.generated_questions):
                            answer = st.session_state.get(f"question_{idx}", "")
                            if q and answer:
                                update_context([q], [answer], 'dynamic_context')
                        
                        # Generate new questions
                        combined_context = get_combined_context()
                        new_questions = generate_content(combined_context, 'questions')
                        
                        # Add only unique questions
                        existing_questions = st.session_state.generated_questions
                        unique_new_questions = [q for q in new_questions if q not in existing_questions]
                        st.session_state.generated_questions.extend(unique_new_questions)
                        st.session_state.set_iteration += 1
                        
                        if unique_new_questions:
                            st.success(f"Generated {len(unique_new_questions)} new questions!")
                        else:
                            st.info("No new unique questions generated.")
            
            # Display generated questions in sets of 7
            if st.session_state.generated_questions:
                total_questions = len(st.session_state.generated_questions)
                for set_idx in range(0, total_questions, 7):
                    set_num = set_idx // 7 + 1
                    with st.expander(f"Question Set {set_num}", expanded=(set_num == total_questions // 7 + 1)):
                        with st.form(key=f"questions_form_{set_idx}"):
                            answers = []
                            for idx in range(set_idx, min(set_idx + 7, total_questions)):
                                question = st.session_state.generated_questions[idx]
                                answer = st.text_area(
                                    question, 
                                    key=f"question_{idx}", 
                                    height=80,
                                    value=st.session_state.get(f"question_{idx}", "")
                                )
                                answers.append(answer)
                            
                            submit_answers = st.form_submit_button("Submit Answers")
                            
                            if submit_answers:
                                with st.spinner("Processing answers..."):
                                    questions_in_set = st.session_state.generated_questions[set_idx:min(set_idx + 7, total_questions)]
                                    success = update_context(
                                        questions_in_set,
                                        answers,
                                        'dynamic_context'
                                    )
                                    if success:
                                        st.success("Answers submitted and context updated!")
            else:
                st.info("No questions generated yet. Click 'Generate Questions' to start.")
        
        # Tab 3: Summary
        with tab3:
            st.header("Technical Summary")
            if st.button("Generate Summary"):
                with st.spinner("Generating summary..."):
                    combined_context = get_combined_context()
                    st.session_state.summary = generate_content(combined_context, 'summary')
            
            if st.session_state.summary:
                st.markdown("### Generated Summary")
                st.write(st.session_state.summary)
                if st.button("Copy Summary", key="copy_summary"):
                    st.code(st.session_state.summary)
                    st.success("Summary copied to clipboard!")
            else:
                st.info("No summary generated yet. Click 'Generate Summary' to create one.")
        
        # Tab 4: Next Steps
        with tab4:
            st.header("Recommended Next Steps")
            if st.button("Generate Next Steps"):
                with st.spinner("Generating next steps..."):
                    combined_context = get_combined_context()
                    st.session_state.next_steps = generate_content(combined_context, 'next_steps')
            
            if st.session_state.next_steps:
                st.markdown("### Recommended Actions")
                st.write(st.session_state.next_steps)
                if st.button("Copy Next Steps", key="copy_next_steps"):
                    st.code(st.session_state.next_steps)
                    st.success("Next steps copied to clipboard!")
            else:
                st.info("No next steps generated yet. Click 'Generate Next Steps' to create recommendations.")
    
    with col2:
        # Quick reference guide
        st.markdown("### Quick Guide")
        st.markdown("""
        **Workflow:**
        1. Add client background and notes
        2. Complete technical questions
        3. Generate follow-up questions
        4. Get summary & next steps
        """)
        
        # Activity log
        st.markdown("### Activity Log")
        log_entries = []
        if st.session_state.get('global_context', ''):
            log_entries.append("✅ Static questions answered")
        
        if st.session_state.generated_questions:
            log_entries.append(f"✅ Generated {len(st.session_state.generated_questions)} questions")
        
        if st.session_state.get('dynamic_context', ''):
            log_entries.append("✅ Processed dynamic Q&A")
        
        if st.session_state.get('summary', ''):
            log_entries.append("✅ Summary generated")
        
        if st.session_state.get('next_steps', ''):
            log_entries.append("✅ Next steps defined")
        
        if log_entries:
            for entry in log_entries:
                st.markdown(entry)
        else:
            st.info("No activities recorded yet")
        
        # Model selector
        st.markdown("### OpenAI Model")
        model = st.selectbox(
            "Select model",
            options=["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0
        )
        st.session_state.model = model

# Main App Logic
def main():
    render_sidebar()
    render_main_content()

if __name__ == "__main__":
    main()