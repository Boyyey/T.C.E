import json
import streamlit as st

from synthetic_mind.core import SyntheticMind

st.set_page_config(page_title="Synthetic Mind", page_icon="🧠", layout="wide")

if "mind" not in st.session_state:
    st.session_state.mind = SyntheticMind(trace=True)

st.title("🧠 Synthetic Mind")

with st.sidebar:
    st.header("Meta-Turing Probes")
    if st.button("Why did you say that?"):
        st.session_state.last_probe = st.session_state.mind.why_did_you_say()
    if st.button("What don't you know?"):
        st.session_state.last_probe = st.session_state.mind.what_dont_you_know()
    if st.button("Summarize chain-of-thought"):
        st.session_state.last_probe = st.session_state.mind.summarize_chain_of_thought()
    st.markdown("---")
    st.write(st.session_state.get("last_probe", ""))

col1, col2 = st.columns([3, 2])
with col1:
    st.subheader("Chat")
    if "history" not in st.session_state:
        st.session_state.history = []
    user = st.text_input("You", value="", placeholder="Type a message and press Enter")
    if user:
        reply = st.session_state.mind.step(user)
        st.session_state.history.append((user, reply))
        st.rerun()
    for u, r in reversed(st.session_state.history[-20:]):
        st.markdown(f"**You**: {u}")
        st.markdown(f"**Mind**: {r}")

with col2:
    st.subheader("Trace")
    trace = getattr(st.session_state.mind, "last_trace", {})
    st.json(trace)
