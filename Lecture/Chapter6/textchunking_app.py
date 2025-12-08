import streamlit as st

st.set_page_config(page_title="Text Chunker (Word-based)", layout="wide")

st.title("Text Chunker (by Number of Words)")

st.write(
    "This app splits a long text into chunks, where each chunk contains **N words** "
    "similar to your `chunker(input_data, N)` function."
)

def chunker(input_data: str, N: int):
    input_words = input_data.split()
    output = []
    cur_chunk = []
    count = 0
    for word in input_words:
        cur_chunk.append(word)
        count += 1
        if count == N:
            output.append(" ".join(cur_chunk))
            count, cur_chunk = 0, []
    # Add remaining words (if any)
    if cur_chunk:
        output.append(" ".join(cur_chunk))
    return output

default_text = (
    "Ku Muhammad Na'im Ku Khalif is actively involved in teaching, research, and "
    "community outreach. He regularly works with AI, data science, and Internet "
    "safety campaigns across schools in Pahang, collaborating with various agencies."
)

text = st.text_area("Input text", value=default_text, height=200)

chunk_size = st.number_input(
    "Number of words per chunk (N)",
    min_value=1,
    max_value=2000,
    value=20,
    step=1,
)

if st.button("Create chunks"):
    if not text.strip():
        st.warning("Please provide some text to chunk.")
    else:
        chunks = chunker(text, int(chunk_size))
        st.success(f"Number of text chunks = {len(chunks)}")

        # Let user select which chunk to view
        idx = st.number_input(
            "Select chunk index to view",
            min_value=1,
            max_value=len(chunks),
            value=1,
            step=1,
        )
        st.subheader(f"Chunk {idx}")
        st.write(chunks[idx - 1])

        with st.expander("Show all chunks"):
            for i, ch in enumerate(chunks, start=1):
                st.markdown(f"**Chunk {i}**")
                st.write(ch)
                st.markdown("---")
