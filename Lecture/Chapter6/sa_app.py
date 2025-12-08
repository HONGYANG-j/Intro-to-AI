import streamlit as st
import nltk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import movie_reviews
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

# ============= NLTK DOWNLOADS (FIRST RUN ONLY) =============
nltk.download("vader_lexicon", quiet=True)
nltk.download("movie_reviews", quiet=True)

# ============= PAGE CONFIG =============
st.set_page_config(
    page_title="Comprehensive Sentiment Analyser",
    layout="wide",
)

st.title("🧠 Comprehensive Sentiment Analyser")
st.write(
    """
This app combines **lexicon-based** and **machine-learning** approaches:

1. **VADER** (lexicon-based) – good for short, informal English text.  
2. **Logistic Regression + TF-IDF** trained on the **NLTK `movie_reviews`** dataset.

Use the sidebar to choose between:
- **Single Text Analysis**
- **Batch CSV Analysis**
"""
)

# ============= MODEL LOADING (CACHED) =============

@st.cache_resource(show_spinner=True)
def load_vader():
    """Load VADER SentimentIntensityAnalyzer."""
    return SentimentIntensityAnalyzer()


@st.cache_resource(show_spinner=True)
def train_ml_model():
    """
    Train a simple sentiment classifier (pos/neg) on NLTK movie_reviews.
    Returns a scikit-learn pipeline (TF-IDF + Logistic Regression)
    and some training statistics.
    """
    # Load movie reviews
    texts = []
    labels = []
    for category in movie_reviews.categories():
        for fileid in movie_reviews.fileids(category):
            texts.append(movie_reviews.raw(fileid))
            labels.append(category)

    # Convert labels to 0 = neg, 1 = pos
    y = np.array([1 if lbl == "pos" else 0 for lbl in labels])
    X = np.array(texts)

    # Simple train/test split
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # TF-IDF + Logistic Regression pipeline
    pipe = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 2),
                stop_words="english"
            )),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )

    pipe.fit(X_train, y_train)

    # Evaluate
    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(
        y_test, y_pred, target_names=["negative", "positive"], output_dict=True
    )

    return pipe, acc, report


sia = load_vader()
ml_model, ml_acc, ml_report = train_ml_model()

# Helper to classify probability into label
def prob_to_label(p, threshold=0.5):
    return "positive" if p >= threshold else "negative"


# ============= SIDEBAR =============
st.sidebar.header("⚙️ Settings")

mode = st.sidebar.radio(
    "Select analysis mode",
    ["Single Text Analysis", "Batch CSV Analysis"],
)

show_explain = st.sidebar.checkbox(
    "Show ML model explanation (top words)", value=True
)

st.sidebar.markdown("---")
st.sidebar.subheader("ML Model Performance (on movie_reviews)")
st.sidebar.write(f"**Accuracy:** {ml_acc:.3f}")
st.sidebar.write(
    f"**Precision (pos):** {ml_report['positive']['precision']:.3f}  \n"
    f"**Recall (pos):** {ml_report['positive']['recall']:.3f}"
)

# ============= EXPLAINABILITY HELPER =============

def get_top_features(pipe, n=15):
    """
    Extract top positive and negative features based on logistic regression coefficients.
    """
    tfidf = pipe.named_steps["tfidf"]
    clf = pipe.named_steps["clf"]
    feature_names = np.array(tfidf.get_feature_names_out())
    coefs = clf.coef_[0]

    top_pos_idx = np.argsort(coefs)[-n:]
    top_neg_idx = np.argsort(coefs)[:n]

    top_pos = list(zip(feature_names[top_pos_idx], coefs[top_pos_idx]))
    top_neg = list(zip(feature_names[top_neg_idx], coefs[top_neg_idx]))

    return top_pos, top_neg


def plot_top_features(top_pos, top_neg):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Positive
    words_pos = [w for w, c in top_pos]
    scores_pos = [c for w, c in top_pos]
    axes[0].barh(words_pos, scores_pos)
    axes[0].set_title("Top Positive Features")
    axes[0].invert_yaxis()

    # Negative
    words_neg = [w for w, c in top_neg]
    scores_neg = [c for w, c in top_neg]
    axes[1].barh(words_neg, scores_neg)
    axes[1].set_title("Top Negative Features")
    axes[1].invert_yaxis()

    plt.tight_layout()
    return fig


# ============= MODE 1: SINGLE TEXT ANALYSIS =============
if mode == "Single Text Analysis":
    st.header("Single Text Sentiment Analysis")

    default_text = (
        "I really love this course! The explanations are clear and the examples "
        "are practical. However, sometimes the assignments are a bit too long."
    )

    text = st.text_area(
        "Enter text (English)",
        height=180,
        value=default_text,
    )

    if st.button("Analyse sentiment"):
        if not text.strip():
            st.warning("Please enter some text.")
        else:
            col1, col2 = st.columns(2)

            # ----- VADER -----
            with col1:
                st.subheader("VADER (Lexicon-based)")
                vs = sia.polarity_scores(text)
                st.write(vs)

                compound = vs["compound"]
                if compound >= 0.05:
                    vader_label = "positive 😀"
                elif compound <= -0.05:
                    vader_label = "negative 😞"
                else:
                    vader_label = "neutral 😐"

                st.markdown(f"**Overall VADER sentiment:** {vader_label}")

            # ----- ML MODEL -----
            with col2:
                st.subheader("ML Model (LogReg + TF-IDF)")
                prob_pos = ml_model.predict_proba([text])[0, 1]
                label = prob_to_label(prob_pos)

                st.write(
                    {
                        "Probability (positive)": float(prob_pos),
                        "Probability (negative)": float(1 - prob_pos),
                    }
                )
                st.markdown(
                    f"**Predicted label:** {label} "
                    f"{'😀' if label == 'positive' else '😞'}"
                )

            # Optional explanation
            if show_explain:
                st.markdown("---")
                st.subheader("🔍 Model Explanation (Top Features)")

                top_pos, top_neg = get_top_features(ml_model, n=15)
                fig = plot_top_features(top_pos, top_neg)
                st.pyplot(fig)

                st.caption(
                    "These are the words that most strongly push the ML model "
                    "towards **positive** or **negative** predictions."
                )

# ============= MODE 2: BATCH CSV ANALYSIS =============
elif mode == "Batch CSV Analysis":
    st.header("Batch Sentiment Analysis (CSV)")

    st.write(
        """
Upload a **CSV file** with at least one text column.
You can then:

- Compute **VADER** scores and **ML model** probabilities  
- Get an **overall sentiment distribution**  
- Download the results as CSV
"""
    )

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.subheader("Preview of uploaded data")
        st.dataframe(df.head(), use_container_width=True)

        if df.empty:
            st.warning("The uploaded CSV is empty.")
        else:
            # Let user choose the text column
            text_col = st.selectbox(
                "Select text column",
                df.columns,
            )

            if st.button("Run batch sentiment analysis"):
                texts = df[text_col].fillna("").astype(str).tolist()

                # VADER
                vader_scores = [sia.polarity_scores(t) for t in texts]
                df["vader_neg"] = [s["neg"] for s in vader_scores]
                df["vader_neu"] = [s["neu"] for s in vader_scores]
                df["vader_pos"] = [s["pos"] for s in vader_scores]
                df["vader_compound"] = [s["compound"] for s in vader_scores]

                def vader_label(comp):
                    if comp >= 0.05:
                        return "positive"
                    elif comp <= -0.05:
                        return "negative"
                    else:
                        return "neutral"

                df["vader_label"] = df["vader_compound"].apply(vader_label)

                # ML Model
                probs_pos = ml_model.predict_proba(df[text_col].astype(str))[:, 1]
                df["ml_prob_pos"] = probs_pos
                df["ml_label"] = [
                    prob_to_label(p) for p in probs_pos
                ]

                st.success("Batch sentiment analysis completed!")

                # Show distribution
                st.subheader("Sentiment distribution (VADER vs ML model)")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**VADER labels**")
                    vader_counts = df["vader_label"].value_counts()
                    st.bar_chart(vader_counts)

                with col2:
                    st.markdown("**ML model labels**")
                    ml_counts = df["ml_label"].value_counts()
                    st.bar_chart(ml_counts)

                st.subheader("Sample of analysed data")
                st.dataframe(
                    df.head(30),
                    use_container_width=True,
                )

                # Download link
                csv_out = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download full results as CSV",
                    data=csv_out,
                    file_name="sentiment_results.csv",
                    mime="text/csv",
                )

                # Optional explanation
                if show_explain:
                    st.markdown("---")
                    st.subheader("🔍 Model Explanation (Top Features)")

                    top_pos, top_neg = get_top_features(ml_model, n=15)
                    fig = plot_top_features(top_pos, top_neg)
                    st.pyplot(fig)

                    st.caption(
                        "These are the words that most strongly push the ML model "
                        "towards **positive** or **negative** predictions."
                    )

    else:
        st.info("Upload a CSV file to start the batch analysis.")
