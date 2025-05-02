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

if __name__ == "__main__":
    # Initialize and run the server
    print("starting server...")
    mcp.run(transport='stdio')
