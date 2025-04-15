import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

###############################################################################
# 1. Page and Image Paths
###############################################################################
st.set_page_config(
    page_title="Actionable Allyship Self-Assessment",
    layout="wide"  # Helps with wide layout, if desired
)

# Path to your existing PDF
EXISTING_PDF_PATH = "Actionable-Allyship-Self-Assessment.pdf"

# Path to the logo image
logo_path = "All-In-Full-Logo-Black-Colour.png"

###############################################################################
# 2. Define Categories, Questions, and Split into Two Sets
###############################################################################
# We assume you have only one main category, with 10 sub-sections total.
main_category_name = "Equity & Inclusion Self-Assessment"

all_sections = {
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

# Which sections go on page 1 vs. page 2
page_1_sections = [
    "Build your knowledge",
    "Explore & grow",
    "Practise self-compassion",
    "Centre the experiences of others",
    "Create safe spaces for dialogue"
]
page_2_sections = [
    "Amplify voices",
    "Speak out",
    "Make equitable & inclusive decisions",
    "Drive accountability",
    "Create sustainable change"
]

###############################################################################
# 3. Helper Functions
###############################################################################
def display_sections(section_list):
    """
    Displays the given sections (list of section names) as headings + selectboxes.
    Returns all user responses for these sections as a list of dicts.
    """
    responses = []
    for section_name in section_list:
        st.markdown(f"### {section_name}")
        questions = all_sections[section_name]
        for question_text in questions:
            unique_key = f"{main_category_name}_{section_name}_{question_text}"
            if unique_key not in st.session_state:
                # Default to 1
                st.session_state[unique_key] = 1

            score = st.selectbox(
                label=question_text,
                options=[1, 2, 3, 4],
                index=[1, 2, 3, 4].index(st.session_state[unique_key]),
                key=unique_key
            )
            responses.append({
                "category": main_category_name,
                "type": section_name,
                "question": question_text,
                "score": score
            })
    return responses

def count_answered_questions():
    """
    Counts how many questions in the entire assessment have a stored score in session_state.
    """
    count = 0
    for section_name, questions in all_sections.items():
        for question_text in questions:
            key = f"{main_category_name}_{section_name}_{question_text}"
            # If it's in session_state with a numeric value, consider it answered
            if key in st.session_state and st.session_state[key] is not None:
                count += 1
    return count

def total_number_of_questions():
    return sum(len(questions) for questions in all_sections.values())

def show_progress_bar():
    """
    Shows how many questions answered so far out of total, as a horizontal progress bar.
    """
    answered = count_answered_questions()
    total_q = total_number_of_questions()
    pct = int(answered / total_q * 100)

    # Custom progress bar using HTML
    st.markdown(
        f"""
        <div style="width: 100%; background-color: #e0e0e0; border-radius: 5px; margin-top: 15px;">
            <div style="width: {pct}%; background-color: #377bff; padding: 5px; color: white; text-align: center; border-radius: 5px;">
                {answered} of {total_q} questions answered ({pct}%)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def calculate_total_score(responses):
    return sum(r['score'] for r in responses if r['score'] is not None)

def calculate_total_scores_per_category(responses):
    total_scores_per_category = {}
    for r in responses:
        cat = r["category"]
        if cat not in total_scores_per_category:
            total_scores_per_category[cat] = 0
        total_scores_per_category[cat] += r["score"]
    return total_scores_per_category

def calculate_max_scores_per_category():
    """
    Calculates the max possible score (4 per question) for the single category we have.
    """
    all_q = total_number_of_questions()
    # 4 points per question
    return {main_category_name: all_q * 4}

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
        cat_data = scores_data[scores_data["Category"] == category].sort_values(by=["Type"], ascending=False)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.barh(cat_data["Type"], cat_data["Percentage"], color='#377bff')
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
    # Track the current "page" in session_state
    if "page" not in st.session_state:
        st.session_state["page"] = 1

    # Also track how many times the page was visited
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

    if st.session_state["page"] == 1:
        # -----------------------
        # PAGE 1 Layout
        # -----------------------
        st.markdown(f"## Page 1: {main_category_name}")
        # Display the first half of the sections
        page1_responses = display_sections(page_1_sections)

        # Show the "Next" button at the bottom of page 1
        if st.button("Next →"):
            st.session_state["page"] = 2

        # Show a progress bar of how many total questions are answered
        show_progress_bar()

    elif st.session_state["page"] == 2:
        # -----------------------
        # PAGE 2 Layout
        # -----------------------
        st.markdown(f"## Page 2: {main_category_name}")
        # Display the second half of the sections
        page2_responses = display_sections(page_2_sections)

        # "Back" button if you want the user to go back and edit Page 1
        # This is optional. Uncomment if you want a back button:
        # if st.button("← Back"):
        #     st.session_state["page"] = 1
        #     st.experimental_rerun()

        # Or "Submit" to finalize
        if st.button("Submit"):
            # Combine all responses for scoring
            # We don't do anything with page1_responses vs page2_responses in session 
            # because the user might have changed page1_responses after we created them.
            # So let's just re-scan them directly in session_state.
            all_responses = []
            for section, questions in all_sections.items():
                for q in questions:
                    key = f"{main_category_name}_{section}_{q}"
                    all_responses.append({
                        "category": main_category_name,
                        "type": section,
                        "question": q,
                        "score": st.session_state[key]
                    })

            st.write("## Assessment Complete. Here are your results:")

            # Calculate total + per-category
            total_scores_per_cat = calculate_total_scores_per_category(all_responses)
            max_scores_per_cat = calculate_max_scores_per_category()
            # Show progress bars for each category
            for cat_name, cat_score in total_scores_per_cat.items():
                cat_max = max_scores_per_cat[cat_name]
                st.write(f"**{cat_name}: {cat_score} out of {cat_max}**")
                pct = int(cat_score / cat_max * 100)
                custom_progress_bar(pct)

            # Build data for bar charts by sub-sections
            flattened_scores = []
            for section, questions in all_sections.items():
                sub_scores = sum(
                    r["score"] for r in all_responses 
                    if r["type"] == section
                )
                sub_max = len(questions) * 4
                sub_pct = (sub_scores / sub_max) * 100
                flattened_scores.append({
                    "Category": main_category_name,
                    "Type": section,
                    "Score": sub_scores,
                    "Percentage": sub_pct
                })

            scores_df = pd.DataFrame(flattened_scores)
            custom_bar_chart(scores_df)

            # Provide the existing PDF for download
            try:
                with open(EXISTING_PDF_PATH, "rb") as pdf_file:
                    PDF_CONTENT = pdf_file.read()
                st.download_button(
                    label="Understand your results",
                    data=PDF_CONTENT,
                    file_name="allyship_guide.pdf",
                    mime="application/pdf"
                )
            except FileNotFoundError:
                st.error("PDF file not found. Check your path or filename.")

        # Show a progress bar of how many total questions are answered
        show_progress_bar()

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
