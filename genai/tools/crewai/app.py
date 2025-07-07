import streamlit as st
from crew_logic import run_genetic_crew

st.set_page_config(layout="centered")
st.title("🧬 Genetic Research with CrewAI")

# Input for genetic research topic
topic = st.text_input("Enter a genetic research topic:", "CRISPR gene editing")

# Button to run the crew
if st.button("Start Genetic Research"):
    if topic:
        st.info(f"Starting research on: {topic}...")
        with st.spinner("Crew is working hard..."):
            try:
                result = run_genetic_crew(topic)
                st.success("Research Complete!")
                st.subheader("Research Summary:")
                st.markdown(result) # Use markdown to render potential bullet points/paragraphs
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic to start the research.") 