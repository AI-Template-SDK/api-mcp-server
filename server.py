from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("senso")

# Constants
SENSO_API_BASE = "https://sdk.senso.ai/api/v1"
API_KEY = "tgr_YOUR_API_KEY"  # Will be set during startup

async def make_senso_request(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Make a request to the Senso API with proper error handling."""
    url = f"{SENSO_API_BASE}{endpoint}"
    headers = {
        "X-API-Key": API_KEY,
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            if method.lower() == "get":
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            elif method.lower() == "post":
                if files:
                    response = await client.post(url, headers=headers, data=params, files=files, timeout=30.0)
                else:
                    response = await client.post(url, headers=headers, json=json_data, timeout=30.0)
            elif method.lower() == "put":
                response = await client.put(url, headers=headers, json=json_data, timeout=30.0)
            elif method.lower() == "patch":
                response = await client.patch(url, headers=headers, json=json_data, timeout=30.0)
            elif method.lower() == "delete":
                response = await client.delete(url, headers=headers, timeout=30.0)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json()
                error_message = error_detail.get("error", str(e))
            except Exception:
                error_message = str(e)
            
            raise Exception(f"API Error: {error_message}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

@mcp.tool()
async def add_raw_content(
    title: Optional[str] = None,
    summary: Optional[str] = None,
    text: str = None
) -> str:
    """Add raw text content to the knowledge base.
    
    Args:
        title: The title of the content (optional)
        summary: Summary of the content (optional)
        text: The raw text content to add
    """
    if not text:
        return "Error: Content text is required"
    
    request_data = {
        "text": text
    }
    
    if title:
        request_data["title"] = title
    
    if summary:
        request_data["summary"] = summary
    
    try:
        response = await make_senso_request("post", "/content/raw", json_data=request_data)
        return f"Content successfully added with ID: {response.get('id', 'unknown')}\nTitle: {response.get('title', 'Untitled')}"
    except Exception as e:
        return f"Failed to add content: {str(e)}"

@mcp.tool()
async def search_content(
    query: str,
    max_results: int = 5
) -> str:
    """Search for content in the knowledge base.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return (default is 5)
    """
    if not query:
        return "Error: Query is required"
    
    request_data = {
        "query": query,
        "max_results": max_results
    }
    
    try:
        response = await make_senso_request("post", "/search", json_data=request_data)
        
        answer = response.get("answer", "No answer generated.")
        results = response.get("results", [])
        
        if not results:
            return f"No relevant information found for query: '{query}'."
        
        # Format results for display
        output = f"Answer: {answer}\n\nFound {len(results)} relevant results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            output += f"Result {i}:\n"
            output += f"Title: {result.get('title', 'No title')}\n"
            output += f"Content: {result.get('chunk_text', 'No content')}\n"
            output += f"ID: {result.get('content_id', 'No ID')}\n\n"
        
        return output
    except Exception as e:
        return f"Search failed: {str(e)}"

@mcp.tool()
async def generate_content(
    content_type: str,
    instructions: str,
    save: bool = False,
    max_results: int = 5
) -> str:
    """Generate content based on instructions and existing knowledge.
    
    Args:
        content_type: Type of content to generate
        instructions: Instructions for content generation
        save: Whether to save the generated content (default is false)
        max_results: Maximum number of source results to use (default is 5)
    """
    if not content_type or not instructions:
        return "Error: Content type and instructions are required"
    
    request_data = {
        "content_type": content_type,
        "instructions": instructions,
        "save": save,
        "max_results": max_results
    }
    
    try:
        response = await make_senso_request("post", "/generate", json_data=request_data)
        
        generated_text = response.get("generated_text", "No content generated.")
        content_id = response.get("content_id")
        sources = response.get("sources", [])
        
        # Format the response
        output = f"Generated content about {content_type}:\n\n{generated_text}\n\n"
        
        if content_id and save:
            output += f"Content was saved with ID: {content_id}\n\n"
        
        if sources:
            output += "Sources used for generation:\n"
            for i, source in enumerate(sources, 1):
                output += f"Source {i}: {source.get('title', 'No title')}\n"
        
        return output
    except Exception as e:
        return f"Content generation failed: {str(e)}"

@mcp.tool()
async def create_prompt(
    name: str,
    text: str
) -> str:
    """Create a new prompt for content generation.
    
    Args:
        name: The name of the prompt (must be unique)
        text: The prompt text with variables in {{variable}} format
    """
    if not name or not text:
        return "Error: Name and text are required"
    
    request_data = {
        "name": name,
        "text": text
    }
    
    try:
        response = await make_senso_request("post", "/prompts", json_data=request_data)
        return f"Prompt created successfully!\nID: {response.get('prompt_id')}\nName: {response.get('name')}"
    except Exception as e:
        return f"Failed to create prompt: {str(e)}"

@mcp.tool()
async def list_prompts(
    limit: int = 10,
    offset: int = 0
) -> str:
    """List all prompts in the organization.
    
    Args:
        limit: Maximum number of prompts to return (default 10, max 100)
        offset: Number of prompts to skip for pagination (default 0)
    """
    params = {
        "limit": min(limit, 100),
        "offset": offset
    }
    
    try:
        response = await make_senso_request("get", "/prompts", params=params)
        
        if not response:
            return "No prompts found."
        
        output = f"Prompts (showing {len(response)} results):\n\n"
        for prompt in response:
            output += f"ID: {prompt.get('prompt_id')}\n"
            output += f"Name: {prompt.get('name')}\n"
            output += f"Text: {prompt.get('text', '')[:100]}{'...' if len(prompt.get('text', '')) > 100 else ''}\n"
            output += f"Created: {prompt.get('created_at', 'Unknown')}\n\n"
        
        return output
    except Exception as e:
        return f"Failed to list prompts: {str(e)}"

@mcp.tool()
async def update_prompt(
    prompt_id: str,
    name: str,
    text: str
) -> str:
    """Update an existing prompt.
    
    Args:
        prompt_id: The ID of the prompt to update
        name: The new name for the prompt
        text: The new text for the prompt
    """
    if not prompt_id or not name or not text:
        return "Error: Prompt ID, name, and text are required"
    
    request_data = {
        "name": name,
        "text": text
    }
    
    try:
        response = await make_senso_request("put", f"/prompts/{prompt_id}", json_data=request_data)
        return f"Prompt updated successfully!\nID: {response.get('prompt_id')}\nName: {response.get('name')}"
    except Exception as e:
        return f"Failed to update prompt: {str(e)}"

@mcp.tool()
async def create_template(
    name: str,
    text: str,
    output_type: str = "text"
) -> str:
    """Create a new template for output formatting.
    
    Args:
        name: The name of the template (must be unique)
        text: The template text with variables in {{variable}} format
        output_type: The output format - 'json' or 'text' (default is 'text')
    """
    if not name or not text:
        return "Error: Name and text are required"
    
    if output_type not in ["json", "text"]:
        return "Error: output_type must be 'json' or 'text'"
    
    request_data = {
        "name": name,
        "text": text,
        "output_type": output_type
    }
    
    try:
        response = await make_senso_request("post", "/templates", json_data=request_data)
        return f"Template created successfully!\nID: {response.get('template_id')}\nName: {response.get('name')}\nOutput Type: {response.get('output_type')}"
    except Exception as e:
        return f"Failed to create template: {str(e)}"

@mcp.tool()
async def list_templates(
    limit: int = 10,
    offset: int = 0
) -> str:
    """List all templates in the organization.
    
    Args:
        limit: Maximum number of templates to return (default 10, max 100)
        offset: Number of templates to skip for pagination (default 0)
    """
    params = {
        "limit": min(limit, 100),
        "offset": offset
    }
    
    try:
        response = await make_senso_request("get", "/templates", params=params)
        
        if not response:
            return "No templates found."
        
        output = f"Templates (showing {len(response)} results):\n\n"
        for template in response:
            output += f"ID: {template.get('template_id')}\n"
            output += f"Name: {template.get('name')}\n"
            output += f"Output Type: {template.get('output_type')}\n"
            output += f"Text: {template.get('text', '')[:100]}{'...' if len(template.get('text', '')) > 100 else ''}\n"
            output += f"Created: {template.get('created_at', 'Unknown')}\n\n"
        
        return output
    except Exception as e:
        return f"Failed to list templates: {str(e)}"

@mcp.tool()
async def update_template(
    template_id: str,
    name: str,
    text: str,
    output_type: str = "text"
) -> str:
    """Update an existing template.
    
    Args:
        template_id: The ID of the template to update
        name: The new name for the template
        text: The new text for the template
        output_type: The output format - 'json' or 'text'
    """
    if not template_id or not name or not text:
        return "Error: Template ID, name, and text are required"
    
    if output_type not in ["json", "text"]:
        return "Error: output_type must be 'json' or 'text'"
    
    request_data = {
        "name": name,
        "text": text,
        "output_type": output_type
    }
    
    try:
        response = await make_senso_request("put", f"/templates/{template_id}", json_data=request_data)
        return f"Template updated successfully!\nID: {response.get('template_id')}\nName: {response.get('name')}"
    except Exception as e:
        return f"Failed to update template: {str(e)}"

@mcp.tool()
async def generate_with_prompt(
    prompt_id: str,
    content_type: str,
    template_id: Optional[str] = None,
    save: bool = False,
    max_results: int = 25
) -> str:
    """Generate content using a saved prompt and optional template.
    
    Args:
        prompt_id: The ID of the prompt to use
        content_type: Description of what content to search for in the knowledge base
        template_id: Optional ID of a template to format the output
        save: Whether to save the generated content (default is false)
        max_results: Maximum number of source results to use (default is 25)
    """
    if not prompt_id or not content_type:
        return "Error: Prompt ID and content type are required"
    
    request_data = {
        "prompt_id": prompt_id,
        "content_type": content_type,
        "save": save,
        "max_results": max_results
    }
    
    if template_id:
        request_data["template_id"] = template_id
    
    try:
        response = await make_senso_request("post", "/generate/prompt", json_data=request_data)
        
        generated_text = response.get("generated_text", "No content generated.")
        content_id = response.get("content_id")
        prompt_info = response.get("prompt", {})
        template_info = response.get("template")
        sources = response.get("sources", [])
        
        # Format the response
        output = f"Generated content using prompt '{prompt_info.get('name', 'Unknown')}':\n\n"
        output += f"{generated_text}\n\n"
        
        if template_info:
            output += f"Formatted with template: {template_info.get('name')} ({template_info.get('output_type')})\n\n"
        
        if content_id and save:
            output += f"Content was saved with ID: {content_id}\n\n"
        
        if sources:
            output += f"Sources used ({len(sources)} total):\n"
            for i, source in enumerate(sources[:5], 1):  # Show first 5 sources
                output += f"- {source.get('title', 'No title')}\n"
            if len(sources) > 5:
                output += f"... and {len(sources) - 5} more sources\n"
        
        return output
    except Exception as e:
        return f"Content generation with prompt failed: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    print("starting server...")
    mcp.run(transport='stdio')
