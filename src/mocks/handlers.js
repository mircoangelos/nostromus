import { rest } from 'msw';

export const handlers = [
  rest.get('https://fakestoreapi.com/products', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: 1, title: 'Camisa', price: 25.99 },
        { id: 2, title: 'Pantalón', price: 40.00 },
      ])
    );
  }),
];