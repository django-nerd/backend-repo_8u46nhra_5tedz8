"""
Database Schemas for Frezee Outlet

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercase of the class name (e.g., Product -> "product").
"""

from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product"
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in BRL")
    category: str = Field(..., description="Product category")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    in_stock: bool = Field(True, description="Whether product is available")
    rating: float = Field(0, ge=0, le=5, description="Average rating 0-5")


class OrderItem(BaseModel):
    product_id: str
    title: str
    price: float
    quantity: int = Field(1, ge=1)
    image: Optional[str] = None


class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    customer_name: str
    customer_email: EmailStr
    customer_phone: Optional[str] = None
    shipping_address: str
    items: List[OrderItem]
    notes: Optional[str] = None
    total_amount: float = Field(..., ge=0)
