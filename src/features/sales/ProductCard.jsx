import React from 'react';

export const ProductCard = ({ product = null, onAddToCart = null }) => {
  if (!product) {
    return <div className="card">Producto no disponible</div>;
  }

  return (
    <div className="card">
      {product.image && (
        <img 
          src={product.image} 
          alt={product.title || 'Producto'} 
          width={100} 
          height={100} 
        />
      )}
      {product.title && <h3>{product.title}</h3>}
      {product.price && <p>${product.price.toFixed(2)}</p>}
      <button 
        onClick={() => onAddToCart && onAddToCart(product)}
        disabled={!onAddToCart}
      >
        Agregar al carrito
      </button>
    </div>
  );
};