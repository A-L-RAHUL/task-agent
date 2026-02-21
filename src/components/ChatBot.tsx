import React, { useState, useEffect, useRef } from 'react';
import { GoogleGenAI, Type } from "@google/genai";
import { MenuItem, ChatMessage } from '../types';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export default function ChatBot() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [menu, setMenu] = useState<MenuItem[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchMenu();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const fetchMenu = async () => {
    const res = await fetch('/api/menu');
    const data = await res.json();
    setMenu(data);
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: ChatMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || '' });
      
      const menuText = menu.map(item => `- ${item.name}: ${item.description} ($${item.price.toFixed(2)})`).join('\n');
      
      const systemInstruction = `You are a polite and professional restaurant waiter. 
Your goal is to help customers browse the menu, answer questions about items, and take their order.

STRICT ADHERENCE RULES:
1. You MUST ONLY offer items that are present in the menu provided below.
2. If a customer asks for something NOT on the menu, politely inform them it is not available.
3. Do NOT make assumptions about ingredients or prices not listed.
4. When the user is ready to order, use the 'place_order' tool.
5. Be concise and helpful.

CURRENT MENU:
${menuText || 'The menu is currently empty.'}`;

      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        contents: [
          ...messages.map(m => ({ role: m.role === 'user' ? 'user' : 'model', parts: [{ text: m.content }] })),
          { role: 'user', parts: [{ text: input }] }
        ],
        config: {
          systemInstruction,
          tools: [{
            functionDeclarations: [{
              name: "place_order",
              description: "Finalizes the order and saves it to the database.",
              parameters: {
                type: Type.OBJECT,
                properties: {
                  items: {
                    type: Type.ARRAY,
                    items: {
                      type: Type.OBJECT,
                      properties: {
                        name: { type: Type.STRING, description: "Name of the item" },
                        quantity: { type: Type.NUMBER, description: "Quantity of the item" }
                      },
                      required: ["name", "quantity"]
                    }
                  }
                },
                required: ["items"]
              }
            }]
          }]
        }
      });

      const functionCalls = response.functionCalls;
      if (functionCalls) {
        for (const call of functionCalls) {
          if (call.name === 'place_order') {
            const args = call.args as { items: { name: string, quantity: number }[] };
            
            // Calculate total and prepare summary
            let total = 0;
            const summaryParts: string[] = [];
            for (const orderItem of args.items) {
              const menuItem = menu.find(m => m.name.toLowerCase() === orderItem.name.toLowerCase());
              if (menuItem) {
                total += menuItem.price * orderItem.quantity;
                summaryParts.push(`${menuItem.name} x${orderItem.quantity}`);
              }
            }

            if (summaryParts.length > 0) {
              const summary = summaryParts.join(', ');
              await fetch('/api/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ items: summary, total_price: total }),
              });
              
              const assistantMsg: ChatMessage = { 
                role: 'assistant', 
                content: `Perfect! I've placed your order for: ${summary}. Your total is $${total.toFixed(2)}. It will be ready shortly!` 
              };
              setMessages(prev => [...prev, assistantMsg]);
            } else {
              const assistantMsg: ChatMessage = { 
                role: 'assistant', 
                content: "I'm sorry, I couldn't find those items on our menu. Could you please double check the names?" 
              };
              setMessages(prev => [...prev, assistantMsg]);
            }
          }
        }
      } else {
        const assistantMsg: ChatMessage = { role: 'assistant', content: response.text || "I'm sorry, I didn't quite catch that." };
        setMessages(prev => [...prev, assistantMsg]);
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', content: "I'm having a bit of trouble connecting to the kitchen. Please try again in a moment." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[70vh] bg-white rounded-2xl shadow-xl border border-black/5 overflow-hidden">
      {/* Header */}
      <div className="bg-emerald-600 p-4 text-white flex items-center gap-3">
        <div className="p-2 bg-white/20 rounded-lg">
          <Bot className="w-6 h-6" />
        </div>
        <div>
          <h3 className="font-bold">AI Waiter</h3>
          <p className="text-xs text-emerald-100">Always here to help</p>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        <AnimatePresence initial={false}>
          {messages.length === 0 && (
            <motion.div 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }} 
              className="text-center py-12 text-gray-400"
            >
              <Bot className="w-12 h-12 mx-auto mb-3 opacity-20" />
              <p>Hello! I'm your AI waiter. How can I help you today?</p>
            </motion.div>
          )}
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex gap-3 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className={`p-2 rounded-lg h-fit ${msg.role === 'user' ? 'bg-emerald-100 text-emerald-600' : 'bg-white text-gray-600 shadow-sm'}`}>
                  {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>
                <div className={`p-3 rounded-2xl ${msg.role === 'user' ? 'bg-emerald-600 text-white rounded-tr-none' : 'bg-white text-gray-800 shadow-sm rounded-tl-none border border-gray-100'}`}>
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                </div>
              </div>
            </motion.div>
          ))}
          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
              <div className="bg-white p-3 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-emerald-600" />
                <span className="text-sm text-gray-400">Thinking...</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="p-4 bg-white border-t border-gray-100 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 px-4 py-2 rounded-xl border border-gray-200 outline-none focus:ring-2 focus:ring-emerald-500 transition-all"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="p-2 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
}
