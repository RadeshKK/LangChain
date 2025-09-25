import streamlit as st
from main import response_by_model

# Page Header
st.set_page_config(page_title="Social Media Content Generator", layout="wide")  # Set layout to wide for better spacing
st.header("🔗 Powerful Content Generator for Various Social Media Platforms 🔗")

# Sidebar for API Key Input
api_key = st.sidebar.text_input("Google Gemini API Key", type="password")

# Function to generate responses
def generate_response(input_text, api_key):
    results = response_by_model(text=input_text, api_key=api_key)  # Should return a dictionary with 'facebook' and 'linkedin'
    
    facebook_content = results.get("fb_tips", "No Facebook content generated.")
    linkedin_content = results.get("linkedin_tips", "No LinkedIn content generated.")

    # Creating two columns for Facebook and LinkedIn
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📘 Facebook Content")
        st.markdown(
            f"""
            <div style="border: 2px solid #1877F2; padding: 10px; border-radius: 10px; background-color: #F0F2F5;">
                <p style="color: black;">{facebook_content}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.subheader("🔗 LinkedIn Content")
        st.markdown(
            f"""
            <div style="border: 2px solid #0A66C2; padding: 10px; border-radius: 10px; background-color: #E8F4FD;">
                <p style="color: black;">{linkedin_content}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Input Form
with st.form("content_form"):
    text = st.text_area("Enter the topic on which you want to generate content:")
    submitted = st.form_submit_button("Generate Content")

    if not api_key:
        st.warning("Please enter your Gemini API key!", icon="⚠")
    elif submitted:
        generate_response(text,api_key)
