import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ProductCard } from '../ProductCard';

describe('ProductCard', () => {
  const mockProduct = {
    id: 1,
    title: 'Camiseta React',
    price: 29.99,
    image: 'https://example.com/react-shirt.jpg'
  };

  const mockOnAddToCart = jest.fn();

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renderiza correctamente con todas las propiedades', () => {
    render(<ProductCard product={mockProduct} onAddToCart={mockOnAddToCart} />);
    
    expect(screen.getByRole('img')).toBeInTheDocument();
    expect(screen.getByText(mockProduct.title)).toBeInTheDocument();
    expect(screen.getByText('$29.99')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /agregar al carrito/i })).toBeInTheDocument();
  });

  it('muestra la imagen con los atributos correctos', () => {
    render(<ProductCard product={mockProduct} onAddToCart={mockOnAddToCart} />);
    
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', mockProduct.image);
    expect(img).toHaveAttribute('alt', mockProduct.title);
    expect(img).toHaveAttribute('width', '100');
    expect(img).toHaveAttribute('height', '100');
  });

  it('llama a onAddToCart cuando se hace clic en el botón', () => {
    render(<ProductCard product={mockProduct} onAddToCart={mockOnAddToCart} />);
    
    const button = screen.getByRole('button', { name: /agregar al carrito/i });
    fireEvent.click(button);
    
    expect(mockOnAddToCart).toHaveBeenCalledTimes(1);
    expect(mockOnAddToCart).toHaveBeenCalledWith(mockProduct);
  });

  it('no muestra la imagen cuando no está definida', () => {
    const productWithoutImage = {
      ...mockProduct,
      image: undefined
    };
    
    render(<ProductCard product={productWithoutImage} onAddToCart={mockOnAddToCart} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  it('muestra correctamente el precio con dos decimales', () => {
    const productsWithDifferentPrices = [
      { ...mockProduct, price: 20 },
      { ...mockProduct, price: 30.5 },
      { ...mockProduct, price: 15.99 },
    ];
    
    const { rerender } = render(
      <ProductCard product={productsWithDifferentPrices[0]} onAddToCart={mockOnAddToCart} />
    );
    expect(screen.getByText('$20.00')).toBeInTheDocument();
    
    rerender(<ProductCard product={productsWithDifferentPrices[1]} onAddToCart={mockOnAddToCart} />);
    expect(screen.getByText('$30.50')).toBeInTheDocument();
    
    rerender(<ProductCard product={productsWithDifferentPrices[2]} onAddToCart={mockOnAddToCart} />);
    expect(screen.getByText('$15.99')).toBeInTheDocument();
  });

  it('maneja correctamente un producto sin título', () => {
    const productWithoutTitle = {
      ...mockProduct,
      title: undefined
    };
    
    render(<ProductCard product={productWithoutTitle} onAddToCart={mockOnAddToCart} />);
    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
  });

  it('maneja correctamente un producto sin precio', () => {
    const productWithoutPrice = {
      ...mockProduct,
      price: undefined
    };
    
    render(<ProductCard product={productWithoutPrice} onAddToCart={mockOnAddToCart} />);
    expect(screen.queryByText(/\$/)).not.toBeInTheDocument();
  });

  it('muestra mensaje cuando el producto es undefined', () => {
    render(<ProductCard product={undefined} onAddToCart={mockOnAddToCart} />);
    expect(screen.getByText('Producto no disponible')).toBeInTheDocument();
  });

  it('muestra mensaje cuando el producto es null', () => {
    render(<ProductCard product={null} onAddToCart={mockOnAddToCart} />);
    expect(screen.getByText('Producto no disponible')).toBeInTheDocument();
  });

  it('muestra el botón deshabilitado cuando onAddToCart no está definido', () => {
    render(<ProductCard product={mockProduct} onAddToCart={undefined} />);
    const button = screen.getByRole('button', { name: /agregar al carrito/i });
    expect(button).toBeDisabled();
  });

  it('no llama a onAddToCart cuando está undefined', () => {
    render(<ProductCard product={mockProduct} onAddToCart={undefined} />);
    const button = screen.getByRole('button', { name: /agregar al carrito/i });
    fireEvent.click(button);
    expect(mockOnAddToCart).not.toHaveBeenCalled();
  });
});