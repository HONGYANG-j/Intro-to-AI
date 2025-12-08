import streamlit as st
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize, WordPunctTokenizer

# Make sure punkt is available
nltk.download("punkt", quiet=True)

st.set_page_config(page_title="Tokenizer Demo (NLTK)", layout="wide")

st.title("NLTK Tokenizer Demo")
st.write(
    "Explore NLTK sentence, word, and word-punct tokenizers interactively."
)

default_text = (
    "Ku Muhammad Na'im Ku Khalif is a senior lecturer at UMPSA. "
    "He works in AI, data science, and analytics, and frequently "
    "delivers talks on digital safety and Internet awareness."
)

text = st.text_area("Input text", value=default_text, height=150)

tokenizer_options = st.multiselect(
    "Select tokenizer(s)",
    ["Sentence tokenizer", "Word tokenizer", "WordPunct tokenizer"],
    default=["Sentence tokenizer", "Word tokenizer", "WordPunct tokenizer"],
)

if st.button("Run tokenizers"):
    if not text.strip():
        st.warning("Please provide some text first.")
    else:
        if "Sentence tokenizer" in tokenizer_options:
            st.subheader("Sentence tokenizer")
            sentences = sent_tokenize(text)
            st.write(sentences)

        if "Word tokenizer" in tokenizer_options:
            st.subheader("Word tokenizer")
            words = word_tokenize(text)
            st.write(words)

        if "WordPunct tokenizer" in tokenizer_options:
            st.subheader("WordPunct tokenizer")
            wp_tokens = WordPunctTokenizer().tokenize(text)
            st.write(wp_tokens)
