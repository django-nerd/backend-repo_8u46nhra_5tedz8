import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order, OrderItem

app = FastAPI(title="Frezee Outlet API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductResponse(Product):
    id: str


class OrderResponse(Order):
    id: str


@app.get("/")
def read_root():
    return {"message": "Frezee Outlet API running"}


@app.get("/api/products", response_model=List[ProductResponse])
def list_products():
    try:
        products = get_documents("product")
        # Convert _id to id str
        formatted = []
        for p in products:
            p["id"] = str(p.get("_id"))
            p.pop("_id", None)
            formatted.append(p)
        return formatted
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/products", response_model=str)
def create_product(product: Product):
    try:
        new_id = create_document("product", product)
        return new_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address: str
    items: List[OrderItem]
    notes: Optional[str] = None


@app.post("/api/orders", response_model=str)
def create_order(order: OrderCreate):
    try:
        # Calculate total
        total = sum(item.price * item.quantity for item in order.items)
        order_doc = Order(
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            customer_phone=order.customer_phone,
            shipping_address=order.shipping_address,
            items=order.items,
            notes=order.notes,
            total_amount=total,
        )
        new_id = create_document("order", order_doc)
        return new_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
