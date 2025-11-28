import asyncio
import os
import json
from typing import Optional

from mcp import ClientSession
from mcp.client.sse import sse_client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BANK_MCP_URL = "http://localhost:3000/sse"

# System prompt for Disha
DISHA_SYSTEM_PROMPT = """
You are Disha, a compassionate financial advisor for low-income Indians.

YOUR USER CONTEXT:
- Rickshaw driver with irregular daily income (₹600-1000/day)
- Family of 4, Monthly income ~₹18,000
- Lives paycheck to paycheck

YOUR MISSION:
1. Build emergency fund (target: 3 months expenses = ~₹15,000)
2. Identify wasteful spending (tea stalls, Dream11 gambling, unnecessary expenses)
3. Help save for specific goals (school fees, festivals, medical emergencies)
4. Predict upcoming expenses using bill history

COMMUNICATION STYLE:
- Mix Hindi/English (Hinglish): "Aapne Dream11 pe ₹500 kharch kiye, ye bahut zyada hai!"
- Be direct but respectful about bad habits
- Celebrate small wins: "Wah! Aapne ₹200 save kiye!"
- Use specific numbers from transactions
- Keep responses conversational and concise (2-4 sentences max for Telegram)

FINANCIAL RULES:
1. ALWAYS call 'get_account_details' first to check current balance
2. Use 'get_recent_transactions' to analyze spending before giving advice
3. Use 'analyze_spending_pattern' for detailed insights
4. Reference specific merchants/amounts: "Sharma Tea Stall pe ₹450 gaye is week"
5. Encourage emergency fund: minimum ₹5000 should always be there

NEVER:
- Give generic advice without data
- Ignore gambling spending (Dream11, etc.)
- Suggest risky investments
- Use complex financial jargon

EXAMPLES:
User: "Mera balance kitna hai?"
You: "Aapka balance ₹5,200 hai. Savings pocket mein ₹1,500 aur emergency fund mein ₹500 hai. Thoda aur emergency fund badhana chahiye! 💪"

User: "Is hafte kitna kharch hua?"
You: "Is hafte ₹890 kharch hue. Sharma Tea Stall pe ₹120 aur Dream11 pe ₹200 gaye. Bhai, Dream11 band karo! Wo paise save kar sakte ho. 🙏"
"""


class DishaAgent:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.bank_url = BANK_MCP_URL
        
    async def process_message(self, user_phone: str, user_message: str, conversation_history: Optional[list] = None) -> str:
        """
        Process a single message and return Disha's response.
        
        Args:
            user_phone: User's phone number (account identifier)
            user_message: The user's query
            conversation_history: Optional list of previous messages for context
            
        Returns:
            Disha's response as a string
        """
        try:
            async with sse_client(self.bank_url) as streams:
                async with ClientSession(streams[0], streams[1]) as session:
                    await session.initialize()
                    
                    # Fetch MCP tools from bank
                    mcp_tools_list = await session.list_tools()
                    
                    # Convert to OpenAI format
                    openai_tools = []
                    for tool in mcp_tools_list.tools:
                        openai_tools.append({
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": tool.inputSchema
                            }
                        })
                    
                    # Build conversation context
                    messages = [{"role": "system", "content": DISHA_SYSTEM_PROMPT}]
                    
                    # Add conversation history if provided
                    if conversation_history:
                        messages.extend(conversation_history)
                    
                    # Add current user message
                    messages.append({
                        "role": "user", 
                        "content": f"User Phone: {user_phone}. Query: {user_message}"
                    })
                    
                    # First API call - get intent and tool calls
                    response = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        tools=openai_tools,
                        tool_choice="auto"
                    )
                    
                    assistant_msg = response.choices[0].message
                    messages.append(assistant_msg)
                    
                    # Handle tool calls if any
                    if assistant_msg.tool_calls:
                        for tool_call in assistant_msg.tool_calls:
                            func_name = tool_call.function.name
                            func_args = json.loads(tool_call.function.arguments)
                            call_id = tool_call.id
                            
                            try:
                                # Execute tool via MCP
                                mcp_result = await session.call_tool(func_name, func_args)
                                
                                # Extract text content
                                result_text = ""
                                for content in mcp_result.content:
                                    if content.type == 'text':
                                        result_text += content.text
                                
                                # Add tool result to conversation
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": call_id,
                                    "content": result_text
                                })
                                
                            except Exception as e:
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": call_id,
                                    "content": f"Error: {str(e)}"
                                })
                        
                        # Second API call - generate final response
                        final_response = self.client.chat.completions.create(
                            model="gpt-4o",
                            messages=messages
                        )
                        return final_response.choices[0].message.content
                    
                    else:
                        # No tool calls, return direct response
                        return assistant_msg.content
                        
        except Exception as e:
            return f"Sorry, kuch technical problem hai: {str(e)}"


# CLI interface for testing
async def run_terminal_chat():
    """Terminal-based chat for testing"""
    agent = DishaAgent()
    user_phone = "9876543210"
    
    print("🤖 Disha Terminal Chat (Type 'quit' to exit)")
    print("-" * 50)
    
    conversation_history = []
    
    while True:
        user_input = input("\n👤 You: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        
        print("💭 Thinking...")
        response = await agent.process_message(user_phone, user_input, conversation_history)
        print(f"\n💬 Disha: {response}")
        
        # Store conversation (optional for context)
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    try:
        asyncio.run(run_terminal_chat())
    except KeyboardInterrupt:
        print("\nGoodbye!")