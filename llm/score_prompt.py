# Defines async function to score a user prompt based on multiple criteria using OpenAI function calling and 
# performs data validation with Pydantic

import os, json
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field, computed_field

class Score(BaseModel):
    relevance: int = Field(..., ge=1, le=10, description="Relevance of prompt")
    coherence: int = Field(..., ge=1, le=10, description="Coherence of prompt")
    simplicity: int = Field(..., ge=1, le=10, description="Simplicity of prompt")
    depth: int = Field(..., ge=1, le=10, description="Depth of prompt")
    explanation: str = Field(..., min_length=5)

    @computed_field
    @property
    def average(self) -> float:
        return (self.relevance + self.coherence + self.simplicity + self.depth) / 4,

    
load_dotenv()

CRITERIA = ["relevance", "coherence", "simplicity", "depth"]        # Criteria for scoring prompt

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def call_llm(prompt, retry_instructions=""):
    instructions = f"""
    Evaluate the following prompt based on the criteria {', '.join(CRITERIA)}.
    Provide a score for each factor on a scale from 1 to 10 and give a brief explanation for your scoring. {retry_instructions}
    Prompt: "{prompt}"
    """

    # Define function schema for LLM output
    functions = [
    {
        "name": "score_prompt",
        "description": "Score a prompt on several criteria",
        "parameters": {
            "type": "object",
            "properties": {
                "relevance": {"type": "integer", "minimum": 1, "maximum": 10},
                "coherence": {"type": "integer", "minimum": 1, "maximum": 10},
                "simplicity": {"type": "integer", "minimum": 1, "maximum": 10},
                "depth":     {"type": "integer", "minimum": 1, "maximum": 10},
                "explanation": {"type": "string", "description": "A brief explanation justifying the assigned scores"}
            },
            "required": ["relevance", "coherence", "simplicity", "depth", "explanation"]
        }
    }
]

    response = await client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {"role" : "system", "content" : "You are an AI evaluator tasked with scoring prompts based on certain criteria"},
            {"role" : "user", "content" : instructions}, 
        ],
        functions=functions,
        function_call={"name" : "score_prompt"},
        max_tokens=300
    )

    output = json.loads(response.choices[0].message.function_call.arguments)
    return output

def score_prompt(prompt, retry_instructions="", retries=2):
    llm_response = call_llm(prompt)

    # Attempt to parse LLM response
    try:
        score_model = Score(**llm_response)
        return score_model.model_dump_json()
    except Exception as exc:
        if retries == 0:
            return
        instr = "Do not include any extra commentary or formatting — only return a raw JSON object that matches the structure exactly."
        score_prompt(prompt=prompt, retry_instructions=instr, retries=retries-1)

