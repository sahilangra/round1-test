
from langchain_core.prompts import ChatPromptTemplate
from prompts.prompts import LEADERSHIP_RAG_PROMPT

try:
    prompt_template = ChatPromptTemplate.from_template(LEADERSHIP_RAG_PROMPT)
    prompt = prompt_template.format(
        history="No previous conversation.",
        context="Some context",
        question="What is the revenue?",
    )
    print("Successfully formatted prompt.")
except Exception as e:
    print(f"Error during formatting: {e}")
    print(f"Error type: {type(e)}")
