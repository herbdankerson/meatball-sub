# Loud Market Client Portal

This repository contains a simple Node.js website acting as a client and admin portal for **Loud Market** (`loud.market`). The site interacts with a PostgREST backend to manage products and orders.

## Features

- **Login**: users authenticate via `/api/login`. The returned token determines whether the user is an admin or client.
- **Admin panel**: view and update products. Changes are sent to `/api/products` via PATCH.
- **Client portal**: browse products, add them to a cart and place COD orders via `/api/orders`.
- **Proxy server**: requests to `/api/*` are forwarded to the PostgREST service defined by the `API_URL` environment variable.

## Setup

1. Ensure Node.js 20+ is installed.
2. Set the environment variable `API_URL` to your PostgREST endpoint. Example:
   ```bash
   export API_URL="http://localhost:3001"
   npm start
   ```
3. Open `http://localhost:3000` in your browser.

The logo file `untitled.png` is used across the pages for branding.
