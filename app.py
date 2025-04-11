import streamlit as st
import pandas as pd
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import matplotlib.pyplot as plt

# Path to the logo image
logo_path = "Logo.png"

###############################################################################
# 1. Define categories, questions, and rating scale
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
# 2. Helper functions for allyship scale, PDF generation, and scoring
###############################################################################

def get_allyship_scale_text(total_score):
    """
    Returns paragraphs describing the user's position on the allyship scale
    based on the overall total_score.
    """
    # Example cutoffs: <30, 30–90, 90–110, 110–120
    if total_score < 30:
        return [
            ("Below 30: Just Starting", "bold"),
            ("It looks like you’re just getting started on this journey.", "normal"),
            ("(Optionally add any supportive text here...)", "normal"),
        ]
    elif total_score <= 90:
        return [
            ("30–90: Consciously Relearning", "bold"),
            ("You are on an important journey of self-education!", "normal"),
            ("Unlearning, relearning and changing behaviour takes time – be patient and stay committed.", "normal"),
            ("Listening and centring the experience of others will be key to elevating your allyship development.", "normal"),
        ]
    elif total_score <= 110:
        return [
            ("90–110: Adapting & Centering Others", "bold"),
            ("You are on an important journey of self-education!", "normal"),
            ("Unlearning, relearning and changing behaviour takes time – be patient and stay committed.", "normal"),
            ("Listening and centring the experience of others will be key to elevating your allyship development.", "normal"),
        ]
    else:
        # 110–120 or above
        return [
            ("110–120: Challenging & Sponsoring", "bold"),
            ("As a consciously inclusive leader, you seek out and amplify under-represented perspectives during decision-making.", "normal"),
            ("You call out unfair practices when you notice them.", "normal"),
            ("Incentivising others and driving systemic change beyond your immediate function or business will be key to elevating your allyship further.", "normal"),
        ]

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
    Returns a list of chart images (in-memory) so we can embed them in the PDF.
    """
    st.markdown("<h3>Self Assessment Scores by Category and Type</h3>", unsafe_allow_html=True)
    chart_images = []
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
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        chart_images.append(buf)
        st.image(buf)
    return chart_images

def wrap_text(text, canvas, max_width, font_size):
    """
    Safely splits a text string into multiple lines so it fits in 'max_width' on the PDF
    (works even if one word is bigger than max_width).
    """
    lines = []
    words = text.split()

    while words:
        line = ''
        # Build as many words as fit into this line
        while words and canvas.stringWidth(line + words[0] + ' ', "Helvetica", font_size) <= max_width:
            line += words.pop(0) + ' '

        if not line.strip():
            # Means the next word is too long to fit in max_width.
            # Instead of looping forever, just force that word to occupy
            # its own line (even if it exceeds max_width).
            # Pop it out, treat it as a line, and move on.
            # If you wanted to truly split it in the middle, you’d have to do additional logic.
            long_word = words.pop(0)
            lines.append(long_word)
        else:
            lines.append(line.strip())

    return lines

def generate_pdf(total_scores_per_category, max_scores_per_category, chart_images, total_score):
    """
    Builds a multi-page PDF with:
      - Scores per category
      - Allyship scale text based on overall total_score
      - Custom bar charts
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 40
    y = height - margin

    # Try adding a logo at the top
    try:
        logo = ImageReader(logo_path)
        logo_width, logo_height = logo.getSize()
        aspect_ratio = logo_height / logo_width
        logo_display_width = 60
        logo_display_height = logo_display_width * aspect_ratio
        c.drawImage(logo, margin, y - logo_display_height, 
                    width=logo_display_width, height=logo_display_height)
        y -= (logo_display_height + 20)
    except Exception as e:
        st.error("Logo image not found or could not be loaded.")
        st.write(e)

    # PDF Title
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "LEAD Network Anti-Bias Self Assessment Tool")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, "Your results:")
    y -= 15

    # Display category scores
    for category_name, score in total_scores_per_category.items():
        max_score = max_scores_per_category[category_name]
        progress = int((score / max_score) * 100) if max_score > 0 else 0
        line = f"{category_name}: {score} out of {max_score} ({progress}%)"
        if y - 15 < margin:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, line)
        y -= 15

    y -= 10

    # Insert Allyship Scale section
    allyship_scale_text = get_allyship_scale_text(total_score)
    for (paragraph, style) in allyship_scale_text:
        if style == "bold":
            c.setFont("Helvetica-Bold", 10)
        else:
            c.setFont("Helvetica", 10)
        lines = wrap_text(paragraph, c, width - 2*margin, 10)
        for line in lines:
            if y - 15 < margin:
                c.showPage()
                y = height - margin
            c.drawString(margin, y, line)
            y -= 12
        y -= 5  # extra spacing

    # Go to a new page for the charts
    c.showPage()

    charts_per_page = 2  
    chart_index = 0
    for page in range(3):
        y = height - 50
        for _ in range(charts_per_page):
            if chart_index >= len(chart_images):
                break
            img = chart_images[chart_index]
            if y - 320 < margin:
                c.showPage()
                y = height - 50
            c.drawImage(ImageReader(img), margin, y - 300, 
                        width=width - 2 * margin, height=300)
            y -= 320
            chart_index += 1
        if chart_index >= len(chart_images):
            break
        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer

###############################################################################
# 3. Main Streamlit UI
###############################################################################

def main():
    if 'unique_visits' not in st.session_state:
        st.session_state.unique_visits = 0
    st.session_state.unique_visits += 1
    
    # Attempt to show the logo in the Streamlit UI
    try:
        st.image(logo_path, width=200)
    except Exception as e:
        st.error("Logo image not found. Please check the path to the logo image.")
        st.write(e)
        
    st.title("Anti-Bias Self Assessment Tool")
    st.write(
        "This tool enables you to explore your own behaviours related to bias & inclusion in the workplace. "
        "Your results are yours and yours alone -- they will not be submitted or shared in any manner unless you choose to do so."
    )
    st.write(
        "Read each statement and choose a score using the rating scale provided. "
        "Once complete, the tool subtotals the scores by section. Reflect on areas where your scores are lower than others and "
        "identify where you can continue to grow. The assessment should take you no longer than 5 – 10 mins."
    )
    st.write("### Rating Scale: 1 = Never | 2 = Rarely | 3 = Sometimes | 4 = Often")

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

        # Create bar chart images
        chart_images = custom_bar_chart(scores_data)

        # Generate PDF
        pdf_buffer = generate_pdf(
            total_scores_per_category, 
            max_scores_per_category, 
            chart_images,
            total_score
        )

        st.download_button(
            label="Download PDF of Results",
            data=pdf_buffer,
            file_name="assessment_results.pdf",
            mime="application/pdf"
        )

    # Footer
    st.markdown(
        f"""
        <div style='text-align: center; margin-top: 50px; font-size: 12px;'>
            Created by Regina Chitralla
        </div>
        <div style='text-align: center; font-size: 12px;'>
            Unique Page Visits: {st.session_state.unique_visits}
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
