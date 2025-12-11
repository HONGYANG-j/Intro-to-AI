import streamlit as st
import nltk
from nltk.stem import WordNetLemmatizer
import pandas as pd

# Ensure required resources are present
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

st.set_page_config(page_title="Lemmatizer Demo (NLTK)", layout="wide")

st.title("NLTK Lemmatizer Demo")
st.write("Compare **noun** and **verb** lemmatization for each word.")

default_words = (
    "writing, calves, be, branded, horse, random, possibly, "
    "provision, hospital, kept, scratchy, code, bad, worse"
)

words_input = st.text_input(
    "Input words (comma-separated)",
    value=default_words
)

if words_input.strip():
    words = [w.strip() for w in words_input.split(",") if w.strip()]
else:
    words = []

lemmatizer = WordNetLemmatizer()

if st.button("Lemmatize words"):
    if not words:
        st.warning("Please enter at least one word.")
    else:
        rows = []
        for w in words:
            rows.append(
                {
                    "Input word": w,
                    "Noun lemma (pos='n')": lemmatizer.lemmatize(w, pos="n"),
                    "Verb lemma (pos='v')": lemmatizer.lemmatize(w, pos="v"),
                }
            )
        df = pd.DataFrame(rows)
        st.subheader("Lemmatization results")
        st.dataframe(df, use_container_width=True)
