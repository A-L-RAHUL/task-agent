import React, { useState } from 'react';
import ChatBot from './components/ChatBot';
import OwnerDashboard from './components/OwnerDashboard';
import { Utensils, User, ShieldCheck } from 'lucide-react';

export default function App() {
  const [view, setView] = useState<'customer' | 'owner'>('customer');

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Navigation Rail */}
      <nav className="fixed top-0 left-0 right-0 bg-white border-b border-black/5 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-emerald-600 rounded-lg">
              <Utensils className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight">GourmetAI</span>
          </div>
          
          <div className="flex bg-gray-100 p-1 rounded-xl">
            <button
              onClick={() => setView('customer')}
              className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                view === 'customer' ? 'bg-white shadow-sm text-emerald-600' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <User className="w-4 h-4" />
              Customer
            </button>
            <button
              onClick={() => setView('owner')}
              className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                view === 'owner' ? 'bg-white shadow-sm text-emerald-600' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <ShieldCheck className="w-4 h-4" />
              Owner
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-24 pb-12 px-4 max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-2">
            {view === 'customer' ? 'Welcome to GourmetAI' : 'Owner Dashboard'}
          </h1>
          <p className="text-gray-500">
            {view === 'customer' 
              ? 'Our AI waiter is ready to take your order.' 
              : 'Manage your menu and track incoming orders in real-time.'}
          </p>
        </div>

        {view === 'customer' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <ChatBot />
            </div>
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-black/5">
                <h3 className="font-bold mb-4 flex items-center gap-2">
                  <Utensils className="w-4 h-4 text-emerald-600" />
                  How it works
                </h3>
                <ul className="space-y-3 text-sm text-gray-600">
                  <li className="flex gap-2">
                    <span className="text-emerald-600 font-bold">1.</span>
                    Ask about our menu items and prices.
                  </li>
                  <li className="flex gap-2">
                    <span className="text-emerald-600 font-bold">2.</span>
                    Tell the waiter what you'd like to order.
                  </li>
                  <li className="flex gap-2">
                    <span className="text-emerald-600 font-bold">3.</span>
                    The waiter will confirm and place your order.
                  </li>
                </ul>
              </div>
              <div className="bg-emerald-600 p-6 rounded-2xl shadow-lg text-white">
                <h3 className="font-bold mb-2">Fresh & Fast</h3>
                <p className="text-sm text-emerald-100 mb-4">
                  Our kitchen is now integrated with AI to ensure your order is processed instantly.
                </p>
                <div className="h-1 bg-white/20 rounded-full overflow-hidden">
                  <div className="h-full bg-white w-2/3"></div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <OwnerDashboard />
        )}
      </main>
    </div>
  );
}
