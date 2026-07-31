import React from "react";

export const Cart = ({ cart, onRemove }) => (
  <div style={{ borderLeft: "1px solid #ddd", paddingLeft: "1rem" }}>
    <h2>Carrito</h2>
    {cart.length === 0 ? (
      <p>El carrito está vacío</p>
    ) : (
      cart.map((item, index) => (
        <div key={`${item.id}-${index}`}>
          <span>{item.title} - ${item.price.toFixed(2)}</span> 
          <button onClick={() => onRemove(item.id)}>Quitar</button>
        </div>
      ))
    )}
    {cart.length > 0 && (
      <h3>Total: ${cart.reduce((sum, p) => sum + p.price, 0).toFixed(2)}</h3>
    )}
  </div>
);