import json
import requests
import time
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import datetime
import base64
from dotenv import load_dotenv
import os
from .models import Interaction
from django.shortcuts import render

load_dotenv()

class AgentCore:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def _call_gemini(self, prompt_parts, generation_config=None, max_retries=3):
        headers = {
            'Content-Type': 'application/json',
        }
        params = {'key': self.api_key}

        payload = {
            "contents": [{"role": "user", "parts": prompt_parts}]
        }
        if generation_config:
            payload["generationConfig"] = generation_config

        for attempt in range(max_retries):
            try:
                response = requests.post(self.base_url, headers=headers, params=params, json=payload)
                response.raise_for_status()
                result = response.json()

                if result.get('candidates') and result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts'):
                    text_content = result['candidates'][0]['content']['parts'][0]['text']
                    if generation_config and generation_config.get('responseMimeType') == 'application/json':
                        try:
                            return json.loads(text_content)
                        except json.JSONDecodeError:
                            return text_content
                    return text_content
                else:
                    return "No valid response from LLM."
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s...
                        print(f"Rate limited (429). Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "Error: You have hit the Gemini API rate limit. Please wait a minute before trying again."
                print(f"Error calling Gemini API: {e}")
                return f"Error communicating with AI: {e}"
            except requests.exceptions.RequestException as e:
                print(f"Error calling Gemini API: {e}")
                return f"Error communicating with AI: {e}"
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return f"An unexpected error occurred: {e}"

    def planning_module(self, prompt, file_content=None, file_data=None, file_type=None, action_type_from_frontend=None):
        prompt_lower = prompt.lower()

        if action_type_from_frontend == "code_generation":
            return {"action_type": "code_generation", "task_description": prompt, "file_content": file_content}
        elif action_type_from_frontend == "debugging":
            return {"action_type": "debugging", "task_description": prompt, "file_content": file_content}
        elif action_type_from_frontend == "git_operation":
            return {"action_type": "git_operation", "task_description": prompt, "file_content": file_content}
        elif action_type_from_frontend == "analyze_file":
            return {"action_type": "analyze_file", "task_description": prompt, "file_content": file_content, "file_type": file_type}
        elif action_type_from_frontend == "analyze_image":
            return {"action_type": "analyze_image", "task_description": prompt, "file_data": file_data, "file_type": file_type}
        elif action_type_from_frontend == "analyze_document":
            return {"action_type": "analyze_document", "task_description": prompt, "file_content": file_content, "file_type": file_type}
        elif action_type_from_frontend == "generate_ideas":
            return {"action_type": "generate_ideas", "task_description": prompt, "file_content": file_content}
        elif action_type_from_frontend == "general_ai":
            return {"action_type": "general_ai", "task_description": prompt, "file_content": file_content, "file_data": file_data, "file_type": file_type}
        
        # Fallback
        if file_data and file_type and file_type.startswith('image/'):
            return {"action_type": "analyze_image", "task_description": prompt, "file_data": file_data, "file_type": file_type}
        elif file_content and (file_type == 'application/pdf' or file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'):
            return {"action_type": "analyze_document", "task_description": prompt, "file_content": file_content, "file_type": file_type}
        elif file_content:
            return {"action_type": "analyze_file", "task_description": prompt, "file_content": file_content, "file_type": file_type}

        return {"action_type": "general_ai", "task_description": prompt}

    def tool_executor(self, action_plan):
        action_type = action_plan.get("action_type")
        task_description = action_plan.get("task_description")
        file_content = action_plan.get("file_content")
        file_data = action_plan.get("file_data")
        file_type = action_plan.get("file_type")

        if action_type == "code_generation":
            return self._generate_code_tool(task_description, file_content)
        elif action_type == "debugging":
            return self._debug_code_tool(task_description, file_content)
        elif action_type == "git_operation":
            return self._execute_git_command_tool(task_description, file_content)
        elif action_type == "analyze_file":
            return self._analyze_file_tool(task_description, file_content)
        elif action_type == "analyze_image":
            return self._analyze_image_tool(task_description, file_data, file_type)
        elif action_type == "analyze_document":
            return self._analyze_document_tool(task_description, file_content, file_type)
        elif action_type == "generate_ideas":
            return self._generate_ideas_tool(task_description, file_content)
        elif action_type == "general_ai":
            return self._general_purpose_ai_tool(task_description, file_content, file_data, file_type)
        else:
            return "Unknown action type requested by the planning module."

    def _generate_code_tool(self, prompt, file_content=None):
        llm_prompt_parts = [{"text": f"Generate code based on the following request. Provide only the code, no explanations:\n{prompt}"}]
        if file_content:
            llm_prompt_parts.append({"text": f"\n\nConsider this file content for context or modification:\n```\n{file_content}\n```"})
        return self._call_gemini(llm_prompt_parts)

    def _debug_code_tool(self, prompt, file_content=None):
        llm_prompt_parts = [{"text": f"Analyze the following code/error and suggest debugging steps or corrections. Be concise:\n"}]
        if file_content:
            llm_prompt_parts.append({"text": f"Code from file:\n```\n{file_content}\n```\n"})
        llm_prompt_parts.append({"text": f"User prompt/additional context: {prompt}"})
        return self._call_gemini(llm_prompt_parts)

    def _execute_git_command_tool(self, prompt, file_content=None):
        llm_prompt_parts = [{"text": f"Based on the following request, provide a simulated outcome for a Git command. Do not actually execute it. Request: {prompt}"}]
        if file_content:
            llm_prompt_parts.append({"text": f"\n\nFile content:\n```\n{file_content}\n```"})
        return self._call_gemini(llm_prompt_parts)

    def _analyze_file_tool(self, prompt, file_content):
        if not file_content:
            return "No text file content provided for analysis."
        llm_prompt_parts = [{"text": f"Analyze the following text file content. {prompt if prompt else 'Provide a summary.'}:\n```\n{file_content}\n```"}]
        return self._call_gemini(llm_prompt_parts)

    def _analyze_image_tool(self, prompt, image_data, image_type):
        if not image_data or not image_type:
            return "No image data provided for analysis."

        llm_prompt_parts = [
            {"text": prompt if prompt else "Describe this image in detail."},
            {"inlineData": {"mimeType": image_type, "data": image_data}}
        ]
        return self._call_gemini(llm_prompt_parts)

    def _analyze_document_tool(self, prompt, file_content, file_type):
        if not file_content:
            return f"No content extracted from {file_type} for analysis."
        
        llm_prompt_parts = [{"text": f"Analyze the content of this document (type: {file_type}). {prompt if prompt else 'Provide a summary.'}:\n```\n{file_content}\n```"}]
        return self._call_gemini(llm_prompt_parts)

    def _generate_ideas_tool(self, prompt, file_content=None):
        llm_prompt = (
            f"Generate a list of creative ideas based on the following request.\n"
            f"Provide ONLY a JSON array of strings.\n"
            f"Request: {prompt}"
        )
        if file_content:
            llm_prompt += f"\n\nConsider this file content:\n```\n{file_content}\n```"
        
        generation_config = {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            }
        }
        return self._call_gemini([{"text": llm_prompt}], generation_config=generation_config)

    def _general_purpose_ai_tool(self, prompt, file_content=None, file_data=None, file_type=None):
        llm_prompt_parts = [
            {"text": (
                f"You are a general-purpose AI assistant. Provide concise and informative answers to the user's request. "
                f"User Request: {prompt}"
            )}
        ]
        if file_data and file_type and file_type.startswith('image/'):
            llm_prompt_parts.append({"inlineData": {"mimeType": file_type, "data": file_data}})
        elif file_content:
            llm_prompt_parts.append({"text": f"\n\nAdditional context from file:\n```\n{file_content}\n```"})
            
        return self._call_gemini(llm_prompt_parts)


agent = AgentCore(api_key=os.getenv('GEMINI_API_KEY', ''))

def home_view(request):
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def agent_api_view(request):
    try:
        action_type_from_frontend = request.POST.get('action_type')
        prompt = request.POST.get('prompt', '').strip()
        
        uploaded_file_data = request.POST.get('uploaded_file_data')
        uploaded_file_type = request.POST.get('uploaded_file_type')
        uploaded_file = request.FILES.get('uploaded_file')

        file_content = None
        file_data_for_llm = None
        file_type_for_llm = None

        if uploaded_file:
            if uploaded_file.size > 2 * 1024 * 1024:
                return JsonResponse({"error": "File size exceeds 2MB limit."}, status=400)
            
            file_type_for_llm = uploaded_file.content_type
            
            if file_type_for_llm and file_type_for_llm.startswith('image/'):
                file_data_for_llm = base64.b64encode(uploaded_file.read()).decode('utf-8')
            elif file_type_for_llm in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                try:
                    file_content = uploaded_file.read().decode('utf-8')
                except UnicodeDecodeError:
                    file_content = f"Binary content. (Text extraction not implemented)"
            else:
                try:
                    file_content = uploaded_file.read().decode('utf-8')
                except UnicodeDecodeError:
                    file_content = f"Could not decode text file."
        
        elif uploaded_file_data and uploaded_file_type:
            file_data_for_llm = uploaded_file_data
            file_type_for_llm = uploaded_file_type

        valid_action_types = [
            "code_generation", "debugging", "git_operation", "analyze_file",
            "generate_ideas", "general_ai", "analyze_image", "analyze_document"
        ]
        
        if not action_type_from_frontend in valid_action_types:
             action_type_from_frontend = 'general_ai'

        action_plan = agent.planning_module(prompt, file_content, file_data_for_llm, file_type_for_llm, action_type_from_frontend)
        result = agent.tool_executor(action_plan)

        # ── FIX: Return 429 if the rate limit error string is caught ──
        if isinstance(result, str) and result.startswith("Error:"):
            return JsonResponse({"error": result}, status=429)

        # ── FIX: Only save to database if successful ──
        Interaction.objects.create(
            prompt=prompt[:2000],  
            result=result if isinstance(result, str) else json.dumps(result),
            action_type=action_type_from_frontend
        )

        return JsonResponse({"result": result})

    except Exception as e:
        print(f"Server error: {e}")
        return JsonResponse({"error": f"Internal server error: {e}"}, status=500)

@require_http_methods(["GET"])
def get_history_view(request):
    try:
        interactions = Interaction.objects.all().order_by('created_at')
        
        history_list = []
        for interaction in interactions:
            history_list.append({
                "prompt": interaction.prompt,
                "action_type": interaction.action_type,
                "result": interaction.result,
                "timestamp": interaction.created_at.isoformat()
            })

        return JsonResponse({"history": history_list})
    except Exception as e:
        print(f"Error fetching history: {e}")
        return JsonResponse({"error": f"Internal server error fetching history: {e}"}, status=500)
# Add this alongside your other views in views.py
@csrf_exempt
@require_http_methods(["DELETE"])
def clear_history_view(request):
    try:
        Interaction.objects.all().delete()
        return JsonResponse({"message": "History cleared successfully"})
    except Exception as e:
        print(f"Error clearing history: {e}")
        return JsonResponse({"error": f"Internal server error clearing history: {e}"}, status=500)