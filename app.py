from collections import deque
import streamlit as st
import pandas as pd
import graphviz
st.markdown("""
    <style>
    h1 { color: #1a237e !important; text-align: center; }
    h2, h3 { color: #1a237e !important; }
    p, label, div { color: #000000 !important; }
    .stButton>button { background-color: purple; color: white; font-size: 16px; }
    .stApp { background-color: #e8f4f8 !important; }
    [data-testid="stSidebar"] { background-color: #FF99BE !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    </style>
""", unsafe_allow_html=True)
st.title("NFA to DFA Converter")
with st.sidebar:
    st.header("How to use:")
    st.write("1. Enter states like: q0, q1, q2")
    st.write("2. Enter alphabets like: a, b")
    st.write("3. Enter initial state like: q0")
    st.write("4. Enter final states like: q2")
    st.write("5. Enter transitions like: q0,a=q0,q1;q0,b=q1")
    st.write("6. Click on \"Convert NFA to DFA\" button.")
st.write("This tool converts an NFA to DFA using Subset Construction Method.")
st.divider()
st.write("Enter the inputs: ")
states = st.text_input("Enter states (ex: q0, q1, A, B): ")
alphabets = st.text_input("Enter alphabets (ex: a, b, 0, 1): ")
initial_state = st.text_input("Enter initial state: ")
final_states = st.text_input("Enter final state/states: ")
st.subheader("Enter transitions:")
st.write("Format to be used: state,symbol=state")
trans = st.text_input("Enter transitions (ex: q0,0=q0;q1;q0,1=q1): ")
if st.button("Convert NFA to DFA"):
    if not states or not alphabets or not initial_state or not final_states:
        st.error("Please fill in all the fields before converting.")
        st.stop()
    states_list = states.replace(" ", "").split(",")
    alphabets_list = alphabets.replace(" ", "").split(",")
    initial = initial_state.replace(" ", "")
    final_states_list = final_states.replace(" ", "").split(",")
    if initial not in states_list:
        st.error(f"Initial state '{initial}' is not in the states list.")
        st.stop()
    nfa = {}
    if trans != "":
        for i in trans.split(";"):
            i = i.strip()
            if "=" not in i:
                continue
            left, right = i.split("=", maxsplit = 1)
            present_state, symbol = left.split(",")
            next_states = right.split(",")
            for ns in next_states:
                if ns not in states_list:
                    st.error(f"Transition state '{ns}' is not in the states list.")
                    st.stop()
            nfa[(present_state, symbol)] = next_states
    rows = []
    for state in states_list:
        row = {}
        row["δ"] = state
        for symbol in alphabets_list:
            if (state, symbol) in nfa:
                row[symbol] = ", ".join(nfa[(state, symbol)])
            else:
                row[symbol] = "∅"
        rows.append(row)
    df = pd.DataFrame(rows)
    st.subheader("NFA Transition Table:")
    st.dataframe(df)
    st.subheader("NFA Diagram:")
    nfa_graph = graphviz.Digraph()
    for state in states_list:
        if state in final_states_list:
            nfa_graph.node(state, shape='doublecircle')
    for (state, symbol), next_states in nfa.items():
        for next_state in next_states:
            nfa_graph.edge(state, next_state, label = symbol)
    st.graphviz_chart(nfa_graph)
    dfa_rows = []
    queue = deque()
    processed = []
    queue.append([initial])
    st.subheader("Subset Construction Steps:")
    while queue:
        present_state = queue.popleft()
        processed.append(present_state)
        st.write(f"Processing state: {present_state}")
        new_row = {}
        new_row["δ"] = str(present_state)
        for symbol in alphabets_list:
            union = []
            for state in present_state:
                nfa_row = df[df["δ"] == state]
                if len(nfa_row) > 0:
                    value = nfa_row.iloc[0][symbol]
                    if value != "∅":
                        for s in value.split(","):
                            s = s.strip()
                            if s not in union:
                                union.append(s)
            if len(union) == 0:
                new_row[symbol] = "qd"
                st.write(f"({present_state}, {symbol}) -> qd")
            else:
                new_row[symbol] = str(union)
                if sorted(union) not in [sorted(p) for p in processed] and \
                   sorted(union) not in [sorted(q) for q in queue]:
                    queue.append(union)
                    st.write(f"δ({present_state}, {symbol}) -> {union}")
                else:
                    st.write(f"{union} already present.")
                    st.write(f"δ({present_state}, {symbol}) -> {union}")
        dfa_rows.append(new_row)
    found = False
    for row in dfa_rows:
        for symbol in alphabets_list:
            if row[symbol] == "qd":
                found = True
    if found:
        dead_row = {}
        dead_row["δ"] = "qd"
        for symbol in alphabets_list:
            dead_row[symbol] = "qd"
        dfa_rows.append(dead_row)
    st.subheader("DFA Transition Table:")
    dfa_df = pd.DataFrame(dfa_rows)
    st.dataframe(dfa_df)
    st.subheader("DFA Final States:")
    for dfa_state in processed:
        if any(f in dfa_state for f in final_states_list):
            st.write(f"{dfa_state} → DFA Final State")
    st.subheader("DFA Diagram:")
    dfa_graph = graphviz.Digraph()
    for dfa_state in processed:
        if any(f in dfa_state for f in final_states_list):
            dfa_graph.node(str(dfa_state), shape='doublecircle')
    for row in dfa_rows:
        for symbol in alphabets_list:
            dfa_graph.edge(row["δ"], row[symbol], label = symbol)
    st.graphviz_chart(dfa_graph)