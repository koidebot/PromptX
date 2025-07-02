import os, json
from openai import AsyncOpenAI
from dotenv import load_dotenv
from models import ScoreResponse, ImprovementIteration
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

    tools = [
        {
            "type": "function",
            "function": {
                "name": "score_prompt",
                "description": "Score a prompt on several criteria",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relevance": {"type": "integer", "minimum": 1, "maximum": 10},
                        "coherence": {"type": "integer", "minimum": 1, "maximum": 10},
                        "simplicity": {"type": "integer", "minimum": 1, "maximum": 10},
                        "depth": {"type": "integer", "minimum": 1, "maximum": 10},
                        "average": {"type": "number"}
                    },
                    "required": ["relevance", "coherence", "simplicity", "depth", "average"]
                }
            }
        }
    ]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI evaluator tasked with scoring prompts based on certain criteria, that returns scores in JSON format"},
                {"role": "user", "content": instructions}, 
            ],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "score_prompt"}},
            max_tokens=300
        )

        tool_call = response.choices[0].message.tool_calls[0]
        args = tool_call.function.arguments
        return json.loads(args)
    except Exception as e:
        # Return default scores if API call fails
        return {
            "relevance": 5,
            "coherence": 5,
            "simplicity": 5,
            "depth": 5,
            "average": 5.0
        }

async def generate_response(prompt, criteria):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "refine_prompt",
                "description": "Return a cleaned-up prompt plus stats",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "refined_prompt": {"type": "string"},
                        "token_count": {"type": "integer"},
                        "keywords_added": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                    },
                    "required": ["refined_prompt"]
                }
            }
        }
    ]

    criteria_text = ", ".join(criteria)
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI that helps improve the specificity and clarity of prompts."},
                {"role": "user", "content": f"Please refine this prompt: {prompt}, focusing on improving these elements: {criteria_text}"}
            ],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "refine_prompt"}}, 
            max_tokens=300
        )

        tool_call = response.choices[0].message.tool_calls[0]
        args_json = tool_call.function.arguments
        data = json.loads(args_json)

        return data["refined_prompt"]
    except Exception as e:
        # Return original prompt if API call fails
        return prompt

async def find_improvement(d1, d2):
    """Find criteria that need improvement (where new scores are lower than old scores)"""
    res = []
    for criterion in d1:
        if criterion == "average":
            continue
        old_score, new_score = d1[criterion], d2[criterion]
        if old_score > new_score:
            res.append(criterion)
    return res  # Fixed: Added missing return statement

async def improve_prompt(request, progress_callback=None):
    try:
        improvement_history = []

        # Get initial scores
        initial_scores = await score_prompt(request.prompt)
        
        # Generate first improvement
        improved_prompt = await generate_response(request.prompt, request.criteria)
        scores = await score_prompt(improved_prompt) 
        to_improve = await find_improvement(initial_scores, scores)

        total_iters = 0
        consecutive_improvements = 0

        while consecutive_improvements < request.min_consecutive_improvements and total_iters < request.max_iterations:
            # Generate improvement focusing on areas that need work
            criteria_to_focus = to_improve if to_improve else request.criteria
            improved_prompt = await generate_response(improved_prompt, criteria_to_focus)
            current_scores = await score_prompt(improved_prompt)  
            to_improve = await find_improvement(scores, current_scores)

            iteration = ImprovementIteration(
                iteration=total_iters + 1,
                prompt=improved_prompt,
                scores=ScoreResponse(**current_scores),
                improvements_needed=to_improve,
                timestamp=datetime.now()
            )
            improvement_history.append(iteration)

            # Update progress if callback provided
            if progress_callback:
                await progress_callback({
                    "iteration": total_iters + 1,
                    "prompt": improved_prompt,
                    "scores": current_scores,
                    "improvements_needed": to_improve,
                    "timestamp": datetime.now()
                })

            # Check if we made improvements (no areas need improvement)
            if len(to_improve) == 0:
                consecutive_improvements += 1
            else:
                consecutive_improvements = 0

            scores = current_scores
            total_iters += 1

        return {
            "status": "completed",
            "final_prompt": improved_prompt,
            "iterations": improvement_history,
            "error": None,
        }
    
    except Exception as e:
        return {
            "status": "failed",
            "final_prompt": None,
            "iterations": improvement_history if 'improvement_history' in locals() else [],
            "error": str(e),
        }