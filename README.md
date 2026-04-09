# **NFA to DFA Converter Using Subset Construction Method**
## **About**
This tool converts a given NFA into a DFA using the Subset Construction Method.
Instead of directly showing only the final DFA, it presents the entire conversion process step by step so that the construction becomes easy to understand.

- NFA Transition Table and NFA Diagram
- Subset Construction Steps
- DFA Transition Table, DFA Final States, and DFA Diagram

## **Built With**
- Python
- Streamlit
- Pandas
- Vis.js

## **What it does**
After clicking Convert, the application displays:

- NFA Transition Table
- NFA Graph (built step by step)
- Subset Construction Process (step by step)
- DFA Transition Table
- DFA Final States
- DFA Graph (built step by step)
- Individual diagrams for each transition in both NFA and DFA

## **Input Format**
- Transitions: Enter one transition per line in the format: state,symbol->nextstate or state,symbol=nextstate1,nextstate2

## **Input Details**

States: Detected automatically
Alphabets: Detected automatically (you can add extra if needed)
Initial State: Taken from the first transition
Final States: Selected manually

## **Features**
- Automatic detection of states and alphabets
- Input validation with proper error messages
- Displays NFA Transition Table and Diagram
- Step-by-step NFA graph construction
- Step-by-step DFA construction using subset construction method
- Displays Subset Construction Steps
- Displays DFA Transition Table, States and Final States
- Separate diagrams for every transition
- Handles NFA with epsilon moves
- Clean and structured UI
- Shows the process step by step instead of displaying everything at once.
