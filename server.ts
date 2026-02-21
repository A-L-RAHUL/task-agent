import express from "express";
import { createServer as createViteServer } from "vite";
import Database from "better-sqlite3";
import path from "path";

const db = new Database("restaurant.db");

// Initialize database
db.exec(`
  CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL
  );
  CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    items TEXT NOT NULL,
    total_price REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

async function startServer() {
  const app = express();
  app.use(express.json());
  const PORT = 3000;

  // API Routes
  app.get("/api/menu", (req, res) => {
    const items = db.prepare("SELECT * FROM menu_items").all();
    res.json(items);
  });

  app.post("/api/menu", (req, res) => {
    const { name, description, price } = req.body;
    const info = db.prepare("INSERT INTO menu_items (name, description, price) VALUES (?, ?, ?)").run(name, description, price);
    res.json({ id: info.lastInsertRowid });
  });

  app.put("/api/menu/:id", (req, res) => {
    const { name, description, price } = req.body;
    db.prepare("UPDATE menu_items SET name = ?, description = ?, price = ? WHERE id = ?").run(name, description, price, req.params.id);
    res.json({ success: true });
  });

  app.delete("/api/menu/:id", (req, res) => {
    db.prepare("DELETE FROM menu_items WHERE id = ?").run(req.params.id);
    res.json({ success: true });
  });

  app.get("/api/orders", (req, res) => {
    const orders = db.prepare("SELECT * FROM orders ORDER BY timestamp DESC").all();
    res.json(orders);
  });

  app.post("/api/orders", (req, res) => {
    const { items, total_price } = req.body;
    const info = db.prepare("INSERT INTO orders (items, total_price) VALUES (?, ?)").run(items, total_price);
    res.json({ id: info.lastInsertRowid });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static("dist"));
    app.get("*", (req, res) => {
      res.sendFile(path.resolve("dist/index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
