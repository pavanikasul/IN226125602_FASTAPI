from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field,EmailStr
from typing import Optional
from typing import List


app=FastAPI()

orders={}
class Order(BaseModel):
    items:List[int]

class ProductPrice(BaseModel):
    name:str
    price:float

feedback_list=[]

class Feedback(BaseModel):
    customer_name:str=Field(..., min_length=2, max_length=15)
    product_id:int
    rating:int=Field(...,le=5, ge=0, description="Product ID must be between 0 and 5")
    comment:Optional[str]=None

class Product(BaseModel):
    name:str
    price:int

class SummaryResponse(BaseModel):
    total_products: int
    in_stock_count: int
    out_of_stock_count: int
    most_expensive: Product
    cheapest: Product
    categories: List[str]

class OrderItem(BaseModel):
    product_id: int=Field(...,gt=0)
    quantity: int=Field(...,gt=1, le=50)


class BulkOrder(BaseModel):
    company_name: str=Field(..., min_length=2, max_length=100)
    items: List[OrderItem]
    contact_email: EmailStr







products = {
    1:{"name":"Laptop","price":50000,"category":"Electronics","in_stock":True},
    2:{"name":"Wireless Mouse","price":400,"category":"Electronics","in_stock":False},
    3:{"name":"XYZ","price":1500,"category":"Electronics","in_stock":True},
    4:{"name":"Monitor","price":12000,"category":"Electronics","in_stock":True},
    5:{"name":"Laptop Stand","price":1500,"category":"Stationary","in_stock":True},
    6:{"name":"Mechanical Keyboard","price":3500,"category":"Furniture","in_stock":True},
    7:{"name":"XYZ","price":2000,"category":"Furniture","in_stock":False}
}

#Question: 1
@app.get("/products/filter")
def filter_products(min_price: int = None, max_price: int = None, category: str = None):
    filtered_products = products
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]
    if category is not None:
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]

    return {"products": filtered_products, "total": len(filtered_products)}

#Question:2
@app.get("/products/{product_id}", response_model=ProductPrice)
def get_product(product_id: int):
    product = products.get(product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "name": product["name"],
        "price": product["price"]
    }

#Question: 3
@app.post("/feedback")
def add_feedback(feedback: Feedback):
    feedback_list.append(feedback)

    return {
        "message": "Feedback submitted successfully",
        "feedback":{
        "customer_name": feedback.customer_name,
        "product_id": feedback.product_id,
        "rating": feedback.rating,
        "comment": feedback.comment,
        "total_feedbacks": len(feedback_list)
        }
        }

#Question: 4
@app.get("/dashboard/summary", response_model=SummaryResponse)
def product_summary_dashboard():

    total_products = len(products)

    in_stock_count = sum(1 for p in products.values() if p["in_stock"])
    out_of_stock_count = sum(1 for p in products.values() if not p["in_stock"])

    most_expensive = max(products.values(), key=lambda x: x["price"])
    cheapest = min(products.values(), key=lambda x: x["price"])

    categories = list(set(p["category"] for p in products.values()))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }

#Question: 5
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    total_bill = 0

    for item in order.items:

        product = products.get(item.product_id)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity
        total_bill += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "total_bill": total_bill
    }

# Bonus
@app.post("/orders")
def create_order(order: Order):
    order_id = len(orders) + 1
    orders[order_id] = {
        "id": order_id,
        "items": order.items,
        "status": "pending"
    }

    return orders[order_id]

@app.get("/orders/{order_id}")
def get_order(order_id: int):

    order = orders.get(order_id)

    if not order:
        return {"error": "order not found"}

    return order

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    order = orders.get(order_id)

    if not order:
        return {"error": "order not found"}

    order["status"] = "confirmed"

    return {
        "message": "order confirmed",
        "order": order
    }