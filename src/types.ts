export interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
}

export interface Order {
  id: number;
  items: string;
  total_price: number;
  timestamp: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}
