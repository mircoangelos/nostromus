import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Cart } from '../Cart';

describe('Cart', () => {
  const cartItems = [
    { id: 1, title: 'Camisa', price: 25.99 },
    { id: 2, title: 'Zapatos', price: 40.00 },
    { id: 3, title: 'Pantalón', price: 35.50 },
  ];

  const emptyCart = [];

  const mockOnRemove = jest.fn();

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('muestra el mensaje de carrito vacío si no hay productos', () => {
    render(<Cart cart={emptyCart} onRemove={mockOnRemove} />);
    expect(screen.getByText(/el carrito está vacío/i)).toBeInTheDocument();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
    expect(screen.queryByText(/Total:/)).not.toBeInTheDocument();
  });

  it('muestra los productos del carrito y el total', () => {
    render(<Cart cart={cartItems} onRemove={mockOnRemove} />);
    
    expect(screen.getByText(/Camisa - \$25.99/)).toBeInTheDocument();
    expect(screen.getByText(/Zapatos - \$40.00/)).toBeInTheDocument();
    expect(screen.getByText(/Pantalón - \$35.50/)).toBeInTheDocument();
    
    expect(screen.getByText(/Total: \$101.49/)).toBeInTheDocument();
  });

  it('llama a onRemove cuando se hace clic en Quitar', () => {
    render(<Cart cart={cartItems} onRemove={mockOnRemove} />);
    
    const removeButtons = screen.getAllByText(/quitar/i);
    expect(removeButtons.length).toBe(cartItems.length);
    
    fireEvent.click(removeButtons[0]);
    expect(mockOnRemove).toHaveBeenCalledWith(cartItems[0].id);
  });

  it('muestra correctamente el formato de precios con dos decimales', () => {
    const itemsWithDecimalPrices = [
      { id: 1, title: 'Producto 1', price: 20 },
      { id: 2, title: 'Producto 2', price: 30.5 },
      { id: 3, title: 'Producto 3', price: 15.99 },
    ];
    
    render(<Cart cart={itemsWithDecimalPrices} onRemove={mockOnRemove} />);
    
    expect(screen.getByText(/Producto 1 - \$20.00/)).toBeInTheDocument();
    expect(screen.getByText(/Producto 2 - \$30.50/)).toBeInTheDocument();
    expect(screen.getByText(/Producto 3 - \$15.99/)).toBeInTheDocument();
    expect(screen.getByText(/Total: \$66.49/)).toBeInTheDocument();
  });

  it('maneja correctamente un producto con nombre largo', () => {
    const longTitle = 'Este es un nombre de producto extremadamente largo que debería mostrarse correctamente';
    const longTitleItem = [
      { id: 1, title: longTitle, price: 10.00 }
    ];
    
    render(<Cart cart={longTitleItem} onRemove={mockOnRemove} />);
    expect(screen.getByText(new RegExp(longTitle))).toBeInTheDocument();
  });

  it('muestra múltiples productos con el mismo ID pero diferentes propiedades', () => {
    const duplicateItems = [
      { id: 1, title: 'Camisa', price: 25.99 },
      { id: 1, title: 'Camisa', price: 25.99, color: 'rojo' }, // Diferente propiedad
    ];
    
    render(<Cart cart={duplicateItems} onRemove={mockOnRemove} />);
    const items = screen.getAllByText(/Camisa - \$25.99/);
    expect(items.length).toBe(2);
  });

  it('tiene el estilo correcto con borde izquierdo', () => {
    const { container } = render(<Cart cart={emptyCart} onRemove={mockOnRemove} />);
    const cartDiv = container.firstChild;
    
    expect(cartDiv).toHaveStyle('border-left: 1px solid #ddd');
    expect(cartDiv).toHaveStyle('padding-left: 1rem');
  });
});