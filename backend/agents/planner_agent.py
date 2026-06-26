import json
import os
import re
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from backend.prompts.planner_prompt import PLANNER_PROMPT

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name=os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile"),
    temperature=0
)

class PlannerAgent:

    def __init__(self):
        self.prompt = ChatPromptTemplate.from_template(PLANNER_PROMPT)
        self.parser = JsonOutputParser()

        self.chain = (self.prompt | llm | self.parser)

    def _parse_json_fallback(self, text: str) -> dict:
        """
        Robust fallback JSON parsing method using regex and cleaning.
        """
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        try:
            match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
            if match:
                return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

        try:
            match = re.search(r'(\{.*\})', text, re.DOTALL)
            if match:
                return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

        return {
            "dataset_type": "Tabular",
            "priority": "medium",
            "summary_of_approach": f"Fallback plan generated due to JSON parsing error: {text[:100]}...",
            "tasks": [
                {
                    "step": 1,
                    "agent": "eda_agent",
                    "action": "summary_statistics",
                    "args": {},
                    "reason": "Examine summary statistics of the dataset as a fallback step."
                }
            ]
        }

    def run(self, state):
        dataset_info = state["dataset_info"]
        try:
            analysis_plan = self.chain.invoke(
                {
                    "dataset_info" : json.dumps(
                        dataset_info,
                        indent=2
                    )
                }
            )
        except Exception as e:
            try:
                formatted_prompt = self.prompt.format_prompt(
                    dataset_info=json.dumps(dataset_info, indent=2)
                )
                response = llm.invoke(formatted_prompt.to_messages())
                raw_text = response.content if hasattr(response, 'content') else str(response)
                analysis_plan = self._parse_json_fallback(raw_text)
            except Exception as inner_e:
                analysis_plan = {
                    "dataset_type": "Tabular",
                    "priority": "medium",
                    "summary_of_approach": f"Fallback plan due to execution error: {str(inner_e)}",
                    "tasks": []
                }

        return {
            "analysis_plan" : analysis_plan
        }