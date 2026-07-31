import React, { useEffect, useState } from "react";
import { fetchProducts } from "./salesAPI";
import { ProductCard } from "./ProductCard";
import { Cart } from "./Cart";

const SalesPage = () => {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);

  useEffect(() => {
    fetchProducts().then(setProducts);
  }, []);

  const addToCart = (product) => setCart(prev => [...prev, product]);
  const removeFromCart = (id) => setCart(prev => prev.filter(p => p.id !== id));

  return (
    <div style={{ display: 'flex', gap: '2rem', padding: '2rem' }}>
      <div>
        <h1>Productos</h1>
        {products.map(product => (
          <ProductCard key={product.id} product={product} onAddToCart={addToCart} />
        ))}
      </div>
      <Cart cart={cart} onRemove={removeFromCart} />
    </div>
  );
};

export default SalesPage;
