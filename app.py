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

# Define the categories, types, and questions
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


# Flattened list of questions to display without headers
questions_list = []
for category_name, types in categories.items():
    for type_name, questions in types.items():
        for question in questions:
            questions_list.append({
                "category": category_name,
                "type": type_name,
                "question": question
            })

# Function to display questions and collect responses
def display_questions():
    responses = []
    for item in st.session_state['shuffled_questions']:
        st.write(item["question"])
        options = [1, 2, 3, 4, 5]
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

# Function to calculate the total score
def calculate_total_score(responses):
    total_score = sum(response['score'] for response in responses if response['score'] is not None)
    return total_score

# Function to calculate the total score per category
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

# Function to calculate the maximum possible score per category
def calculate_max_scores_per_category(categories):
    max_scores_per_category = {}
    for category_name, types in categories.items():
        total_questions = sum(len(questions) for questions in types.values())
        max_scores_per_category[category_name] = total_questions * 4  # Maximum score is 4 per question
    return max_scores_per_category

# Function to create custom progress bar
def custom_progress_bar(percentage, color="#377bff"):
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

# Function to create custom bar chart
def custom_bar_chart(scores_data):
    st.markdown("<h3>Self Assessment Scores by Category and Type</h3>", unsafe_allow_html=True)
    chart_images = []
    for category in scores_data["Category"].unique():
        st.markdown(f"### {category}", unsafe_allow_html=True)
        category_data = scores_data[scores_data["Category"] == category]
        category_data = category_data.sort_values(by=["Type"], ascending=[False])  # Ensure consistent order

        fig, ax = plt.subplots(figsize=(10, 4))  # Increase the height for better readability
        ax.barh(category_data["Type"], category_data["Percentage"], color='#377bff')
        ax.set_xlim(0, 100)
        ax.set_xlabel('Percentage', fontsize=12)
        ax.set_title(category, fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=10)
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300)  # Increase DPI for better resolution
        buf.seek(0)
        chart_images.append(buf)
        st.image(buf)
    return chart_images

# Function to wrap text for the PDF
def wrap_text(text, canvas, max_width, font_size):
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and canvas.stringWidth(line + words[0] + ' ', "Helvetica", font_size) <= max_width:
            line += words.pop(0) + ' '
        lines.append(line.strip())
    return lines

# Function to generate PDF
def generate_pdf(total_scores_per_category, max_scores_per_category, chart_images):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 40
    y = height - margin

    # Add the logo
    try:
        logo = ImageReader(logo_path)
        logo_width, logo_height = logo.getSize()
        aspect_ratio = logo_height / logo_width
        logo_display_width = 60
        logo_display_height = logo_display_width * aspect_ratio
        c.drawImage(logo, margin, y - logo_display_height, width=logo_display_width, height=logo_display_height)
        y -= (logo_display_height + 20)
    except Exception as e:
        st.error("Logo image not found or could not be loaded.")
        st.write(e)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "All In- Journeys- Self-Assessment")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, "Your results:")
    y -= 15

    for category_name, score in total_scores_per_category.items():
        max_score = max_scores_per_category[category_name]
        progress = int((score / max_score) * 100)
        line = f"{category_name}: {score} out of {max_score} ({progress}%)"
        if y - 15 < margin:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, line)
        y -= 15

    y -= 10  # Extra space before explanations

    # Add explanations with bold headers
    explanations = [
        ("How to interpret the results", "bold"),
        ("The questions answered fall under the individual, company, and industry related actions and choices you make every day at work.", "normal"),
        ("They address key areas from hiring through developing and retaining talent that we as company leaders make in relation to our peers, team members, superiors, and creating a broader impact on the industry.", "normal"),
        ("Take a look at the scores below and see:", "normal"),
        ("- Where do you score highest?", "normal"),
        ("- Which area has the highest potential to improve?", "normal"),
        ("- Is there anything that surprised you?", "normal"),
        ("- What are some of the actions that you can take to reduce bias and drive inclusion?", "normal"),
        ("", "normal"),  # Add a blank line for more space
        ("Capture your reflection for a later conversation.", "normal"),
        ("Development: Spans actions in the area of developing talent/your team", "bold_pre"),
        ("General: Covers general work related attitudes and actions", "bold_pre"),
        ("Recruiting & Hiring: Highlights potential bias in recruiting and hiring talent", "bold_pre"),
        ("Performance & Reward: Looks at equity in relation to this area of rewarding the team", "bold_pre"),
        ("Culture & Engagement: Your actions and attitudes related to organisational culture", "bold_pre"),
        ("Exit & Retention: Actions related to retaining and understanding the reasons for talent drain", "bold_pre")
    ]

    for explanation, style in explanations:
        if style == "bold":
            c.setFont("Helvetica-Bold", 10)
            lines = wrap_text(explanation, c, width - 2 * margin, 10)
        elif style == "bold_pre":
            text, remainder = explanation.split(":", 1)
            lines = wrap_text(text + ":", c, width - 2 * margin, 10)
            c.setFont("Helvetica-Bold", 10)
            for line in lines:
                if y - 15 < margin:
                    c.showPage()
                    y = height - margin
                c.drawString(margin, y, line)
                y -= 12
            c.setFont("Helvetica", 10)
            lines = wrap_text(remainder.strip(), c, width - 2 * margin, 10)
        else:
            c.setFont("Helvetica", 10)
            lines = wrap_text(explanation, c, width - 2 * margin, 10)

        for line in lines:
            if y - 15 < margin:
                c.showPage()
                y = height - margin
            c.drawString(margin, y, line)
            y -= 12
        y -= 5  # Add extra space between sections

    # Start a new page for the charts
    c.showPage()

    # Embed charts into the PDF, spread across up to 3 pages
    charts_per_page = 2  # Adjust as desired for better readability

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
            c.drawImage(ImageReader(img), margin, y - 300, width=width - 2 * margin, height=300)
            y -= 320
            chart_index += 1
        if chart_index >= len(chart_images):
            break
        c.showPage()

    c.save()
    buffer.seek(0)

    return buffer

def main():
    # --- Initialize or update your unique visits counter in session state ---
    if 'unique_visits' not in st.session_state:
        st.session_state.unique_visits = 0
    st.session_state.unique_visits += 1
    
    try:
        st.image(logo_path, width=200)  # Add your logo at the top
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
        "Once complete, the tool subtotals the scores by section. Reflect on areas where your scores are lower than others and identify where you can continue to grow. "
        "The assessment should take you no longer than 5 – 10 mins."
    )
    st.write("### Rating Scale: 1 = Never | 2 = Rarely | 3 = Sometimes | 4 = Often | 5 = Consistently all the time")

    # Shuffle questions once per session
    if 'shuffled_questions' not in st.session_state:
        st.session_state['shuffled_questions'] = questions_list.copy()
        random.shuffle(st.session_state['shuffled_questions'])

    # Display the questions and collect responses
    responses = display_questions()

    # Calculate the total score
    total_score = calculate_total_score(responses)

    # Calculate the total scores per category
    total_scores_per_category = calculate_total_scores_per_category(responses)

    # Calculate the maximum possible scores per category
    max_scores_per_category = calculate_max_scores_per_category(categories)

    if st.button("Submit"):
        st.write("## Assessment Complete. Here are your results:")

        st.write("### How to interpret the results")
        st.write(
            "The questions answered fall under the individual, company, and industry related actions and choices you make every day at work. "
            "They address key areas from hiring through developing and retaining talent that we as company leaders make in relation to our peers, "
            "team members, superiors, and creating a broader impact on the industry."
        )
        st.write(
            "Take a look at the scores below and see:\n"
            "- Where do you score highest?\n"
            "- Which area has the highest potential to improve?\n"
            "- Is there anything that surprised you?\n"
            "- What are some of the actions that you can take to reduce bias and drive inclusion?\n"
            "\n"
            "Capture your reflection for a later conversation."
        )
        st.write("#### Development")
        st.write("Spans actions in the area of developing talent/your team")
        st.write("#### General")
        st.write("Covers general work related attitudes and actions")
        st.write("#### Recruiting & Hiring")
        st.write("Highlights potential bias in recruiting and hiring talent")
        st.write("#### Performance & Reward")
        st.write("Looks at equity in relation to this area of rewarding the team")
        st.write("#### Culture & Engagement")
        st.write("Your actions and attitudes related to organisational culture")
        st.write("#### Exit & Retention")
        st.write("Actions related to retaining and understanding the reasons for talent drain")

        # Display total scores per category
        for category_name, score in total_scores_per_category.items():
            max_score = max_scores_per_category[category_name]
            st.write(f"**{category_name}: {score} out of {max_score}**")

            # Calculate and display custom progress bar
            progress = int((score / max_score) * 100)
            custom_progress_bar(progress)

        # Prepare data for visualization
        flattened_scores = []
        for category_name, types in categories.items():
            for type_name, questions in types.items():
                response_scores = [
                    r['score'] for r in responses
                    if r['category'] == category_name and r['type'] == type_name and type(r['score']) == int
                ]
                score = sum(response_scores)
                max_score = len(questions) * 5
                percentage = (score / max_score) * 100
                flattened_scores.append({
                    "Category": category_name,
                    "Type": type_name,
                    "Score": score,
                    "Percentage": percentage
                })

        scores_data = pd.DataFrame(flattened_scores)
        # Sort the scores_data based on the ordered categories
        ordered_categories = scores_data["Category"].unique()
        scores_data["Category"] = pd.Categorical(
            scores_data["Category"],
            categories=ordered_categories,
            ordered=True
        )
        scores_data = scores_data.sort_values(by=["Category", "Type"], ascending=[True, False])

        # Create a custom horizontal bar chart for scores (percentage)
        chart_images = custom_bar_chart(scores_data)

        # Generate and provide download link for PDF
        pdf_buffer = generate_pdf(total_scores_per_category, max_scores_per_category, chart_images)
        st.download_button(
            label="Download PDF of Results",
            data=pdf_buffer,
            file_name="assessment_results.pdf",
            mime="application/pdf"
        )

    # Smaller credit text and visitor counter at the bottom
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
