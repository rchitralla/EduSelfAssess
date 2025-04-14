import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
from io import BytesIO

###############################################################################
# 1. Page and Image Paths
###############################################################################
st.set_page_config(
    page_title="Actionable Allyship Self-Assessment",
    layout="wide"  # Ensures layout is wide
)

# Path to your existing PDF
EXISTING_PDF_PATH = "Actionable-Allyship-Self-Assessment.pdf"

# Path to the logo image
logo_path = "All-In-Full-Logo-Black-Colour.png"

###############################################################################
# 2. Define Categories, Questions, and Rating Scale
###############################################################################
categories = {
    "Equity & Inclusion Self-Assessment": {
        "Build your knowledge": [
            "I learn about people who are different to me.",
            "I invest time in learning about equity & inclusion.",
            "I leverage insights from Employee Resource Groups (or equivalent) to impact business outcomes."
        ],
        "Amplify voices": [
            "When developing ideas or making decisions, I ask 'Whose perspective are we missing?'",
            "I advocate for individuals from marginalised groups when they’re not in the room.",
            "I give credit to individuals whose voices are often overlooked or unheard."
        ],
        "Explore & grow": [
            "I am aware of and challenge my own biases and assumptions.",
            "I seek feedback about the impact of my actions & behaviours on others.",
            "I take feedback seriously and course correct."
        ],
        "Speak out": [
            "I say something when I hear people make comments that are rooted in stereotype or assumption.",
            "If I notice someone is being talked over or dismissed, I draw attention to it.",
            "I challenge inequities and unfair practices when I witness them."
        ],
        "Practise self-compassion": [
            "I accept that I will make mistakes.",
            "I see my mistakes as opportunities to listen, learn, and improve, without dwelling on them.",
            "If I unintentionally make a mistake, I apologise, correct myself and move on."
        ],
        "Make equitable & inclusive decisions": [
            "I ensure diverse perspectives are included when developing products and services.",
            "I prioritise equity when making hiring, promotion and other critical people decisions.",
            "I evaluate and measure the outcomes of my decisions across different populations."
        ],
        "Centre the experiences of others": [
            "I actively listen to the experiences of others without being judgmental or defensive.",
            "I believe others’ experiences and challenge my own assumptions.",
            "In discussions, I intentionally hold back from sharing my view, until others have shared their own perspectives."
        ],
        "Drive accountability": [
            "I establish equity & inclusion goals that tie to business performance.",
            "I hold all team members accountable for creating an inclusive environment.",
            "I reward equitable & inclusive behaviours."
        ],
        "Create safe spaces for dialogue": [
            "At the beginning of group discussions, I remind participants to give each other their full attention.",
            "I share my experiences with equity and inclusion to build trust and connection with others.",
            "I invite people to raise concerns, even if it feels uncomfortable."
        ],
        "Create sustainable change": [
            "I use a data-driven approach to develop and evaluate policies.",
            "I elevate equity & inclusion when developing and executing strategic plans.",
            "I make equity & inclusion a priority when collaborating with others from different parts of the value chain."
        ]
    }
}

# Flattened list of questions
questions_list = []
for category_name, types in categories.items():
    for type_name, questions in types.items():
        for question in questions:
            questions_list.append({
                "category": category_name,
                "type": type_name,
                "question": question
            })

###############################################################################
# 3. Helper Functions for Scoring, Display, and Charting
###############################################################################
def display_questions():
    """
    Display each question as a selectbox with the rating scale (1..4).
    Return a list of dictionaries capturing the user's score.
    """
    responses = []
    options = [1, 2, 3, 4]
    for item in st.session_state['shuffled_questions']:
        st.write(item["question"])
        key = f"{item['category']}_{item['type']}_{item['question']}"
        if key not in st.session_state:
            st.session_state[key] = 1

        selected_option = st.selectbox(
            "Select your response:",
            options,
            index=options.index(st.session_state[key]) if st.session_state[key] in options else 0,
            key=key
        )

        responses.append({
            "category": item["category"],
            "type": item["type"],
            "question": item["question"],
            "score": selected_option
        })
    return responses

def calculate_total_score(responses):
    return sum(response['score'] for response in responses if response['score'] is not None)

def calculate_total_scores_per_category(responses):
    total_scores_per_category = {}
    for response in responses:
        if response["score"] is None:
            continue
        category = response["category"]
        score = response["score"]
        if category not in total_scores_per_category:
            total_scores_per_category[category] = 0
        total_scores_per_category[category] += score
    return total_scores_per_category

def calculate_max_scores_per_category(categories):
    """
    Calculates the max possible score (4 per question) for each category.
    """
    max_scores_per_category = {}
    for category_name, types in categories.items():
        total_questions = sum(len(questions) for questions in types.values())
        max_scores_per_category[category_name] = total_questions * 4  # 4 is the max rating
    return max_scores_per_category

def custom_progress_bar(percentage, color="#377bff"):
    """
    Creates a horizontal progress bar with the given percentage and color in Streamlit.
    """
    st.markdown(
        f"""
        <div style="width: 100%; background-color: #e0e0e0; border-radius: 5px;">
            <div style="width: {percentage}%; background-color: {color}; padding: 5px; color: white; text-align: center; border-radius: 5px;">
                {percentage}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def custom_bar_chart(scores_data):
    """
    Displays a bar chart per category, showing the percentage for each sub-type.
    """
    st.markdown("<h3>Self Assessment Scores by Category and Type</h3>", unsafe_allow_html=True)
    for category in scores_data["Category"].unique():
        st.markdown(f"### {category}", unsafe_allow_html=True)
        category_data = scores_data[scores_data["Category"] == category]
        category_data = category_data.sort_values(by=["Type"], ascending=[False])

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.barh(category_data["Type"], category_data["Percentage"], color='#377bff')
        ax.set_xlim(0, 100)
        ax.set_xlabel('Percentage', fontsize=12)
        ax.set_title(category, fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=10)
        plt.tight_layout()

        st.pyplot(fig)

###############################################################################
# 4. Main Streamlit UI
###############################################################################
def main():
    if 'unique_visits' not in st.session_state:
        st.session_state.unique_visits = 0
    st.session_state.unique_visits += 1
    
    # Show the logo at a fixed width
    try:
        st.image(logo_path, width=200)
    except Exception as e:
        st.error("Logo image not found. Please check the path to the logo image.")
        st.write(e)
        
    st.title("Actionable Allyship Self-Assessment")
    st.write(
        """This confidential assessment aligns with the All In Action Framework. It is designed 
        to reveal your current allyship strengths and opportunities for growth."""
    )
    st.write("### Rating Scale: 1 = Never | 2 = Rarely | 3 = Sometimes | 4 = Often")

    # Shuffle questions if not already done
    if 'shuffled_questions' not in st.session_state:
        st.session_state['shuffled_questions'] = questions_list.copy()
        random.shuffle(st.session_state['shuffled_questions'])

    # Display the questions
    responses = display_questions()

    # Calculate total + per-category scores
    total_score = calculate_total_score(responses)
    total_scores_per_category = calculate_total_scores_per_category(responses)
    max_scores_per_category = calculate_max_scores_per_category(categories)

    if st.button("Submit"):
        st.write("## Assessment Complete. Here are your results:")

        # Show per-category progress
        for category_name, score in total_scores_per_category.items():
            max_score = max_scores_per_category[category_name]
            st.write(f"**{category_name}: {score} out of {max_score}**")
            progress = int((score / max_score) * 100)
            custom_progress_bar(progress)

        # Build data for bar charts
        flattened_scores = []
        for category_name, types in categories.items():
            for type_name, questions in types.items():
                response_scores = [
                    r['score'] for r in responses
                    if r['category'] == category_name and r['type'] == type_name
                ]
                score = sum(response_scores)
                max_score_type = len(questions) * 4
                percentage = (score / max_score_type) * 100
                flattened_scores.append({
                    "Category": category_name,
                    "Type": type_name,
                    "Score": score,
                    "Percentage": percentage
                })

        scores_data = pd.DataFrame(flattened_scores)
        # Sort to keep categories in the order they appear
        ordered_categories = scores_data["Category"].unique()
        scores_data["Category"] = pd.Categorical(
            scores_data["Category"],
            categories=ordered_categories,
            ordered=True
        )
        scores_data = scores_data.sort_values(by=["Category", "Type"], ascending=[True, False])

        # Create bar charts
        custom_bar_chart(scores_data)

        # -------------------------------------------
        # Provide the existing PDF for download
        # -------------------------------------------
        with open(EXISTING_PDF_PATH, "rb") as pdf_file:
            PDF_CONTENT = pdf_file.read()

        st.download_button(
            label="Understand your results",
            data=PDF_CONTENT,
            file_name="allyship_guide.pdf",
            mime="application/pdf"
        )

    # Footer
    st.markdown(
        f"""
        <div style='text-align: center; margin-top: 50px; font-size: 12px;'>
            Created by Regina
        </div>
        <div style='text-align: center; font-size: 12px;'>
            Unique Page Visits: {st.session_state.unique_visits}
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
