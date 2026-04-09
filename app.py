from collections import deque, defaultdict
import streamlit as st
import pandas as pd
import time
import json

st.set_page_config(page_title="NFA to DFA Converter", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Fira+Code:wght@400;500&display=swap');

*, body { font-family: 'Nunito', sans-serif !important; }

.stApp {
    background: linear-gradient(135deg, #fdf0ff 0%, #fce4ec 50%, #f3e5f5 100%);
    min-height: 100vh;
}
.block-container { padding: 2rem 3rem 4rem 3rem; max-width: 1100px; }
#MainMenu, footer, header { visibility: hidden; }
h1,h2,h3 { color: #6a1b9a !important; }

.main-title {
    text-align: center;
    font-size: 54px;
    font-weight: 900;
    background: linear-gradient(135deg, #8e24aa, #e91e63, #f06292);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 4px;
}

.section-head {
    font-size: 20px;
    font-weight: 800;
    color: #8e24aa;
    border-bottom: 3px solid #f48fb1;
    padding-bottom: 6px;
    margin: 28px 0 14px 0;
}

.sep {
    height: 3px;
    background: linear-gradient(90deg, transparent, #f06292, #ba68c8, transparent);
    border: none;
    border-radius: 4px;
    margin: 28px 0;
}

.instr-box {
    background: linear-gradient(135deg, #fff0f8, #f3e5f5);
    border: 2px solid #ce93d8;
    border-radius: 20px;
    padding: 24px 32px;
    box-shadow: 0 4px 28px rgba(142,36,170,0.10);
    margin: 18px 0;
}
.instr-step {
    display: flex;
    align-items: flex-start;
    margin: 12px 0;
    gap: 14px;
}
.instr-num {
    background: linear-gradient(135deg, #ba68c8, #f06292);
    color: white;
    border-radius: 50%;
    min-width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 13px;
    flex-shrink: 0;
}
.instr-text { color: #4a148c; font-size: 15px; line-height: 1.6; }
.code-ex {
    background: #fff0f8;
    border: 1.5px solid #f48fb1;
    border-radius: 8px;
    padding: 6px 14px;
    font-family: 'Fira Code', monospace !important;
    font-size: 13px;
    color: #880e4f;
    display: inline-block;
    margin: 2px 4px;
}

.stTextArea textarea {
    background: #ffffff !important;
    color: #2d0052 !important;
    caret-color: #8e24aa !important;
    border: 2px solid #ce93d8 !important;
    border-radius: 14px !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 14px !important;
    padding: 12px !important;
    box-shadow: 0 2px 10px rgba(142,36,170,0.08) !important;
}
.stTextArea textarea:focus {
    border-color: #8e24aa !important;
    box-shadow: 0 0 0 3px rgba(142,36,170,0.18) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder {
    color: #b39ddb !important;
    opacity: 1 !important;
}
.stTextInput input {
    background: #ffffff !important;
    color: #2d0052 !important;
    caret-color: #8e24aa !important;
    border: 2px solid #ce93d8 !important;
    border-radius: 14px !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    box-shadow: 0 2px 10px rgba(142,36,170,0.08) !important;
}
.stTextInput input:focus {
    border-color: #8e24aa !important;
    box-shadow: 0 0 0 3px rgba(142,36,170,0.18) !important;
    outline: none !important;
}
.stTextInput input::placeholder {
    color: #b39ddb !important;
    opacity: 1 !important;
}

.stMultiSelect { overflow: visible !important; }
.stMultiSelect > div { overflow: visible !important; }
.stMultiSelect > div > div {
    background: #ffffff !important;
    border: 2px solid #ce93d8 !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 10px rgba(142,36,170,0.08) !important;
    overflow: visible !important;
}
.stMultiSelect [data-baseweb="select"] {
    overflow: visible !important;
}
.stMultiSelect [data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #2d0052 !important;
    overflow: visible !important;
    flex-wrap: wrap !important;
    min-height: 48px !important;
    padding: 8px 10px !important;
    gap: 6px !important;
    align-items: center !important;
    clip: unset !important;
    clip-path: none !important;
}
.stMultiSelect input {
    color: #2d0052 !important;
    caret-color: #8e24aa !important;
    background: transparent !important;
    min-width: 60px !important;
}
[data-baseweb="select"] [data-baseweb="tag"] {
    background: #ede7f6 !important;
    border: 1.5px solid #ba68c8 !important;
    border-radius: 20px !important;
    padding: 4px 8px 4px 12px !important;
    margin: 2px !important;
    display: inline-flex !important;
    align-items: center !important;
    flex-direction: row !important;
    flex-shrink: 0 !important;
    max-width: none !important;
    width: auto !important;
    overflow: visible !important;
    clip: unset !important;
    clip-path: none !important;
    position: relative !important;
    left: 0 !important;
}
[data-baseweb="select"] [data-baseweb="tag"] span,
[data-baseweb="select"] [data-baseweb="tag"] div,
[data-baseweb="select"] [data-baseweb="tag"] [role="presentation"] {
    color: #4a148c !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: clip !important;
    max-width: none !important;
    width: auto !important;
    display: inline !important;
    opacity: 1 !important;
    visibility: visible !important;
    clip: unset !important;
    clip-path: none !important;
}
[data-baseweb="popover"] ul li {
    background: #fff9fc !important;
    color: #2d0052 !important;
}
[data-baseweb="popover"] ul li:hover {
    background: #f3e5f5 !important;
}
[data-baseweb="popover"] {
    background: #fff9fc !important;
}
[data-baseweb="menu"] {
    background: #fff9fc !important;
}
[data-baseweb="option"] {
    background: #fff9fc !important;
    color: #2d0052 !important;
}
[role="listbox"] {
    background: #fff9fc !important;
}
[role="option"] {
    background: #fff9fc !important;
    color: #2d0052 !important;
}
[role="option"]:hover {
    background: #f3e5f5 !important;
}

label {
    color: #4a148c !important;
    font-weight: 800 !important;
    font-size: 15px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ba68c8, #f06292) !important;
    color: white !important;
    border: none !important;
    border-radius: 30px !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    padding: 0.65rem 2.5rem !important;
    box-shadow: 0 4px 18px rgba(240,98,146,0.30) !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(240,98,146,0.40) !important;
}

.stDataFrame { border-radius: 14px !important; overflow: hidden; }
div[data-testid="stDataFrame"] {
    border: 2px solid #f8bbd0;
    border-radius: 14px;
    overflow: hidden;
}

.card-lavender {
    background: linear-gradient(120deg, #f8f0ff, #ede7f6);
    border: 1.5px solid #ce93d8;
    border-radius: 18px;
    padding: 18px 22px;
    margin: 0;
    box-shadow: 0 2px 14px rgba(142,36,170,0.08);
}
.card-pink {
    background: linear-gradient(120deg, #fff0f6, #fce4ec);
    border: 1.5px solid #f48fb1;
    border-radius: 18px;
    padding: 18px 22px;
    margin: 14px 0;
    box-shadow: 0 2px 14px rgba(240,98,146,0.10);
}

.badge {
    display: inline-block;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 13px;
    font-weight: 700;
    margin: 3px;
}
.badge-start { background:#e1bee7; color:#4a148c; border:1.5px solid #ba68c8; }
.badge-final { background:#fce4ec; color:#880e4f; border:1.5px solid #f48fb1; }
.badge-state { background:#f3e5f5; color:#6a1b9a; border:1.5px solid #ce93d8; }

.step-state {
    background: linear-gradient(120deg, #fff8e1, #fff3e0);
    border-left: 5px solid #f06292;
    border-radius: 0 14px 14px 0;
    padding: 12px 18px;
    margin: 10px 0 4px 0;
    font-size: 15px;
    font-weight: 700;
    color: #4a148c;
}
.step-trans {
    background: linear-gradient(120deg, #fdf6ff, #fff0fa);
    border-left: 5px solid #ba68c8;
    border-radius: 0 14px 14px 0;
    padding: 10px 18px 10px 32px;
    margin: 3px 0;
    font-size: 14px;
    color: #4a148c;
}
.step-new {
    background: linear-gradient(120deg, #e8f5e9, #f9fbe7);
    border-left: 5px solid #43a047;
    border-radius: 0 14px 14px 0;
    padding: 10px 18px 10px 32px;
    margin: 3px 0;
    font-size: 14px;
    color: #1b5e20;
    font-weight: 700;
}
.step-dead-intro {
    background: linear-gradient(120deg, #fce4ec, #fff0f6);
    border-left: 5px solid #e53935;
    border-radius: 0 14px 14px 0;
    padding: 10px 18px 10px 32px;
    margin: 3px 0;
    font-size: 14px;
    color: #b71c1c;
    font-weight: 700;
}
.step-dead {
    background: linear-gradient(120deg, #fafafa, #f5f5f5);
    border-left: 5px solid #757575;
    border-radius: 0 14px 14px 0;
    padding: 10px 18px 10px 32px;
    margin: 3px 0;
    font-size: 14px;
    color: #424242;
    font-weight: 700;
}
.step-done {
    background: linear-gradient(120deg, #e8f5e9, #f1f8e9);
    border-left: 5px solid #66bb6a;
    border-radius: 0 14px 14px 0;
    padding: 12px 18px;
    margin: 10px 0 4px 0;
    font-size: 15px;
    font-weight: 700;
    color: #1b5e20;
}
.step-already {
    background: linear-gradient(120deg, #e3f2fd, #e8eaf6);
    border-left: 5px solid #1e88e5;
    border-radius: 0 14px 14px 0;
    padding: 10px 18px 10px 32px;
    margin: 3px 0;
    font-size: 14px;
    color: #0d47a1;
    font-weight: 600;
}
.step-epsilon {
    background: linear-gradient(120deg, #f3e5f5, #ede7f6);
    border-left: 5px solid #8e24aa;
    border-radius: 0 14px 14px 0;
    padding: 10px 18px 10px 32px;
    margin: 3px 0;
    font-size: 14px;
    color: #4a148c;
    font-weight: 600;
}

.step-diagram-card {
    background: linear-gradient(120deg, #fdf6ff, #fff0fa);
    border: 1.5px solid #ce93d8;
    border-radius: 18px;
    padding: 16px 20px 12px 20px;
    margin: 14px 0;
    box-shadow: 0 2px 14px rgba(142,36,170,0.08);
}
.step-diagram-label {
    font-size: 14px;
    font-weight: 800;
    color: #6a1b9a;
    margin-bottom: 8px;
    padding: 6px 14px;
    background: linear-gradient(90deg, #fce4ec, #f3e5f5);
    border-radius: 10px;
    border: 1px solid #f8bbd0;
    display: inline-block;
}

.epsilon-box {
    background: linear-gradient(135deg, #f3e5f5, #ede7f6);
    border: 2px solid #ba68c8;
    border-radius: 14px;
    padding: 14px 20px;
    margin: 10px 0 18px 0;
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
}
.epsilon-symbol {
    font-size: 28px;
    font-weight: 900;
    color: #6a1b9a;
    font-family: 'Fira Code', monospace;
    background: #fff0f8;
    border: 2px solid #f48fb1;
    border-radius: 10px;
    padding: 4px 16px;
    cursor: pointer;
    user-select: all;
    letter-spacing: 2px;
}
.epsilon-label {
    color: #4a148c;
    font-size: 14px;
    font-weight: 700;
}
.epsilon-hint {
    color: #8e24aa;
    font-size: 13px;
    font-style: italic;
}

p, div, span, li { color: #4a148c; }
</style>
""", unsafe_allow_html=True)

EPSILON = "\u03b5"


def compute_epsilon_closure(nfa, states):
    closure = set(states)
    stack = list(states)
    while stack:
        s = stack.pop()
        for ns in nfa.get((s, EPSILON), []):
            if ns not in closure:
                closure.add(ns)
                stack.append(ns)
    return frozenset(closure)


def parse_input(text, extra_alpha_str=""):
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if not lines:
        return None, ["No transitions provided. Please enter at least one transition."]

    nfa = {}
    states_set = set()
    alpha_set = set()
    errors = []

    for i, line in enumerate(lines, 1):
        if "=" in line:
            sep = "="
        elif "->" in line:
            sep = "->"
        else:
            errors.append(f"Line {i}: '{line}' - invalid format. Expected: state,symbol=nextstate or state,symbol->nextstate")
            continue

        parts = line.split(sep, 1)
        if len(parts) != 2:
            errors.append(f"Line {i}: '{line}' - could not split on '{sep}'. Check your format.")
            continue

        left, right = parts[0].strip(), parts[1].strip()

        if "," not in left:
            errors.append(f"Line {i}: '{left}' - missing comma between state and symbol. Expected: state,symbol")
            continue

        comma = left.rfind(",")
        state = left[:comma].strip()
        sym = left[comma+1:].strip()

        if not state:
            errors.append(f"Line {i}: empty state name before the comma.")
            continue
        if not sym:
            errors.append(f"Line {i}: empty symbol after the comma in '{left}'.")
            continue

        dest_states = [d.strip() for d in right.split(",") if d.strip()]
        if not dest_states:
            errors.append(f"Line {i}: no destination state provided after '{sep}' in '{line}'.")
            continue

        states_set.add(state)
        if sym != EPSILON:
            alpha_set.add(sym)
        for d in dest_states:
            states_set.add(d)

        if (state, sym) in nfa:
            for d in dest_states:
                if d not in nfa[(state, sym)]:
                    nfa[(state, sym)].append(d)
        else:
            nfa[(state, sym)] = dest_states

    if errors:
        return None, errors

    if extra_alpha_str.strip():
        for a in extra_alpha_str.split(","):
            a = a.strip()
            if a and a != EPSILON:
                alpha_set.add(a)

    first_line = lines[0]
    sep = "=" if "=" in first_line else "->"
    left_part = first_line.split(sep, 1)[0].strip()
    comma = left_part.rfind(",")
    initial = left_part[:comma].strip()

    has_epsilon = any(sym == EPSILON for (_, sym) in nfa.keys())

    return {
        "nfa": nfa,
        "states": sorted(states_set),
        "alphabets": sorted(alpha_set),
        "initial": initial,
        "has_epsilon": has_epsilon,
    }, None


def build_graph_html(states, edges, final_states, initial_state,
                     highlighted_state=None, highlighted_edges=None, title=""):
    nodes = []
    for s in states:
        is_init = (s == initial_state)
        is_final = (s in final_states)
        is_dead = (s == "qd")

        if s == highlighted_state:
            bg, border = "#ff8a65", "#e64a19"
        elif is_dead:
            bg, border = "#bdbdbd", "#757575"
        elif is_init and is_final:
            bg, border = "#a5d6a7", "#2e7d32"
        elif is_init:
            bg, border = "#80cbc4", "#00695c"
        elif is_final:
            bg, border = "#f48fb1", "#c2185b"
        else:
            bg, border = "#ce93d8", "#8e24aa"

        sz = 36 if s == highlighted_state else 30
        border_width = 4 if is_final else 2

        if "," in s:
            display_label = "[" + s + "]"
        else:
            display_label = s

        nodes.append({
            "id": s,
            "label": display_label,
            "color": {
                "background": bg,
                "border": border,
                "highlight": {"background": "#ffcc02", "border": "#f57f17"}
            },
            "font": {"color": "#4a148c", "size": 14, "face": "Nunito", "bold": True},
            "size": sz,
            "shape": "ellipse",
            "borderWidth": border_width,
        })

    edge_map = {}
    for (src, dst, label) in edges:
        key = (src, dst)
        if key in edge_map:
            edge_map[key]["labels"].append(label)
        else:
            edge_map[key] = {"labels": [label], "highlighted": False}

    if highlighted_edges:
        for (src, dst, label) in highlighted_edges:
            key = (src, dst)
            if key in edge_map:
                edge_map[key]["highlighted"] = True

    edge_list = []
    curve_count = defaultdict(int)
    for (src, dst), info in edge_map.items():
        combined_label = ", ".join(sorted(set(info["labels"])))
        is_hi = info["highlighted"]
        is_self = (src == dst)
        curve_count[(src, dst)] += 1
        roundness = 0.3 if curve_count[(src, dst)] > 1 else 0.2

        if is_self:
            smooth_type = "curvedCCW"
        else:
            smooth_type = "curvedCW"

        edge_list.append({
            "from": src,
            "to": dst,
            "label": combined_label,
            "color": {"color": "#e64a19" if is_hi else "#8e24aa", "highlight": "#f57f17"},
            "width": 3 if is_hi else 2,
            "font": {"color": "#4a148c", "size": 13, "strokeWidth": 0, "face": "Nunito"},
            "arrows": "to",
            "smooth": {"type": smooth_type, "roundness": roundness},
        })

    nodes.append({"id": "__start__", "label": "", "size": 1,
                  "color": {"background": "transparent", "border": "transparent"}, "shape": "dot"})
    edge_list.append({"from": "__start__", "to": initial_state,
                      "color": {"color": "#00695c"}, "width": 2,
                      "arrows": "to", "label": "start",
                      "font": {"color": "#00695c", "size": 12, "face": "Nunito"},
                      "smooth": {"type": "straight"}})

    legend = (
        "<div id='legend'>"
        "<span style='color:#00695c;font-weight:700;'>Teal = Start</span> &nbsp;|&nbsp; "
        "<span style='color:#c2185b;font-weight:700;'>Pink = Final</span> &nbsp;|&nbsp; "
        "<span style='color:#8e24aa;font-weight:700;'>Purple = Normal</span> &nbsp;|&nbsp; "
        "<span style='color:#e64a19;font-weight:700;'>Orange = Active</span> &nbsp;|&nbsp; "
        "<span style='color:#757575;font-weight:700;'>Grey = Dead (qd)</span>"
        "</div>"
    )

    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<script src='https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js'></script>"
        "<link href='https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css' rel='stylesheet'/>"
        "<style>"
        "body{margin:0;background:transparent;font-family:Nunito,sans-serif;}"
        "#title-bar{font-family:Nunito,sans-serif;font-size:13px;font-weight:700;color:#6a1b9a;"
        "background:linear-gradient(90deg,#fce4ec,#f3e5f5);padding:7px 16px;"
        "border-radius:12px 12px 0 0;border:1.5px solid #f8bbd0;border-bottom:none;}"
        "#graph{width:100%;height:320px;border:1.5px solid #f8bbd0;"
        "background:#fff9fc;}"
        "#legend{font-family:Nunito,sans-serif;font-size:12px;color:#4a148c;"
        "background:#fff0f8;padding:6px 16px;"
        "border:1.5px solid #f8bbd0;border-top:none;"
        "border-radius:0 0 12px 12px;}"
        "</style></head><body>"
        "<div id='title-bar'>" + title + "</div>"
        "<div id='graph'></div>"
        + legend +
        "<script>"
        "var nodes=new vis.DataSet(" + json.dumps(nodes) + ");"
        "var edges=new vis.DataSet(" + json.dumps(edge_list) + ");"
        "var net=new vis.Network(document.getElementById('graph'),{nodes,edges},{"
        "physics:{enabled:true,stabilization:{iterations:200},"
        "barnesHut:{gravitationalConstant:-3500,springLength:140}},"
        "interaction:{hover:true,zoomView:true,dragView:true},"
        "layout:{improvedLayout:true}});"
        "</script></body></html>"
    )
    return html


def build_step_graph_html(states, edges, final_states, initial_state, height=260):
    nodes = []
    for s in states:
        is_init = (s == initial_state)
        is_final = (s in final_states)
        is_dead = (s == "qd")

        if is_dead:
            bg, border = "#bdbdbd", "#757575"
        elif is_init and is_final:
            bg, border = "#a5d6a7", "#2e7d32"
        elif is_init:
            bg, border = "#80cbc4", "#00695c"
        elif is_final:
            bg, border = "#f48fb1", "#c2185b"
        else:
            bg, border = "#ce93d8", "#8e24aa"

        border_width = 4 if is_final else 2

        if "," in s:
            display_label = "[" + s + "]"
        else:
            display_label = s

        nodes.append({
            "id": s,
            "label": display_label,
            "color": {
                "background": bg,
                "border": border,
                "highlight": {"background": "#ffcc02", "border": "#f57f17"}
            },
            "font": {"color": "#4a148c", "size": 14, "face": "Nunito", "bold": True},
            "size": 30,
            "shape": "ellipse",
            "borderWidth": border_width,
        })

    edge_map = {}
    for (src, dst, label) in edges:
        key = (src, dst)
        if key in edge_map:
            edge_map[key].append(label)
        else:
            edge_map[key] = [label]

    edge_list = []
    for (src, dst), labels in edge_map.items():
        combined_label = ", ".join(sorted(set(labels)))
        is_self = (src == dst)
        smooth_type = "curvedCCW" if is_self else "curvedCW"
        edge_list.append({
            "from": src,
            "to": dst,
            "label": combined_label,
            "color": {"color": "#e64a19", "highlight": "#f57f17"},
            "width": 3,
            "font": {"color": "#4a148c", "size": 13, "strokeWidth": 0, "face": "Nunito"},
            "arrows": "to",
            "smooth": {"type": smooth_type, "roundness": 0.25},
        })

    if initial_state in [s for s in states]:
        nodes.append({"id": "__start__", "label": "", "size": 1,
                      "color": {"background": "transparent", "border": "transparent"}, "shape": "dot"})
        edge_list.append({"from": "__start__", "to": initial_state,
                          "color": {"color": "#00695c"}, "width": 2,
                          "arrows": "to", "label": "start",
                          "font": {"color": "#00695c", "size": 12, "face": "Nunito"},
                          "smooth": {"type": "straight"}})

    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<script src='https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js'></script>"
        "<link href='https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css' rel='stylesheet'/>"
        "<style>"
        "body{margin:0;background:transparent;font-family:Nunito,sans-serif;}"
        "#graph{width:100%;height:" + str(height) + "px;background:#fff9fc;"
        "border-radius:12px;border:1.5px solid #f8bbd0;}"
        "</style></head><body>"
        "<div id='graph'></div>"
        "<script>"
        "var nodes=new vis.DataSet(" + json.dumps(nodes) + ");"
        "var edges=new vis.DataSet(" + json.dumps(edge_list) + ");"
        "var net=new vis.Network(document.getElementById('graph'),{nodes,edges},{"
        "physics:{enabled:true,stabilization:{iterations:300},"
        "barnesHut:{gravitationalConstant:-4000,springLength:160}},"
        "interaction:{hover:true,zoomView:true,dragView:true},"
        "layout:{improvedLayout:true}});"
        "</script></body></html>"
    )
    return html


def frozenset_to_str(fs):
    if not fs:
        return "qd"
    return ",".join(sorted(fs))


def run_subset_construction(nfa, alphabets_list, initial_state, final_states):
    dead_state_label = "qd"
    initial_closure = compute_epsilon_closure(nfa, frozenset([initial_state]))
    initial_frozen = initial_closure

    queue = deque()
    queue.append(initial_frozen)
    visited = {}
    order = []
    dfa_transitions = {}
    has_dead = False
    discovered = set()
    discovered.add(frozenset_to_str(initial_frozen))

    steps_log = []

    while queue:
        current_frozen = queue.popleft()
        current_str = frozenset_to_str(current_frozen)

        if current_str in visited:
            continue

        visited[current_str] = current_frozen
        order.append(current_str)

        epsilon_closure_members = sorted(current_frozen)
        step_info = {
            "state": current_str,
            "epsilon_closure": epsilon_closure_members,
            "transitions": [],
        }

        for sym in alphabets_list:
            reachable = set()
            for s in current_frozen:
                for ns in nfa.get((s, sym), []):
                    reachable.add(ns)

            if reachable:
                reachable = compute_epsilon_closure(nfa, reachable)

            if not reachable:
                nxt_str = dead_state_label
                is_first_dead = not has_dead
                has_dead = True
                dfa_transitions[(current_str, sym)] = dead_state_label
                step_info["transitions"].append({
                    "sym": sym,
                    "nxt": dead_state_label,
                    "is_new": False,
                    "is_dead": True,
                    "is_first_dead": is_first_dead,
                    "from_dead": False,
                    "reachable_before_closure": [],
                    "reachable_after_closure": [],
                })
            else:
                nxt_frozen = frozenset(reachable)
                nxt_str = frozenset_to_str(nxt_frozen)
                dfa_transitions[(current_str, sym)] = nxt_str
                is_new = nxt_str not in discovered
                if is_new:
                    discovered.add(nxt_str)
                    queue.append(nxt_frozen)
                step_info["transitions"].append({
                    "sym": sym,
                    "nxt": nxt_str,
                    "is_new": is_new,
                    "is_dead": False,
                    "is_first_dead": False,
                    "from_dead": False,
                    "reachable_after_closure": sorted(reachable),
                })

        steps_log.append(step_info)

    if has_dead:
        dead_step = {
            "state": dead_state_label,
            "epsilon_closure": [],
            "transitions": [],
        }
        for sym in alphabets_list:
            dfa_transitions[(dead_state_label, sym)] = dead_state_label
            dead_step["transitions"].append({
                "sym": sym,
                "nxt": dead_state_label,
                "is_new": False,
                "is_dead": True,
                "is_first_dead": False,
                "from_dead": True,
                "reachable_after_closure": [],
            })
        steps_log.append(dead_step)
        order.append(dead_state_label)

    dfa_final = []
    for s_str, s_frozen in visited.items():
        if any(f in s_frozen for f in final_states):
            dfa_final.append(s_str)

    return order, dfa_transitions, dfa_final, has_dead, steps_log


def render_ui():
    st.markdown("""
    <div style='text-align:center; padding: 18px 0 6px;'>
      <div class='main-title'>NFA to DFA Converter</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sep'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='instr-box'>
      <div style='font-size:20px; font-weight:800; color:#8e24aa; margin-bottom:16px;'>How to Use</div>
      <div class='instr-step'>
        <div class='instr-num'>1</div>
        <div class='instr-text'>Enter transitions below - one per line using the format:<br>
          <span class='code-ex'>state,symbol=nextstate1,nextstate2</span>
          &nbsp; or &nbsp;
          <span class='code-ex'>state,symbol->nextstate</span>
        </div>
      </div>
      <div class='instr-step'>
        <div class='instr-num'>2</div>
        <div class='instr-text'>The <b>first state</b> in the first transition is automatically the <b>start state</b>.</div>
      </div>
      <div class='instr-step'>
        <div class='instr-num'>3</div>
        <div class='instr-text'>States and alphabets are <b>extracted automatically</b>. If any extra alphabets are provided, include them in the field below - if there is no extra alphabet, leave it blank and detected symbols will be used.</div>
      </div>
      <div class='instr-step'>
        <div class='instr-num'>4</div>
        <div class='instr-text'>For <b>epsilon transitions</b>, use the symbol <b>{EPSILON}</b> as the transition symbol. You can copy it from the box below.</div>
      </div>
      <div class='instr-step'>
        <div class='instr-num'>5</div>
        <div class='instr-text'>Select <b>final states</b> from the dropdown, then click <b>Convert</b>.</div>
      </div>
      <div style='margin-top:16px; padding:14px 18px; background:#fff0f8; border-radius:12px; border:1px solid #f8bbd0;'>
        <b style='color:#880e4f;'>Example input (with epsilon):</b><br>
        <span style='font-family:Fira Code,monospace; font-size:13px; color:#4a148c; line-height:2;'>
          q0,{EPSILON}=q1<br>q0,a=q0<br>q1,b=q2<br>q2,{EPSILON}=q0
        </span>
        <br><br>
        <b style='color:#880e4f;'>Example input (without epsilon):</b><br>
        <span style='font-family:Fira Code,monospace; font-size:13px; color:#4a148c; line-height:2;'>
          q0,a=q0,q1<br>q0,b=q0<br>q1,a=q2<br>q1,b=q2<br>q2,a=q2<br>q2,b=q2
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='epsilon-box'>
      <span class='epsilon-label'>Epsilon symbol for copy-paste:</span>
      <span class='epsilon-symbol' title='Click and copy this symbol'>{EPSILON}</span>
      <span class='epsilon-hint'>Select and copy {EPSILON} above to use in transitions (e.g. q0,{EPSILON}=q1)</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sep'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-head'>Enter Transitions</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        trans_text = st.text_area(
            "Transitions (one per line)",
            placeholder=f"q0,a=q0,q1\nq0,b=q0\nq1,{EPSILON}=q2\nq2,a=q2",
            height=180,
        )
    with col2:
        st.markdown(f"""
        <div class='card-lavender' style='height:100%; box-sizing:border-box;'>
          <b style='color:#6a1b9a; font-size:15px;'>Format Guide</b><br><br>
          <span style='font-size:13px; color:#4a148c;'>
          Basic:<br>
          <code style='background:#f3e5f5; padding:2px 6px; border-radius:4px; color:#880e4f;'>q0,a=q1</code><br><br>
          Multiple destinations:<br>
          <code style='background:#f3e5f5; padding:2px 6px; border-radius:4px; color:#880e4f;'>q0,a=q1,q2</code><br><br>
          Epsilon transition:<br>
          <code style='background:#f3e5f5; padding:2px 6px; border-radius:4px; color:#880e4f;'>q0,{EPSILON}=q1</code><br><br>
          Arrow style also works:<br>
          <code style='background:#f3e5f5; padding:2px 6px; border-radius:4px; color:#880e4f;'>q0,a->q1</code><br><br>
          <b style='color:#e91e63;'>First line state = Start state</b>
          </span>
        </div>
        """, unsafe_allow_html=True)

    col3, _ = st.columns([1, 1])
    with col3:
        extra_alpha = st.text_input(
            "Extra alphabets (optional, comma-separated - leave blank to use detected symbols only)",
            placeholder="e.g. c, d",
        )

    parsed, errors = None, None
    if trans_text and trans_text.strip():
        parsed, errors = parse_input(trans_text, extra_alpha)

    final_states = []
    if parsed and not errors:
        st.markdown("<div class='section-head'>Select Final States</div>", unsafe_allow_html=True)

        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            final_states = st.multiselect(
                "Final States",
                options=parsed["states"],
                default=[],
                key="final_states_selector",
            )
        with col_f2:
            badges_states = " ".join(
                f"<span class='badge badge-state'>{s}</span>" for s in parsed['states']
            )
            badges_alpha = " ".join(
                f"<span class='badge badge-state'>{a}</span>" for a in parsed['alphabets']
            )
            has_eps_badge = ""
            if parsed.get("has_epsilon"):
                has_eps_badge = f"<br><br><b>Epsilon transitions:</b> <span class='badge badge-final'>{EPSILON}-NFA detected</span>"
            st.markdown(f"""
            <div class='card-pink' style='margin-top:0; padding:14px 18px;'>
              <b style='color:#880e4f;'>Detected automatically:</b><br><br>
              <b>Start state:</b> <span class='badge badge-start'>{parsed['initial']}</span><br><br>
              <b>States:</b> {badges_states}<br><br>
              <b>Alphabets (excl. {EPSILON}):</b> {badges_alpha}{has_eps_badge}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if errors:
        for e in errors:
            st.error(f"Error: {e}")
        return

    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    with col_b2:
        convert = st.button("Convert", use_container_width=True)

    if not convert or not parsed:
        if not trans_text or not trans_text.strip():
            st.markdown("""
            <div style='text-align:center; padding:40px 0; margin-top:20px;
                        background:rgba(255,255,255,0.6); border-radius:20px;
                        border:2px dashed #f8bbd0;'>
              <div style='font-size:22px; font-weight:800; color:#8e24aa;'>Ready to Convert</div>
              <div style='color:#ad84c8; font-size:15px; margin-top:8px;'>
                Enter your NFA transitions above and click Convert.
              </div>
            </div>
            """, unsafe_allow_html=True)
        return

    if not final_states:
        st.warning("No final states selected - the DFA will have no accepting states.")

    nfa = parsed["nfa"]
    states_list = parsed["states"]
    alphabets_list = parsed["alphabets"]
    initial_state = parsed["initial"]
    has_epsilon = parsed.get("has_epsilon", False)

    final_states_clean = [str(s) for s in final_states]

    st.markdown("<div class='sep'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-head'>NFA Transition Table</div>", unsafe_allow_html=True)

    if has_epsilon:
        st.markdown(f"""
        <div class='step-epsilon' style='margin-bottom:12px;'>
          This is an {EPSILON}-NFA. The transition table includes an {EPSILON} column showing epsilon transitions.
          The DFA conversion will apply {EPSILON}-closure at every step.
        </div>
        """, unsafe_allow_html=True)

    nfa_cols = alphabets_list + ([EPSILON] if has_epsilon else [])
    nfa_rows = []
    for state in states_list:
        label = state
        if state == initial_state:
            label = "-> " + label
        if state in final_states_clean:
            label = label + " *"
        row = {"State": label}
        for sym in alphabets_list:
            row[sym] = ", ".join(nfa[(state, sym)]) if (state, sym) in nfa else "\u03d5"
        if has_epsilon:
            row[EPSILON] = ", ".join(nfa[(state, EPSILON)]) if (state, EPSILON) in nfa else "\u03d5"
        nfa_rows.append(row)
    st.dataframe(pd.DataFrame(nfa_rows), use_container_width=True, hide_index=True)

    st.markdown("<div class='section-head'>NFA Graph - Step by Step</div>", unsafe_allow_html=True)

    all_nfa_edges = []
    for (s, sym), ns_list in nfa.items():
        for ns in ns_list:
            all_nfa_edges.append((s, ns, sym))

    edges_by_src = defaultdict(list)
    for e in all_nfa_edges:
        edges_by_src[e[0]].append(e)

    revealed_states = set()
    revealed_edges = []

    nfa_graph_placeholder = st.empty()
    nfa_step_area = st.container()

    with st.spinner("Building NFA graph step by step..."):
        for state in states_list:
            revealed_states.add(state)

            nfa_ph = nfa_step_area.empty()
            nfa_ph.markdown(
                f"<div class='step-state'>NFA - adding state: {state}</div>",
                unsafe_allow_html=True
            )

            nfa_graph_placeholder.empty()
            with nfa_graph_placeholder:
                st.components.v1.html(
                    build_graph_html(list(revealed_states), revealed_edges,
                                     final_states_clean, initial_state,
                                     highlighted_state=state,
                                     title="NFA - adding state: " + state),
                    height=400)
            time.sleep(0.85)

            for edge in edges_by_src[state]:
                revealed_states.add(edge[1])
                revealed_edges.append(edge)

                edge_ph = nfa_step_area.empty()
                edge_ph.markdown(
                    f"<div class='step-trans'>{edge[0]} --{edge[2]}--> {edge[1]}</div>",
                    unsafe_allow_html=True
                )

                nfa_graph_placeholder.empty()
                with nfa_graph_placeholder:
                    st.components.v1.html(
                        build_graph_html(list(revealed_states), revealed_edges,
                                         final_states_clean, initial_state,
                                         highlighted_state=state,
                                         highlighted_edges=[edge],
                                         title="NFA - " + edge[0] + " --[" + edge[2] + "]--> " + edge[1]),
                        height=400)
                time.sleep(0.9)

    nfa_graph_placeholder.empty()
    with nfa_graph_placeholder:
        st.components.v1.html(
            build_graph_html(states_list, all_nfa_edges, final_states_clean,
                             initial_state, title="NFA - complete"),
            height=400)

    nfa_done_ph = nfa_step_area.empty()
    nfa_done_ph.markdown(
        "<div class='step-done'>NFA graph complete.</div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='sep'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-head'>DFA Subset Construction - Step by Step</div>",
                unsafe_allow_html=True)

    if has_epsilon:
        initial_closure = compute_epsilon_closure(nfa, frozenset([initial_state]))
        closure_members = ", ".join(sorted(initial_closure))
        st.markdown(f"""
        <div class='step-epsilon' style='margin-bottom:14px;'>
          {EPSILON}-closure({initial_state}) = {{{closure_members}}} - this is the DFA start state.
        </div>
        """, unsafe_allow_html=True)

    order, dfa_transitions, dfa_final, has_dead, steps_log = run_subset_construction(
        nfa, alphabets_list, initial_state, final_states_clean
    )

    steps_area = st.container()
    dfa_graph_placeholder = st.empty()

    dfa_revealed_states = set()
    dfa_revealed_edges = []

    all_dfa_edges = []
    for (s_str, sym), nxt_str in dfa_transitions.items():
        all_dfa_edges.append((s_str, nxt_str, sym))

    dead_introduced = False

    with st.spinner("Running subset construction..."):
        for step in steps_log:
            state_str = step["state"]

            if state_str == "qd":
                header_ph = steps_area.empty()
                header_ph.markdown(
                    "<div class='step-state'>Processing dead state [qd] - all inputs loop back to [qd]</div>",
                    unsafe_allow_html=True
                )
            else:
                header_ph = steps_area.empty()
                if "," in state_str:
                    nfa_members = "{" + state_str + "}"
                else:
                    nfa_members = "{" + state_str + "}"

                epsilon_note = ""
                if has_epsilon and step.get("epsilon_closure"):
                    ec_members = ", ".join(step["epsilon_closure"])
                    epsilon_note = f" | {EPSILON}-closure: {{{ec_members}}}"

                header_ph.markdown(
                    f"<div class='step-state'>Processing DFA state: [{state_str}] - NFA states: {nfa_members}{epsilon_note}</div>",
                    unsafe_allow_html=True
                )

            dfa_revealed_states.add(state_str)

            dfa_graph_placeholder.empty()
            with dfa_graph_placeholder:
                st.components.v1.html(
                    build_graph_html(list(dfa_revealed_states), dfa_revealed_edges,
                                     dfa_final, initial_state,
                                     highlighted_state=state_str,
                                     title="DFA - processing: [" + state_str + "]"),
                    height=400)
            time.sleep(0.5)

            for t in step["transitions"]:
                sym = t["sym"]
                nxt = t["nxt"]
                is_new = t["is_new"]
                is_dead = t["is_dead"]
                is_first_dead = t["is_first_dead"]
                from_dead = t["from_dead"]

                if from_dead:
                    msg = f"On '{sym}': [qd] --> [qd]"
                    css_class = "step-dead"
                elif is_first_dead and not dead_introduced:
                    dead_introduced = True
                    msg = f"On '{sym}': [{state_str}] --> [qd] (no NFA transitions - dead state introduced)"
                    css_class = "step-dead-intro"
                elif is_dead:
                    msg = f"On '{sym}': [{state_str}] --> [qd]"
                    css_class = "step-dead"
                elif is_new:
                    after_closure = t.get("reachable_after_closure", [])
                    closure_note = ""
                    if has_epsilon and after_closure:
                        closure_note = f" | {EPSILON}-closure: {{{', '.join(after_closure)}}}"
                    msg = f"On '{sym}': [{state_str}] --> [{nxt}] (new state discovered){closure_note}"
                    css_class = "step-new"
                else:
                    msg = f"On '{sym}': [{state_str}] --> [{nxt}] (already known)"
                    css_class = "step-already"

                trans_ph = steps_area.empty()
                trans_ph.markdown(
                    "<div class='" + css_class + "'>" + msg + "</div>",
                    unsafe_allow_html=True
                )

                current_edge = (state_str, nxt, sym)
                if current_edge not in dfa_revealed_edges:
                    dfa_revealed_states.add(nxt)
                    dfa_revealed_edges.append(current_edge)

                dfa_graph_placeholder.empty()
                with dfa_graph_placeholder:
                    st.components.v1.html(
                        build_graph_html(list(dfa_revealed_states), dfa_revealed_edges,
                                         dfa_final, initial_state,
                                         highlighted_state=state_str,
                                         highlighted_edges=[current_edge],
                                         title="DFA - [" + state_str + "] --[" + sym + "]--> [" + nxt + "]"),
                        height=400)
                time.sleep(0.5)

    done_ph = steps_area.empty()
    done_ph.markdown(
        "<div class='step-done'>Subset construction complete. All DFA states processed.</div>",
        unsafe_allow_html=True
    )

    dfa_graph_placeholder.empty()
    with dfa_graph_placeholder:
        st.components.v1.html(
            build_graph_html(list(dfa_revealed_states), all_dfa_edges,
                             dfa_final, initial_state, title="DFA - complete"),
            height=400)

    st.markdown("<div class='sep'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-head'>DFA Transition Table</div>", unsafe_allow_html=True)

    dfa_rows_out = []
    for s_str in order:
        label = s_str
        if s_str == frozenset_to_str(compute_epsilon_closure(nfa, frozenset([initial_state]))):
            label = "-> " + label
        if s_str in dfa_final:
            label = label + " *"
        row = {"State": label}
        for sym in alphabets_list:
            row[sym] = dfa_transitions.get((s_str, sym), "qd")
        dfa_rows_out.append(row)

    st.dataframe(pd.DataFrame(dfa_rows_out), use_container_width=True, hide_index=True)

    dfa_start_state = frozenset_to_str(compute_epsilon_closure(nfa, frozenset([initial_state])))

    final_badges = " ".join(
        f"<span class='badge badge-final'>{s}</span>" for s in dfa_final
    ) or "<i>None</i>"
    all_dfa_state_badges = " ".join(
        f"<span class='badge badge-state'>{s}</span>" for s in order
    )

    st.markdown(f"""
    <div class='card-pink'>
      <b>Start State:</b> <span class='badge badge-start'>{dfa_start_state}</span>
      &nbsp;&nbsp;
      <b>Final States:</b> {final_badges}<br><br>
      <b>All DFA States:</b> {all_dfa_state_badges}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sep'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-head'>NFA - Individual Step Diagrams</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='card-lavender' style='margin-bottom:18px;'>
      <span style='font-size:14px; color:#4a148c;'>
        Each diagram below shows exactly one NFA transition - the source state appears first,
        then the transition edge is drawn, followed by the destination state.
        Only the states involved in that specific step are shown.
      </span>
    </div>
    """, unsafe_allow_html=True)

    nfa_step_counter = 1
    for src_state in states_list:
        for edge in edges_by_src[src_state]:
            src, dst, sym = edge
            step_states = list({src, dst})
            step_edges = [(src, dst, sym)]
            step_label = (
                f"Step {nfa_step_counter}: From {src} on input '{sym}' --> {dst}"
            )

            st.markdown(
                f"<div class='step-diagram-label'>{step_label}</div>",
                unsafe_allow_html=True
            )
            st.markdown("<div class='step-diagram-card'>", unsafe_allow_html=True)

            col_src, col_arrow, col_dst = st.columns([1, 1, 1])
            with col_src:
                st.components.v1.html(
                    build_step_graph_html([src], [], final_states_clean, initial_state, height=220),
                    height=230
                )
                st.markdown(
                    f"<div style='text-align:center; font-size:13px; font-weight:700; color:#6a1b9a;'>Source: {src}</div>",
                    unsafe_allow_html=True
                )

            with col_arrow:
                st.components.v1.html(
                    build_step_graph_html(step_states, step_edges, final_states_clean, initial_state, height=220),
                    height=230
                )
                st.markdown(
                    f"<div style='text-align:center; font-size:13px; font-weight:700; color:#6a1b9a;'>Transition: {src} --{sym}--> {dst}</div>",
                    unsafe_allow_html=True
                )

            with col_dst:
                st.components.v1.html(
                    build_step_graph_html([dst], [], final_states_clean, initial_state, height=220),
                    height=230
                )
                st.markdown(
                    f"<div style='text-align:center; font-size:13px; font-weight:700; color:#6a1b9a;'>Destination: {dst}</div>",
                    unsafe_allow_html=True
                )

            st.markdown("</div>", unsafe_allow_html=True)
            nfa_step_counter += 1

    st.markdown("<div class='sep'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-head'>DFA - Individual Step Diagrams</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='card-lavender' style='margin-bottom:18px;'>
      <span style='font-size:14px; color:#4a148c;'>
        Each diagram below shows exactly one DFA transition produced by subset construction.
        The source DFA state appears first, then the transition is drawn, then the destination DFA state appears.
        Only the two states and the single transition involved are shown per step.
      </span>
    </div>
    """, unsafe_allow_html=True)

    dfa_step_counter = 1
    for step in steps_log:
        state_str = step["state"]
        for t in step["transitions"]:
            sym = t["sym"]
            nxt = t["nxt"]
            is_new = t["is_new"]
            is_dead = t["is_dead"]
            from_dead = t["from_dead"]

            if is_new:
                discovery_note = " (new DFA state discovered)"
            elif from_dead:
                discovery_note = " (dead state self-loop)"
            elif is_dead:
                discovery_note = " (goes to dead state)"
            else:
                discovery_note = ""

            step_states = list({state_str, nxt})
            step_edges = [(state_str, nxt, sym)]

            step_label = (
                f"Step {dfa_step_counter}: DFA state [{state_str}] on input '{sym}' --> [{nxt}]{discovery_note}"
            )

            st.markdown(
                f"<div class='step-diagram-label'>{step_label}</div>",
                unsafe_allow_html=True
            )
            st.markdown("<div class='step-diagram-card'>", unsafe_allow_html=True)

            col_src, col_arrow, col_dst = st.columns([1, 1, 1])
            with col_src:
                st.components.v1.html(
                    build_step_graph_html([state_str], [], dfa_final, initial_state, height=220),
                    height=230
                )
                st.markdown(
                    f"<div style='text-align:center; font-size:13px; font-weight:700; color:#6a1b9a;'>Source: [{state_str}]</div>",
                    unsafe_allow_html=True
                )

            with col_arrow:
                st.components.v1.html(
                    build_step_graph_html(step_states, step_edges, dfa_final, initial_state, height=220),
                    height=230
                )
                st.markdown(
                    f"<div style='text-align:center; font-size:13px; font-weight:700; color:#6a1b9a;'>On '{sym}': [{state_str}] --> [{nxt}]</div>",
                    unsafe_allow_html=True
                )

            with col_dst:
                st.components.v1.html(
                    build_step_graph_html([nxt], [], dfa_final, initial_state, height=220),
                    height=230
                )
                st.markdown(
                    f"<div style='text-align:center; font-size:13px; font-weight:700; color:#6a1b9a;'>Destination: [{nxt}]</div>",
                    unsafe_allow_html=True
                )

            st.markdown("</div>", unsafe_allow_html=True)
            dfa_step_counter += 1


render_ui()
