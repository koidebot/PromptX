import re
import os, json
from openai import AsyncOpenAI
from dotenv import load_dotenv
import asyncio
from models import PromptRequest, ScoreResponse, ImprovementIteration, JobStatus, JobResponse
from datetime import datetime

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

max_iterations = 3
default_criteria = ["relevance", "coherence", "simplicity", "depth"]

async def score_prompt(prompt):
    instructions = f"""
    Evaluate the following prompt based on the criteria {', '.join(default_criteria)}.
    Provide a score for each factor on a scale from 1 to 10 and calculate a final average.

    Prompt: "{prompt}"
    """

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
                "average":   {"type": "number"}
            },
            "required": ["relevance", "coherence", "simplicity", "depth", "average"]
        }
    }
]

    response = await client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {"role" : "system", "content" : "You are an AI evaluator tasked with scoring prompts based on certain criteria, that returns scores in JSON format"},
            {"role" : "user", "content" : instructions}, 
        ],
        functions=functions,
        function_call={"name" : "score_prompt"},
        max_tokens=300
    )

    args = response.choices[0].message.function_call.arguments
    return json.loads(args)

async def generate_response(prompt, criteria):
    functions = [
        {
            "name": "refine_prompt",
            "description": "Return a cleaned-up prompt plus stats",
            "parameters": {
                "type": "object",
                "properties": {
                    "refined_prompt": {"type": "string"},
                    "token_count":    {"type": "integer"},
                    "keywords_added": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                },
                "required": ["refined_prompt"]
            }
        }
    ]

    criteria_text = ", ".join(criteria)
    response = await client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {"role" : "system", "content" : "You are an AI that helps improve the specifity and clarity of prompts."},
            {"role" : "user", "content" : f"Please refine this prompt: {prompt}, focusing on improving these elements: {criteria_text}"}
        ],
        functions=functions,
        function_call={"name":"refine_prompt"}, 
        max_tokens=300
    )

    args_json = response.choices[0].message.function_call.arguments
    data = json.loads(args_json)

    return data["refined_prompt"]

async def find_improvement(d1, d2):
    res = []
    for criterion in d1:
        if criterion == "average":
            continue
        old_score, new_score = d1[criterion], d2[criterion]
        if old_score > new_score:
            res.append(criterion)

async def improve_prompt(request):
    improvement_history = []

    initial_scores = await score_prompt(request.prompt)
    improved_prompt = await generate_response(request.prompt, request.criteria)
    scores = await score_prompt(improved_prompt)
    to_improve = await find_improvement(initial_scores, scores)

    total_iters = 0
    consecutive_improvements = 0

    while consecutive_improvements < request.min_consecutive_improvements or total_iters < request.max_iterations:
        improved_prompt = await generate_response(improved_prompt, to_improve if to_improve else request.criteria)
        current_scores = await score_prompt(improved_prompt, request.criteria)
        to_improve = await find_improvement(scores, current_scores)

        iteration = ImprovementIteration(
            iteration=total_iters + 1,
            prompt=improved_prompt,
            scores=ScoreResponse(**current_scores),
            improvements_needed=to_improve,
            timestamp=datetime.now()
        )
        improvement_history.append(iteration)

        if len(to_improve) == 0:
            consecutive_improvements += 1
        else:
            consecutive_improvements = 0

        scores = current_scores
        total_iters += 1

        if total_iters >= request.max_iterations:
            break

    return {
        "status": "completed",
        "final_prompt": improved_prompt,
        "iterations": improvement_history,
        "error": None,
    }