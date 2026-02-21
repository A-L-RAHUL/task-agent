alr@As-MacBook-Air agent-anti % python main.py
zsh: command not found: python
alr@As-MacBook-Air agent-anti % ./.venv/bin/python main.py
/Users/alr/Desktop/agent-anti/.venv/lib/python3.9/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  warnings.warn(
/Users/alr/Desktop/agent-anti/.venv/lib/python3.9/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/alr/Desktop/agent-anti/.venv/lib/python3.9/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/alr/Desktop/agent-anti/.venv/lib/python3.9/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/alr/Desktop/agent-anti/.venv/lib/python3.9/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.ai.generativelanguage_v1beta supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.ai.generativelanguage_v1beta.
  warnings.warn(message, FutureWarning)
Initializing Restaurant Agent...
/Users/alr/Desktop/agent-anti/agent.py:104: LangChainDeprecationWarning: Please see the migration guide at: https://python.langchain.com/docs/versions/migrating_memory/
  memory = ConversationBufferMemory(

****************************************
* Welcome to the Restaurant Terminal! *
****************************************

The waiter is ready. Type 'quit', 'exit', or 'bye' to leave.

You: hi, whats good here
Waiter: Hello! Welcome to our restaurant. I'd be happy to tell you about our menu or answer any questions you might have.

Some popular items include our **Classic Burger** and the **Margherita Pizza** for mains. For appetizers, the **Mozzarella Sticks** are always a hit.


You: types in burgers
Waiter: We have the **Classic Burger** for $10.00. It comes with a beef patty, lettuce, tomato, and house sauce. Would you like to add that to your order?


You: sounds good
Waiter: Great! One Classic Burger added. Anything else I can get for you?


You: deserts?
Waiter: I apologize, but we don't have any desserts on our current menu.


You: then just burger

=========================
--- KITCHEN TICKET ---
1.0x Classic Burger ($10.00 each)
-------------------------
Total: $10.00
=========================

Waiter: Your order for one Classic Burger has been placed. Your total comes to $10.00. Thank you for your order!

You: thankyou
Waiter: You're very welcome! Enjoy your meal.

You: yep
Waiter: Is there anything else I can assist you with today?

You: nothing
Waiter: Alright, thank you! Have a great day.

You: same to you
Waiter: Thank you!

You: bye

Waiter: Thank you for visiting! Have a great day!
alr@As-MacBook-Air agent-anti % 
 *  History restored
