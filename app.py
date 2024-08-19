import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64

# Define the URLs for the FastAPI endpoints
STORY_API_URL = "http://localhost:8000/generate_story/"
IMAGE_API_URL = "http://localhost:8001/generate_images/"

def get_image_from_base64(base64_str):
    image_data = base64.b64decode(base64_str)
    return Image.open(BytesIO(image_data))

# Apply RTL direction and set the font for Arabic text
st.markdown("""
    <style>
        body {
            direction: rtl;
            font-family: 'Arial', sans-serif;
        }
        .stTextInput > div > div > input {
            text-align: right;
        }
        .stNumberInput > div > div > input {
            text-align: right;
        }
        .stButton > div > div {
            text-align: center;
        }
        .stText {
            text-align: right;
        }
        .stSubheader {
            text-align: right;
        }
        .stError {
            text-align: right;
        }
    </style>
    """, unsafe_allow_html=True)

st.title("تخيل مستقبلك")
st.write("هنا يمكنك إدخال معلوماتك الأساسية وحلمك وسنعرض لك عينة من السيناريوهات المحتملة التي نتمنى حدوثها في المستقبل")

# Initialize session state variables if they do not exist
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'age' not in st.session_state:
    st.session_state.age = 0
if 'dream' not in st.session_state:
    st.session_state.dream = ""
if 'country' not in st.session_state:
    st.session_state.country = ""

# Input fields for user details
st.session_state.name = st.text_input("الاسم", value=st.session_state.name, help="أدخل اسمك هنا")
st.session_state.age = st.number_input("العمر", min_value=0, max_value=120, value=st.session_state.age)
st.session_state.dream = st.text_input("الحلم", value=st.session_state.dream, help="أدخل حلمك هنا")
st.session_state.country = st.text_input("البلد", value=st.session_state.country, help="أدخل بلدك هنا")

if st.button("دعني أتخيل"):
    # Generate the story
    story_response = requests.post(STORY_API_URL, json={
        "name": st.session_state.name,
        "age": st.session_state.age,
        "dream": st.session_state.dream,
        "country": st.session_state.country,
    })

    if story_response.status_code == 200:
        story_data = story_response.json()
        sentences_en = story_data.get("sentences_en", [])
        sentences_ar = story_data.get("sentences_ar", [])

        # Generate images using English sentences
        image_response = requests.post(IMAGE_API_URL, json={"prompts": sentences_en})

        if image_response.status_code == 200:
            image_data = image_response.json()
            images = image_data.get("images", [])

            # Display the Arabic sentences and corresponding images
            for sentence_ar, img_base64 in zip(sentences_ar, images):
                st.subheader(sentence_ar)
                image = get_image_from_base64(img_base64)
                st.image(image, caption=sentence_ar)
        else:
            st.error("فشل في توليد الصور.")
    else:
        st.error("فشل في توليد القصة.")
