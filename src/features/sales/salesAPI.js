import axios from 'axios';

const API_BASE_URL = 'https://fakestoreapi.com';

export const fetchProducts = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/products`);
    return response.data;
  } catch (error) {
    console.error('Error fetching products:', error);
    throw error;
  }
};

export const fetchProductDetails = async (id) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/products/${id}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching product details:', error);
    throw error;
  }
};

export const simulatePurchase = async (cartItems) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/carts`, {
      userId: 1,
      date: new Date().toISOString(),
      products: cartItems.map(item => ({
        productId: item.id,
        quantity: item.quantity
      }))
    });
    return response.data;
  } catch (error) {
    console.error('Error simulating purchase:', error);
    throw error;
  }
};