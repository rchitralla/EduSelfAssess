import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

###############################################################################
# 1. Page and Image Paths
###############################################################################
st.set_page_config(
    page_title="Actionable Allyship Self-Assessment",
    layout="wide"  # Ensures layout is wide (helpful for columns).
)

# Path to your existing PDF
EXISTING_PDF_PATH = "Actionable-Allyship-Self-Assessment.pdf"

# Path to the logo image
logo_path = "All-In-Full-Logo-Black-Colour.png"

###############################################################################
# 2. Define Categories, Questions, and Separate Lists for Left/Right Sections
###############################################################################
categories = {
    "Equity & Inclusion Self-Assessment": {
        "Build your knowledge": [
            "I learn about people who are different to me.",
            "I invest time in learning about equity & inclusion.",
            "I leverage insights from Employee Resource Groups (or equivalent) to impact business outcomes."
        ],
        "Explore & grow": [
            "I am aware of and challenge my own biases and assumptions.",
            "I seek feedback about the impact of my actions & behaviours on others.",
            "I take feedback seriously and course correct."
        ],
        "Practise self-compassion": [
            "I accept that I will make mistakes.",
            "I see my mistakes as opportunities to listen, learn, and improve, without dwelling on them.",
            "If I unintentionally make a mistake, I apologise, correct myself and move on."
        ],
        "Centre the experiences of others": [
            "I actively listen to the experiences of others without being judgmental or defensive.",
            "I believe others’ experiences and challenge my own assumptions.",
            "In discussions, I intentionally hold back from sharing my view, until others have shared their own perspectives."
        ],
        "Create safe spaces for dialogue": [
            "At the beginning of group discussions, I remind participants to give each other their full attention.",
            "I share my experiences with equity and inclusion to build trust and connection with others.",
            "I invite people to raise concerns, even if it feels uncomfortable."
        ],
        "Amplify voices": [
            "When developing ideas or making decisions, I ask 'Whose perspective are we missing?'",
            "I advocate for individuals from marginalised groups when they’re not in the room.",
            "I give credit to individuals whose voices are often overlooked or unheard."
        ],
        "Speak out": [
            "I say something when I hear people make comments that are rooted in stereotype or assumption.",
            "If I notice someone is being talked over or dismissed, I draw attention to it.",
            "I challenge inequities and unfair practices when I witness them."
        ],
        "Make equitable & inclusive decisions": [
            "I ensure diverse perspectives are included when developing products and services.",
            "I prioritise equity when making hiring, promotion and other critical people decisions.",
            "I evaluate and measure the outcomes of my decisions across different populations."
        ],
        "Drive accountability": [
            "I establish equity & inclusion goals that tie to business performance.",
            "I hold all team members accountable for creating an inclusive environment.",
            "I reward equitable & inclusive behaviours."
        ],
        "Create sustainable change": [
            "I use a data-driven approach to develop and evaluate policies.",
            "I elevate equity & inclusion when developing and executing strategic plans.",
            "I make equity & inclusion a priority when collaborating with others from different parts of the value chain."
        ]
    }
}

# We just have one top-level category, but let's note it for clarity:
main_category_name = "Equity & Inclusion Self-Assessment"

# Define which sub-sections go in the LEFT vs. RIGHT columns
left_sections = [
    "Build your knowledge",
    "Explore & grow",
    "Practise self-compassion",
    "Centre the experiences of others",
    "Create safe spaces for dialogue"
]

right_sections = [
    "Amplify voices",
    "Speak out",
    "Make equitable & inclusive decisions",
    "Drive accountability",
    "Create sustainable change"
]

###############################################################################
# 3. Helper Functions
###############################################################################
def display_subsections_in_column(col, category_dict, category_name, subsection_list):
    """
    Displays each subsection (and its questions) in the given column 'col'.
    Returns a list of response dicts (category, type, question, score).
    """
    responses = []
    with col:
        # Show the category name once at the top if you want. 
        # If you prefer a smaller heading, use st.markdown("### ...")
        for subsection_title in subsection_list:
            st.markdown(f"### {subsection_title}")
            questions = category_dict[category_name][subsection_title]
            for question in questions:
                unique_key = f"{category_name}_{subsection_title}_{question}"
                if unique_key not in st.session_state:
                    st.session_state[unique_key] = 1

                score = st.selectbox(
                    label=question,
                    options=[1, 2, 3, 4],
                    index=[1, 2, 3, 4].index(st.session_state[unique_key]),
                    key=unique_key
                )
                responses.append({
                    "category": category_name,
                    "type": subsection_title,
                    "question": question,
                    "score": score
                })
    return responses


def calculate_total_score(responses):
    return sum(r['score'] for r in responses if r['score'] is not None)

def calculate_total_scores_per_category(responses):
    total_scores_per_category = {}
    for r in responses:
        if r["score"] is None:
            continue
        cat = r["category"]
        if cat not in total_scores_per_category:
            total_scores_per_category[cat] = 0
        total_scores_per_category[cat] += r["score"]
    return total_scores_per_category

def calculate_max_scores_per_category(categories_dict):
    """
    Calculates the max possible score (4 per question) for each category.
    """
    max_scores_per_category = {}
    for cat_name, sub_sections in categories_dict.items():
        total_questions = sum(len(qlist) for qlist in sub_sections.values())
        max_scores_per_category[cat_name] = total_questions * 4
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
    unique_categories = scores_data["Category"].unique()
    for category in unique_categories:
        st.markdown(f"### {category}", unsafe_allow_html=True)
        category_data = scores_data[scores_data["Category"] == category]
        category_data = category_data.sort_values(by=["Type"], ascending=False)

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
    # Track unique page visits
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

    # Create two columns for the sub-sections
    col_left, col_right = st.columns(2)
    
    # Display left sections in the first column
    left_responses = display_subsections_in_column(
        col=col_left,
        category_dict=categories,
        category_name=main_category_name,
        subsection_list=left_sections
    )
    
    # Display right sections in the second column
    right_responses = display_subsections_in_column(
        col=col_right,
        category_dict=categories,
        category_name=main_category_name,
        subsection_list=right_sections
    )

    # Combine all responses
    all_responses = left_responses + right_responses

    if st.button("Submit"):
        st.write("## Assessment Complete. Here are your results:")

        # Calculate total + per-category scores
        total_score = calculate_total_score(all_responses)
        total_scores_per_category = calculate_total_scores_per_category(all_responses)
        max_scores_per_category = calculate_max_scores_per_category(categories)

        # Show progress bars for each category
        for cat_name, score_value in total_scores_per_category.items():
            max_score = max_scores_per_category[cat_name]
            st.write(f"**{cat_name}: {score_value} out of {max_score}**")
            progress_pct = int((score_value / max_score) * 100)
            custom_progress_bar(progress_pct)

        # Prepare data for bar chart
        flattened_scores = []
        for cat_name, sub_sections in categories.items():
            for subsection_title, qlist in sub_sections.items():
                # sum up the user scores in that sub-section
                matched_scores = [
                    r['score'] 
                    for r in all_responses 
                    if r['category'] == cat_name and r['type'] == subsection_title
                ]
                sub_total_score = sum(matched_scores)
                sub_max_score = len(qlist) * 4
                sub_percentage = (sub_total_score / sub_max_score) * 100
                flattened_scores.append({
                    "Category": cat_name,
                    "Type": subsection_title,
                    "Score": sub_total_score,
                    "Percentage": sub_percentage
                })

        scores_data = pd.DataFrame(flattened_scores)
        # Keep the order of categories as in the dictionary
        ordered_categories = list(scores_data["Category"].unique())
        scores_data["Category"] = pd.Categorical(
            scores_data["Category"], 
            categories=ordered_categories, 
            ordered=True
        )
        # Sort to keep sub-sections in a readable order (optional).
        scores_data = scores_data.sort_values(by=["Category", "Type"], ascending=[True, True])

        # Show the bar charts
        custom_bar_chart(scores_data)

        # Provide the existing PDF for download
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
