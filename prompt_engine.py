import re
import os, json
from openai import AsyncOpenAI
from dotenv import load_dotenv
import asyncio

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

max_iterations = 3
criteria = ["relevance", "coherence", "simplicity", "depth"]

async def score_prompt(prompt):
    instructions = f"""
    Evaluate the following prompt based on the criteria {', '.join(criteria)}.
    Provide a score for each factor on a scale from 1 to 10 and calculate a final average.

    Prompt: "{prompt}"
    """

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

async def parse_scores(text):
    scores = {}
    for criterion in criteria:
        match = re.search(fr"{criterion.capitalize()}: (\d+)", text)
        if match:
            scores[criterion] = int(match.group(1))
    
    if scores:
        scores["average"] = sum(scores.values()) / len(scores)
    else:
        scores["average"] = None  
    
    return scores
    

async def generate_response(prompt, criteria):
    criteria_text = f"{', '.join(criteria)}"
    response = await client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {"role" : "system", "content" : "You are an AI that elps improve the specifity and clarity of prompts."},
            {"role" : "user", "content" : f"Please refine this prompt: {prompt}, focusing on improving these elements: {criteria_text}"}
        ]
    )
    return response.choices[0].message.content

async def find_improvement(d1, d2):
    res = []
    for criterion in d1:
        if criterion == "average":
            return res
        old_score, new_score = d1[criterion], d2[criterion]
        if old_score > new_score:
            res.append(criterion)
            

async def main():
    initial_prompt = input("Give me a prompt to improve: ")
    initial_scores = await score_prompt(initial_prompt)
    print(f"Initial Scores: {initial_scores}")
    
    prompt = await generate_response(initial_prompt, criteria)
    scores = await score_prompt(prompt)
    to_improve = await find_improvement(initial_scores, scores)
    print(f"Initial Improvement Needed: {to_improve}")

    total_iters = 0
    cur_iters = 0
    while cur_iters < 2 or total_iters < max_iterations:
        prompt = await generate_response(prompt, to_improve)
        print(f"Iteration {total_iters + 1}: {prompt}")
        cur_scores = await score_prompt(prompt)
        print(f"Scores: {cur_scores}")
        to_improve = await find_improvement(scores, cur_scores)
        
        if len(to_improve) == 0:
            cur_iters += 1
        
        total_iters += 1
    
    print(f"Final Prompt: {prompt}")

if __name__ == '__main__':
    asyncio.run(main())