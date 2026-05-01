# Like Math But Not Math

A desktop application designed to convert and analyze formal languages, including Regular Expressions, Deterministic Finite Automata (DFA), Non-deterministic Finite Automata (NFA), Context-Free Grammars (CFG), and sets of strings.

## Installation & Requirements

To easily install the project dependencies, a `requirements.txt` file has been provided. 

1. It is recommended to use a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

After installing the requirements, you can start the application by running:

```bash
python main.py
```

## How to Input Correctly

The application supports various input types. To ensure the application correctly parses your input, please follow the formats below:

### 1. Regular Expressions (regex)
Enter your regular expression as a continuous string. 
- You can use standard operators like `*` (Kleene star), `|` (Union), etc.
- Use `ε`, `epsilon`, or `eps` to represent an empty string.
- Example: `(a|b)*abb`

### 2. DFA Text
Define your DFA with explicit fields (`states`, `alphabet`, `start`, `accept`, and `transitions`). Each transition should map a `state,symbol` to a new `state`.
**Example:**
```text
states: q0,q1,q2
alphabet: a,b
start: q0
accept: q2
transitions:
  q0,a -> q1
  q0,b -> q0
  q1,a -> q1
  q1,b -> q2
  q2,a -> q1
  q2,b -> q0
```

### 3. Context-Free Grammar (CFG)
Write production rules using `->`. 
- Separate alternative right-hand sides with `|`.
- Terminals and Variables should be separated by spaces in some contexts or properly grouped.
- The first rule defined will be assumed as the start variable.
- You can use `ε`, `epsilon`, `''`, or `""` for empty string productions.
**Example:**
```text
S -> a S | b A | b
A -> a A | a
```

### 4. Sets of Strings
Provide a list of strings, with each string on a new line. The converter will automatically build a DFA that accepts exactly this finite set of strings.
**Example:**
```text
a
ab
abb
```

### 5. NFA JSON
If you are inputting an NFA, provide a valid JSON object with the properties expected by the system (usually matching `states`, `alphabet`, `transitions`, `start_state`, `accept_states`).