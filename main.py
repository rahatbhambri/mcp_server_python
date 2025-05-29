import os
import sys
import asyncio
import logging
import mysql.connector
from typing import List, Dict, Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from functools import reduce

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger('mcp_demo')

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

print('...', file=sys.stderr)
# Create an MCP server
logger.info("Initializing MCP server...")
try:
    mcp = FastMCP("Demo")
    logger.info("MCP server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MCP: {e}", exc_info=True)
    raise

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


@mcp.tool()
def calculate_magic_amount(amounts: List[int]) -> int:
    """Calculate the magic number from a list of amounts
    
    Args:
        amounts: A list of amounts
        
    Returns:
        The magic number calculated from the list of amounts"""   
    return reduce(lambda x, y: x * y, amounts)    