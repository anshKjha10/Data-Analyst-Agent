import json
import os
import re
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from backend.prompts.insight_prompt import INSIGHT_PROMPT

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name=os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile"),
    temperature=0
)

class InsightAgent:
    def __init__(self):
        self.prompt = ChatPromptTemplate.from_template(INSIGHT_PROMPT)
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
            "executive_summary": "Failed to parse generated insights cleanly. Below is the raw output.",
            "key_findings": [text[:500]],
            "trends": [],
            "anomalies": [],
            "business_risks": [],
            "recommendations": []
        }

    def run(self, state):
        dataset_info = state["dataset_info"]
        eda_results = state["eda_results"]
        visualizations = state["visualizations"]

        try:
            insights = self.chain.invoke(
                {
                    "dataset_info": json.dumps(dataset_info, indent=2, default=str),
                    "eda_results": json.dumps(eda_results, indent=2, default=str),
                    "visualizations": json.dumps(visualizations, indent=2, default=str)
                }
            )
        except Exception as e:
            try:
                formatted_prompt = self.prompt.format_prompt(
                    dataset_info=json.dumps(dataset_info, indent=2, default=str),
                    eda_results=json.dumps(eda_results, indent=2, default=str),
                    visualizations=json.dumps(visualizations, indent=2, default=str)
                )
                response = llm.invoke(formatted_prompt.to_messages())
                raw_text = response.content if hasattr(response, 'content') else str(response)
                insights = self._parse_json_fallback(raw_text)
            except Exception as inner_e:
                insights = {
                    "executive_summary": f"Failed to execute LLM analysis: {str(inner_e)}",
                    "key_findings": [],
                    "trends": [],
                    "anomalies": [],
                    "business_risks": [],
                    "recommendations": []
                }

        return {
            "insights": insights
        }