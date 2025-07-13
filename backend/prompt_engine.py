import os, json
from openai import AsyncOpenAI
from dotenv import load_dotenv
from models import ScoreResponse, ImprovementIteration
from datetime import datetime

load_dotenv()

class PromptEngine:
    def __init__(self, 
                 api_key: str = None,
                 model: str = "gpt-4o-mini",
                 default_criteria: list = None,
                 max_iterations: int = 3):
        """
        Initialize the PromptEngine with configuration
        
        Args:
            api_key: OpenAI API key (defaults to env var)
            model: OpenAI model to use
            default_criteria: Default scoring criteria
            max_iterations: Maximum improvement iterations
        """
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.max_iterations = max_iterations
        self.default_criteria = default_criteria or ["relevance", "coherence", "simplicity", "depth"]
    
    async def score_prompt(self, prompt: str) -> dict:
        """Score a prompt based on the configured criteria"""
        instructions = f"""
        Evaluate the following prompt based on the criteria {', '.join(self.default_criteria)}.
        Provide a score for each factor on a scale from 1 to 10 and calculate a final average.

        Prompt: "{prompt}"
        """

        # Define function schema for LLM output
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "score_prompt",
                    "description": "Score a prompt on several criteria",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            criterion: {"type": "integer", "minimum": 1, "maximum": 10}
                            for criterion in self.default_criteria
                        } | {"average": {"type": "number"}},
                        "required": self.default_criteria + ["average"]
                    }
                }
            }
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
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
            return {criterion: 5 for criterion in self.default_criteria} | {"average": 5.0}

    async def generate_response(self, prompt: str, criteria: list) -> str:
        """Generate an improved version of the prompt"""
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
            response = await self.client.chat.completions.create(
                model=self.model,
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
            return prompt

    async def find_improvement(self, d1: dict, d2: dict) -> list:
        """Find criteria that need improvement (where new scores are lower than old scores)"""
        res = []
        for criterion in d1:
            if criterion == "average":
                continue
            old_score, new_score = d1[criterion], d2[criterion]
            if old_score > new_score:
                res.append(criterion)
        return res  

    async def improve_prompt(self, request, progress_callback=None):
        """Main method to improve a prompt through iterative refinement"""
        try:
            improvement_history = []
            initial_scores = await self.score_prompt(request.prompt)
            
            improved_prompt = await self.generate_response(request.prompt, request.criteria)
            scores = await self.score_prompt(improved_prompt) 
            to_improve = await self.find_improvement(initial_scores, scores)

            total_iters = 0
            consecutive_improvements = 0

            while consecutive_improvements < request.min_consecutive_improvements and total_iters < request.max_iterations:
                criteria_to_focus = to_improve if to_improve else request.criteria
                improved_prompt = await self.generate_response(improved_prompt, criteria_to_focus)
                current_scores = await self.score_prompt(improved_prompt)  
                to_improve = await self.find_improvement(scores, current_scores)

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

def create_prompt_engine(**kwargs) -> PromptEngine:
    """Create a PromptEngine instance with default settings"""
    return PromptEngine(**kwargs)

default_engine = PromptEngine()

async def improve_prompt(request, progress_callback=None):
    """Backward-compatible wrapper for the main improve_prompt function"""
    return await default_engine.improve_prompt(request, progress_callback)