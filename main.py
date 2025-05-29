import os
import mysql.connector
from typing import List, Dict, Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        raise

# Create an MCP server
mcp = FastMCP("Demo")

@mcp.tool()
def get_customer_by_name(name: str) -> List[Dict[str, Any]]:
    """
    Retrieve customer information by name from the database.
    
    Args:
        name: The name of the customer to search for
        
    Returns:
        List of customer records matching the name
    """
    query = """
        SELECT * 
        FROM customer 
        WHERE name = %s
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (name,))
        
        # Fetch all rows and convert to list of dicts
        customers = cursor.fetchall()
        
        # Convert any non-serializable types to strings
        for customer in customers:
            for key, value in customer.items():
                if not isinstance(value, (str, int, float, bool, type(None))):
                    customer[key] = str(value)
        
        return customers
        
    except Exception as e:
        return [{"error": f"Failed to fetch customer data: {str(e)}"}]
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.app, host="0.0.0.0", port=8000)