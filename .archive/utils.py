
def build_structured_prompt(role, task, constraints, output, personality):
    return f"""
[1. ROLE or CONTEXTUAL SETTING]: Imagine you are a {role}.

[2. OBJECTIVE or TASK]: I want you to help me {task}.

[3. CONSTRAINTS & RESOURCES]: Here’s what I already have / can't do / must consider:
{constraints}

[4. PREFERRED OUTPUT STYLE]: I want the response to be in {output}.

[5. BONUS – PERSONAL TOUCH]: Think like {personality}.
""".strip()

def build_natural_prompt(role, task, constraints, output, personality):
    return f"""
Imagine you are {role}.
I want you to help me {task}.
Constraints: {constraints}
Output: {output}
Act like {personality}.
""".strip()
