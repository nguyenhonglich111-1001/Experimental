import streamlit as st
from crew_logic import run_research_crew

st.set_page_config(layout="centered")
st.title("🔬 General Research with CrewAI")

# Initialize session state for controlling research start
if 'start_research' not in st.session_state:
    st.session_state.start_research = False

def set_start_research():
    st.session_state.start_research = True

# Input for research topic
topic = st.text_input("Enter a research topic:", "AI in healthcare", on_change=set_start_research, key="research_topic_input")

# Run the crew only if topic is entered and 'Enter' is pressed
if st.session_state.start_research and topic:
    st.info(f"Starting research on: {topic}...")
    with st.spinner("Crew is working hard..."):
        try:
            result = run_research_crew(topic)
            st.success("Research Complete!")
            st.subheader("Research Summary:")
            st.markdown(result) # Use markdown to render potential bullet points/paragraphs
        except Exception as e:
            st.error(f"An error occurred: {e}")
    # Reset the flag after running to prevent re-running on subsequent unrelated interactions
    st.session_state.start_research = False
elif not topic:
    st.warning("Please enter a topic to start the research.") 