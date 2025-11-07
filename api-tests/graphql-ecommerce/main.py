"""
GraphQL API - E-commerce Store
Built by SuperAgent - Production-Ready GraphQL API
"""
from typing import List, Optional
from datetime import datetime
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# In-memory databases
products_db = {}
orders_db = {}
product_counter = 0
order_counter = 0

# GraphQL Types
@strawberry.type
class Product:
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None
    created_at: str

@strawberry.type
class OrderItem:
    product_id: int
    product_name: str
    quantity: int
    price: float

@strawberry.type
class Order:
    id: int
    customer_name: str
    customer_email: str
    items: List[OrderItem]
    total: float
    status: str
    created_at: str

@strawberry.type
class ProductResponse:
    success: bool
    message: str
    product: Optional[Product] = None

@strawberry.type
class OrderResponse:
    success: bool
    message: str
    order: Optional[Order] = None

# Input Types
@strawberry.input
class ProductInput:
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None

@strawberry.input
class OrderItemInput:
    product_id: int
    quantity: int

@strawberry.input
class OrderInput:
    customer_name: str
    customer_email: str
    items: List[OrderItemInput]

# Queries
@strawberry.type
class Query:
    @strawberry.field
    def products(self, category: Optional[str] = None) -> List[Product]:
        """Get all products, optionally filtered by category"""
        all_products = list(products_db.values())
        if category:
            return [p for p in all_products if p.category.lower() == category.lower()]
        return all_products
    
    @strawberry.field
    def product(self, id: int) -> Optional[Product]:
        """Get a specific product by ID"""
        return products_db.get(id)
    
    @strawberry.field
    def orders(self) -> List[Order]:
        """Get all orders"""
        return list(orders_db.values())
    
    @strawberry.field
    def order(self, id: int) -> Optional[Order]:
        """Get a specific order by ID"""
        return orders_db.get(id)
    
    @strawberry.field
    def categories(self) -> List[str]:
        """Get all unique product categories"""
        return list(set(p.category for p in products_db.values()))

# Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_product(self, product: ProductInput) -> ProductResponse:
        """Create a new product"""
        global product_counter
        product_counter += 1
        
        new_product = Product(
            id=product_counter,
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            category=product.category,
            image_url=product.image_url,
            created_at=datetime.utcnow().isoformat()
        )
        
        products_db[product_counter] = new_product
        
        return ProductResponse(
            success=True,
            message=f"Product '{product.name}' created successfully",
            product=new_product
        )
    
    @strawberry.mutation
    def update_product(self, id: int, product: ProductInput) -> ProductResponse:
        """Update an existing product"""
        if id not in products_db:
            return ProductResponse(
                success=False,
                message=f"Product with ID {id} not found",
                product=None
            )
        
        existing = products_db[id]
        updated_product = Product(
            id=id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            category=product.category,
            image_url=product.image_url,
            created_at=existing.created_at
        )
        
        products_db[id] = updated_product
        
        return ProductResponse(
            success=True,
            message=f"Product '{product.name}' updated successfully",
            product=updated_product
        )
    
    @strawberry.mutation
    def delete_product(self, id: int) -> ProductResponse:
        """Delete a product"""
        if id not in products_db:
            return ProductResponse(
                success=False,
                message=f"Product with ID {id} not found",
                product=None
            )
        
        deleted_product = products_db[id]
        del products_db[id]
        
        return ProductResponse(
            success=True,
            message=f"Product '{deleted_product.name}' deleted successfully",
            product=deleted_product
        )
    
    @strawberry.mutation
    def create_order(self, order: OrderInput) -> OrderResponse:
        """Create a new order"""
        global order_counter
        order_counter += 1
        
        # Calculate order items and total
        order_items = []
        total = 0.0
        
        for item_input in order.items:
            product = products_db.get(item_input.product_id)
            if not product:
                return OrderResponse(
                    success=False,
                    message=f"Product with ID {item_input.product_id} not found",
                    order=None
                )
            
            if product.stock < item_input.quantity:
                return OrderResponse(
                    success=False,
                    message=f"Insufficient stock for product '{product.name}'",
                    order=None
                )
            
            item_total = product.price * item_input.quantity
            total += item_total
            
            order_items.append(OrderItem(
                product_id=product.id,
                product_name=product.name,
                quantity=item_input.quantity,
                price=product.price
            ))
            
            # Update stock
            product.stock -= item_input.quantity
        
        new_order = Order(
            id=order_counter,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            items=order_items,
            total=total,
            status="pending",
            created_at=datetime.utcnow().isoformat()
        )
        
        orders_db[order_counter] = new_order
        
        return OrderResponse(
            success=True,
            message=f"Order #{order_counter} created successfully",
            order=new_order
        )
    
    @strawberry.mutation
    def update_order_status(self, id: int, status: str) -> OrderResponse:
        """Update order status (pending, processing, shipped, delivered, cancelled)"""
        if id not in orders_db:
            return OrderResponse(
                success=False,
                message=f"Order with ID {id} not found",
                order=None
            )
        
        order = orders_db[id]
        order.status = status
        
        return OrderResponse(
            success=True,
            message=f"Order #{id} status updated to '{status}'",
            order=order
        )

# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create FastAPI app
app = FastAPI(
    title="GraphQL API - E-commerce Store",
    description="Production-ready GraphQL API built by SuperAgent",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GraphQL route
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# REST endpoint for info
@app.get("/")
async def root():
    return {
        "message": "GraphQL API - E-commerce Store",
        "version": "1.0.0",
        "built_by": "SuperAgent",
        "graphql_endpoint": "/graphql",
        "graphql_playground": "/graphql (GET request)",
        "features": {
            "products": "CRUD operations for products",
            "orders": "Order management with inventory tracking",
            "categories": "Product categorization"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "products": len(products_db),
        "orders": len(orders_db)
    }

# Seed some sample data
def seed_data():
    global product_counter
    
    sample_products = [
        {"name": "Laptop", "description": "High-performance laptop", "price": 999.99, "stock": 10, "category": "Electronics"},
        {"name": "Smartphone", "description": "Latest smartphone", "price": 699.99, "stock": 25, "category": "Electronics"},
        {"name": "Headphones", "description": "Wireless headphones", "price": 149.99, "stock": 50, "category": "Electronics"},
        {"name": "T-Shirt", "description": "Cotton t-shirt", "price": 19.99, "stock": 100, "category": "Clothing"},
        {"name": "Jeans", "description": "Denim jeans", "price": 49.99, "stock": 75, "category": "Clothing"},
    ]
    
    for p in sample_products:
        product_counter += 1
        products_db[product_counter] = Product(
            id=product_counter,
            name=p["name"],
            description=p["description"],
            price=p["price"],
            stock=p["stock"],
            category=p["category"],
            created_at=datetime.utcnow().isoformat()
        )

if __name__ == "__main__":
    seed_data()
    print("🚀 Starting GraphQL API - E-commerce Store")
    print("📚 GraphQL Playground: http://localhost:8002/graphql")
    print("🏥 Health Check: http://localhost:8002/health")
    print(f"📦 Seeded {len(products_db)} sample products")
    uvicorn.run(app, host="0.0.0.0", port=8002)
