import React, { useState, useEffect } from 'react';
import { MenuItem, Order } from '../types';
import { Plus, Trash2, Edit2, RefreshCw, LogIn } from 'lucide-react';

export default function OwnerDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [menu, setMenu] = useState<MenuItem[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [newItem, setNewItem] = useState({ name: '', description: '', price: 0 });
  const [editingItem, setEditingItem] = useState<MenuItem | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      fetchMenu();
      fetchOrders();
    }
  }, [isAuthenticated]);

  const fetchMenu = async () => {
    const res = await fetch('/api/menu');
    const data = await res.json();
    setMenu(data);
  };

  const fetchOrders = async () => {
    const res = await fetch('/api/orders');
    const data = await res.json();
    setOrders(data);
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === 'password') {
      setIsAuthenticated(true);
    } else {
      alert('Invalid password');
    }
  };

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    await fetch('/api/menu', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newItem),
    });
    setNewItem({ name: '', description: '', price: 0 });
    fetchMenu();
  };

  const handleDeleteItem = async (id: number) => {
    await fetch(`/api/menu/${id}`, { method: 'DELETE' });
    fetchMenu();
  };

  const handleUpdateItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingItem) return;
    await fetch(`/api/menu/${editingItem.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editingItem),
    });
    setEditingItem(null);
    fetchMenu();
  };

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <form onSubmit={handleLogin} className="bg-white p-8 rounded-2xl shadow-xl border border-black/5 w-full max-w-md">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-emerald-100 rounded-xl">
              <LogIn className="w-6 h-6 text-emerald-600" />
            </div>
            <h2 className="text-2xl font-bold">Owner Login</h2>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 outline-none"
                placeholder="Enter 'password'"
              />
            </div>
            <button
              type="submit"
              className="w-full bg-emerald-600 text-white py-2 rounded-xl font-medium hover:bg-emerald-700 transition-colors"
            >
              Login
            </button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Menu Management */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-black/5">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold flex items-center gap-2">
              <Plus className="w-5 h-5 text-emerald-600" />
              Manage Menu
            </h3>
          </div>

          <form onSubmit={handleAddItem} className="space-y-4 mb-8 p-4 bg-gray-50 rounded-xl">
            <div className="grid grid-cols-2 gap-4">
              <input
                placeholder="Item Name"
                value={newItem.name}
                onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                className="px-4 py-2 rounded-lg border border-gray-200 outline-none focus:ring-2 focus:ring-emerald-500"
                required
              />
              <input
                type="number"
                step="0.01"
                placeholder="Price"
                value={newItem.price || ''}
                onChange={(e) => setNewItem({ ...newItem, price: parseFloat(e.target.value) })}
                className="px-4 py-2 rounded-lg border border-gray-200 outline-none focus:ring-2 focus:ring-emerald-500"
                required
              />
            </div>
            <textarea
              placeholder="Description"
              value={newItem.description}
              onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
              className="w-full px-4 py-2 rounded-lg border border-gray-200 outline-none focus:ring-2 focus:ring-emerald-500"
              rows={2}
            />
            <button type="submit" className="w-full bg-emerald-600 text-white py-2 rounded-lg font-medium hover:bg-emerald-700">
              Add Item
            </button>
          </form>

          <div className="space-y-3">
            {menu.map((item) => (
              <div key={item.id} className="flex items-center justify-between p-4 border border-gray-100 rounded-xl hover:bg-gray-50 transition-colors">
                <div>
                  <h4 className="font-bold">{item.name}</h4>
                  <p className="text-sm text-gray-500">{item.description}</p>
                  <p className="text-emerald-600 font-medium">${item.price.toFixed(2)}</p>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => setEditingItem(item)} className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg">
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button onClick={() => handleDeleteItem(item.id)} className="p-2 text-red-600 hover:bg-red-50 rounded-lg">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Orders Dashboard */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-black/5">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold flex items-center gap-2">
              <RefreshCw className="w-5 h-5 text-emerald-600" />
              Incoming Orders
            </h3>
            <button onClick={fetchOrders} className="text-sm text-emerald-600 hover:underline">Refresh</button>
          </div>

          <div className="space-y-4">
            {orders.map((order) => (
              <div key={order.id} className="p-4 border border-gray-100 rounded-xl bg-gray-50">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-mono text-gray-400">Order #{order.id}</span>
                  <span className="text-xs text-gray-500">{new Date(order.timestamp).toLocaleString()}</span>
                </div>
                <p className="font-medium text-gray-800 mb-2">{order.items}</p>
                <div className="flex justify-between items-center pt-2 border-top border-gray-200">
                  <span className="text-sm text-gray-500">Total Bill</span>
                  <span className="text-lg font-bold text-emerald-600">${order.total_price.toFixed(2)}</span>
                </div>
              </div>
            ))}
            {orders.length === 0 && (
              <div className="text-center py-12 text-gray-400">
                No orders yet
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {editingItem && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white p-6 rounded-2xl w-full max-w-md">
            <h3 className="text-xl font-bold mb-4">Edit Item</h3>
            <form onSubmit={handleUpdateItem} className="space-y-4">
              <input
                value={editingItem.name}
                onChange={(e) => setEditingItem({ ...editingItem, name: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-200"
              />
              <textarea
                value={editingItem.description}
                onChange={(e) => setEditingItem({ ...editingItem, description: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-200"
              />
              <input
                type="number"
                step="0.01"
                value={editingItem.price}
                onChange={(e) => setEditingItem({ ...editingItem, price: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 rounded-lg border border-gray-200"
              />
              <div className="flex gap-3">
                <button type="submit" className="flex-1 bg-emerald-600 text-white py-2 rounded-lg">Save</button>
                <button type="button" onClick={() => setEditingItem(null)} className="flex-1 bg-gray-100 py-2 rounded-lg">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
