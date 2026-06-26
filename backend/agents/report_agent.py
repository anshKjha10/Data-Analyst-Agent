import json
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.prompts.report_prompt import REPORT_PROMPT
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name=os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile"),
    temperature=0
)

class ReportAgent:
    def __init__(self):
        self.prompt = ChatPromptTemplate.from_template(REPORT_PROMPT)
        self.parser = StrOutputParser()

        self.chain = (
            self.prompt | llm | self.parser
        )

    def run(self, state: dict) -> dict:
        payload = {
            "dataset_info": json.dumps(state.get("dataset_info", {}), indent=2, default=str),
            "eda_results": json.dumps(state.get("eda_results", {}), indent=2, default=str),
            "visualizations": json.dumps(state.get("visualizations", []), indent=2, default=str),
            "insights": json.dumps(state.get("insights", {}), indent=2, default=str)
        }

        try:
            report_text = self.chain.invoke(payload)
        except Exception as e:
            try:
                formatted_prompt = self.prompt.format_prompt(**payload)
                response = llm.invoke(formatted_prompt.to_messages())
                report_text = response.content if hasattr(response, 'content') else str(response)
            except Exception as inner_e:
                report_text = f"# Business Report\n\nExecution error occurred: {str(inner_e)}"

        return {
            "report": report_text
        }