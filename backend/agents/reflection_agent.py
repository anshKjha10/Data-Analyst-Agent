import json
import os
import re
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from backend.prompts.reflection_prompt import REFLECTION_PROMPT
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="GPT-4",
    base_url="https://models.inference.ai.azure.com",
    temperature=0
)

class ReflectionAgent:
    def __init__(self):
        self.prompt = ChatPromptTemplate.from_template(REFLECTION_PROMPT)
        self.parser = JsonOutputParser()

        self.chain = (
            self.prompt | llm | self.parser
        )

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
            "reflection_summary": "Failed to parse reflection JSON.",
            "new_tasks": []
        }

    def run(self, state: dict) -> dict:
        payload = {
            "analysis_plan": json.dumps(state.get("analysis_plan", {}), indent=2, default=str),
            "review": json.dumps(state.get("review", {}), indent=2, default=str)
        }

        try:
            result = self.chain.invoke(payload)
        except Exception as e:
            try:
                formatted_prompt = self.prompt.format_prompt(**payload)
                response = llm.invoke(formatted_prompt.to_messages())
                raw_text = response.content if hasattr(response, 'content') else str(response)
                result = self._parse_json_fallback(raw_text)
            except Exception as inner_e:
                result = {
                    "reflection_summary": f"Reflection execution error: {str(inner_e)}",
                    "new_tasks": []
                }

        if not isinstance(result, dict):
            result = {
                "reflection_summary": "Invalid reflection result structure from LLM.",
                "new_tasks": []
            }
        
        if "new_tasks" not in result:
            result["new_tasks"] = []
            
        return result
