import streamlit as st
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.snowball import SnowballStemmer
import pandas as pd

st.set_page_config(page_title="Stemmer Demo (NLTK)", layout="wide")

st.title("NLTK Stemmer Demo")
st.write("Compare **Porter**, **Lancaster**, and **Snowball** stemmers.")

default_words = "writing, calves, branded, horse, randomly, possibly, provision, hospital, kept, scratchy, code"

words_input = st.text_input(
    "Input words (comma-separated)",
    value=default_words
)

if words_input.strip():
    # Build stemmer objects
    porter = PorterStemmer()
    lancaster = LancasterStemmer()
    snowball = SnowballStemmer("english")

    # Clean and split words
    words = [w.strip() for w in words_input.split(",") if w.strip()]
else:
    words = []

if st.button("Stem words"):
    if not words:
        st.warning("Please enter at least one word.")
    else:
        data = []
        for w in words:
            data.append(
                {
                    "Input word": w,
                    "Porter": porter.stem(w),
                    "Lancaster": lancaster.stem(w),
                    "Snowball": snowball.stem(w),
                }
            )

        df = pd.DataFrame(data)
        st.subheader("Stemming results")
        st.dataframe(df, use_container_width=True)
