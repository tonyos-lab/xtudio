# Business Requirements Document — ShopEasy E-Commerce Platform

## Executive Summary
ShopEasy is an e-commerce platform allowing small businesses to sell products online.
The platform must support product listings, shopping cart, checkout, and order management.

## 1. User Management

### 1.1 Customer Registration and Login
Customers must be able to register using email and password or via Google OAuth.
Customers must verify their email address before placing their first order.
Returning customers must be able to log in and access their order history.
Customers must be able to update their profile information including delivery addresses.

### 1.2 Merchant Accounts
Merchants must be able to register for a separate merchant account.
Merchant accounts require manual approval by platform administrators before activation.
Merchants must be able to manage their own product listings independently of other merchants.

## 2. Product Catalogue

### 2.1 Product Listings
Merchants must be able to create product listings with: title, description, price, stock quantity, and up to 5 product images.
Products must be searchable by title, category, and price range.
Products must be filterable by category, price range, and availability (in stock / out of stock).
Out-of-stock products must be displayed but not purchasable.

### 2.2 Categories
The platform must support a two-level category hierarchy (e.g. Electronics > Phones).
Merchants must be able to assign products to one or more categories.

## 3. Shopping and Checkout

### 3.1 Shopping Cart
Customers must be able to add products to a shopping cart without being logged in.
The cart must persist for 7 days for anonymous users.
When a logged-in customer adds to cart, the cart must merge with any anonymous cart.
Customers must be able to update quantities and remove items from the cart.

### 3.2 Checkout
Customers must be able to check out as a guest or logged-in user.
The checkout process must collect: delivery address, contact details, and payment information.
The platform must integrate with Stripe for payment processing.
Customers must receive an order confirmation email immediately after purchase.

### 3.3 Stock Management
Stock quantity must be decremented immediately on successful payment.
If a product sells out between cart and checkout, the customer must be notified and the item removed from their cart.

## 4. Order Management

### 4.1 Customer Orders
Customers must be able to view their full order history.
Each order must show: items, quantities, prices, status, and estimated delivery date.
Customers must be able to cancel an order within 1 hour of placing it.

### 4.2 Merchant Order Fulfilment
Merchants must be notified by email when a new order is placed for their products.
Merchants must be able to update order status: Processing, Shipped, Delivered.
Merchants must be able to enter a tracking number when marking an order as Shipped.

## 5. Non-Functional Requirements

### 5.1 Performance
Product search results must return within 500ms for up to 200 concurrent users.
The checkout process must complete within 3 seconds (excluding payment gateway response time).

### 5.2 Security
All payment data must be handled by Stripe — no card details stored on platform servers.
All user passwords must be hashed using bcrypt.
All API endpoints must be protected against SQL injection and XSS attacks.

### 5.3 Availability
The platform must achieve 99.5% uptime, excluding scheduled maintenance windows.

## 6. Technical Requirements

### 6.1 Backend
Django 5.1 with PostgreSQL 15+ database.
Celery with Redis for async tasks (order confirmation emails, merchant notifications).
AWS S3 for product image storage.

### 6.2 Frontend
Server-rendered Django templates with HTMX for dynamic interactions.
Responsive design supporting mobile (320px+), tablet (768px+), and desktop (1024px+).

### 6.3 Infrastructure
Deployable to AWS EC2 with RDS PostgreSQL.
Static files served via CloudFront CDN.
