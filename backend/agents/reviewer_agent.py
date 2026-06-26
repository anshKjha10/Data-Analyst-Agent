import json
import os
import re
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from backend.prompts.reviewer_prompt import REVIEWER_PROMPT

load_dotenv()

llm = ChatOpenAI(
    model_name="GPT-4",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://models.inference.ai.azure.com"
)

class ReviewerAgent:
    def __init__(self):
        self.prompt = ChatPromptTemplate.from_template(REVIEWER_PROMPT)
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
            "scores": {
                "completeness": 0,
                "statistical_correctness": 0,
                "business_relevance": 0,
                "quality_of_visualizations": 0,
                "actionability_of_recommendations": 0
            },
            "passed": False,
            "strengths": [],
            "missing_analysis": [],
            "missing_visualizations": [],
            "feedback": ["Failed to parse review content cleanly.", text[:500]],
            "next_actions": []
        }
    
    def run(self, state):
        payload = {
            "dataset_info": json.dumps(state.get("dataset_info", {}), indent=2, default=str),
            "analysis_plan": json.dumps(state.get("analysis_plan", {}), indent=2, default=str),
            "eda_results": json.dumps(state.get("eda_results", {}), indent=2, default=str),
            "visualizations": json.dumps(state.get("visualizations", []), indent=2, default=str),
            "insights": json.dumps(state.get("insights", {}), indent=2, default=str)
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
                    "scores": {
                        "completeness": 0,
                        "statistical_correctness": 0,
                        "business_relevance": 0,
                        "quality_of_visualizations": 0,
                        "actionability_of_recommendations": 0
                    },
                    "passed": False,
                    "strengths": [],
                    "missing_analysis": [],
                    "missing_visualizations": [],
                    "feedback": [f"Reviewer execution error: {str(inner_e)}"],
                    "next_actions": []
                }

        scores = result.get("scores", {})
        if isinstance(scores, dict) and scores:
            try:
                score = sum(float(v) for v in scores.values()) / len(scores)
            except Exception:
                score = 0.0
        else:
            score = float(result.get("score", 0))

        passed = result.get("passed", False)
        
        return {
            "review": result,
            "review_score": score,
            "review_passed": passed
        }