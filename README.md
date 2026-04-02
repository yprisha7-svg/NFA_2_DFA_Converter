#**NFA to DFA Converter Using Subset Construction Method**
##**About**
This tool converts a given NFA into a DFA using the Subset Construction Method.
The user enters the NFA details: states, alphabets, initial state, final state(s), and transitions in the format mentioned on the sidebar.
On clicking the Convert "NFA to DFA" button, the following are displayed:

- NFA Transition Table and NFA Diagram
- Subset Construction Steps
- DFA Transition Table, DFA Final States, and DFA Diagram

##**Technologies Used**
- Python
- Streamlit
- Pandas
- Graphviz

## Input Format
- **States:** comma separated (ex: q0, q1, q2)
- **Alphabets:** comma separated (ex: a, b)
- **Initial State:** single state (ex: q0)
- **Final States:** comma separated (ex: q1, q2)
- **Transitions:** state,symbol=nextstate1,nextstate2 separated by semicolons (ex: q0,a=q0,q1;q0,b=q1)

## Features
- Displays NFA Transition Table and Diagram
- Displays Subset Construction Steps
- Displays DFA Transition Table and Diagram
- Highlights DFA Final States with double circles in the diagram
- Input validation using error messages
