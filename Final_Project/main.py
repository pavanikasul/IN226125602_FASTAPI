from fastapi import FastAPI, Query, Response, status, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# PYDANTIC MODELS
from pydantic import BaseModel, Field
class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2)
    item_id:int
    quantity:int=Field(..., gt=0, le=20)
    delivery_address: str = Field(..., min_length=10)
    order_type:str="delivery"


class NewMenuItem(BaseModel):
    name: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    is_available: bool = True

class CheckoutRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


# HELPER FUNCTIONS
# Find menu item by id
def find_menu_item(item_id: int):
    for item in menu:
        if item["id"] == item_id:
            return item
    return None
#Calculate bill
def calculate_bill(price:int, quantity:int):
    return price*quantity

#Update calculate_bill
def calculate_bill(price:int, quantity:int, order_type:str):
    total=price*quantity

    if order_type=="delivery":
        total+=30 #delivery charge

    return total

def filter_menu_logic(item, category=None, max_price=None, is_available=None):
    if category is not None and item["category"].lower() != category.lower():
        return False
    
    if max_price is not None and item["price"] > max_price:
        return False
    
    if is_available is not None and item["is_available"] != is_available:
        return False

    return True

orders=[]
order_counter=1
cart=[]

@app.get('/')
def home():
    return {'message': 'Welcome to QuickBite Food Delivery '}


menu = [
    {"id": 1, "name": "Margherita Pizza", "price": 199, "category": "Pizza", "is_available": True},
    {"id": 2, "name": "Veg Burger", "price": 99, "category": "Burger", "is_available": True},
    {"id": 3, "name": "Coke", "price": 40, "category": "Drink", "is_available": True},
    {"id": 4, "name": "Chocolate Cake", "price": 120, "category": "Dessert", "is_available": True},
    {"id": 5, "name": "Chicken Pizza", "price": 249, "category": "Pizza", "is_available": False},
    {"id": 6, "name": "French Fries", "price": 80, "category": "Snack", "is_available": True}
]

# GET /menu endpoint
@app.get("/menu")
def get_menu():
    return {
        "items": menu,
        "total": len(menu)
    }

@app.get("/menu/summary")
def menu_summary():
    total_items = len(menu)
    available=0
    unavailable=0
    categories=set()
    for item in menu:
        if item["is_available"]:
            available+=1
        else:
            unavailable+=1
        categories.add(item["category"])
    
    return {
        "total_items": total_items,
        "available": available,
        "unavailable": unavailable,
        "categories": list(categories)
    }

@app.get("/menu/filter")
def filter_menu(
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None
):
    filtered = []

    for item in menu:
        if category is not None and item["category"] != category:
            continue
        if max_price is not None and item["price"] > max_price:
            continue
        if is_available is not None and item["is_available"] != is_available:
            continue

        filtered.append(item)

    return {
        "items": filtered,
        "count": len(filtered)
    }

@app.get("/menu/search")
def search_menu(keyword: str):
    result = []

    for item in menu:
        if keyword.lower() in item["name"].lower() or keyword.lower() in item["category"].lower():
            result.append(item)

    if not result:
        return {
            "message": "No items found",
            "total_found": 0
        }

    return {
        "items": result,
        "total_found": len(result)
    }


@app.get("/menu/sort")
def sort_menu(sort_by: str = "price", order: str = "asc"):

    valid_fields = ["price", "name", "category"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort_by")

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order")

    reverse = True if order == "desc" else False

    sorted_menu = sorted(menu, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sorted_by": sort_by,
        "order": order,
        "items": sorted_menu
    }

@app.get("/menu/page")
def paginate_menu(page: int = 1, limit: int = 3):

    if page < 1 or limit < 1:
        return {"error": "Invalid page or limit"}

    start = (page - 1) * limit
    end = start + limit

    total = len(menu)
    total_pages = (total + limit - 1) // limit   # ceiling division

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "items": menu[start:end]
    }

@app.get("/menu/browse")
def browse_menu(
    keyword: str = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):

    data = menu

    #  FILTER (search)
    if keyword:
        data = [
            item for item in data
            if keyword.lower() in item["name"].lower()
            or keyword.lower() in item["category"].lower()
        ]

    #  SORT
    valid_fields = ["price", "name", "category"]
    if sort_by not in valid_fields:
        return {"error": "Invalid sort_by"}

    reverse = True if order == "desc" else False
    data = sorted(data, key=lambda x: x[sort_by], reverse=reverse)

    #  PAGINATION
    total = len(data)
    start = (page - 1) * limit
    end = start + limit
    total_pages = (total + limit - 1) // limit

    paginated_data = data[start:end]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "items": paginated_data
    }


@app.get("/menu/{item_id}")
def get_menu_item(item_id: int):
    for item in menu:
        if item["id"] == item_id:
            return item
    return {"error": "Item not found"}

@app.get("/orders/search")
def search_orders(customer_name: str):
    result = []

    for o in orders:
        if customer_name.lower() in o["customer_name"].lower():
            result.append(o)

    if not result:
        return {"message": "No orders found"}

    return {
        "orders": result,
        "count": len(result)
    }

from fastapi import HTTPException

@app.get("/orders/sort")
def sort_orders(order: str = "asc"):

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order")

    reverse = True if order == "desc" else False

    sorted_orders = sorted(orders, key=lambda x: x["total_price"], reverse=reverse)

    return {
        "order": order,
        "orders": sorted_orders
    }



@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total": len(orders)
    }

@app.post("/orders")
def create_order(order:OrderRequest):
    global order_counter

    menu_item=find_menu_item(order.item_id)
    if not menu_item:
        return {"error": "Menu item not found"}
    if not menu_item["is_available"]:
        return {"error": f"{menu_item['name']} is currently unavailable"}
    
    total_price=calculate_bill(menu_item["price"], order.quantity, order.order_type)
    new_order={
        "order_id": order_counter,
        "customer_name": order.customer_name,
        "item": menu_item["name"],
        "quantity": order.quantity,
        "delivery_address": order.delivery_address,
        "total_price": total_price,
        "status": "confirmed"
    }
    orders.append(new_order)
    order_counter+=1
    return {
        "message": "Order placed successfully",
        "order": new_order
    }


@app.post("/menu")
def add_item(item: NewMenuItem, response: Response):
    # check duplicate name (case-insensitive)
    for m in menu:
        if m["name"].lower() == item.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Item already exists"}

    new_id = max([m["id"] for m in menu]) + 1 if menu else 1

    new_item = {
        "id": new_id,
        "name": item.name,
        "price": item.price,
        "category": item.category,
        "is_available": item.is_available
    }

    menu.append(new_item)
    response.status_code = status.HTTP_201_CREATED

    return new_item

@app.put("/menu/{item_id}")
def update_item(
    item_id: int,
    price: Optional[int] = None,
    is_available: Optional[bool] = None
):
    item = find_menu_item(item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if price is not None:
        item["price"] = price

    if is_available is not None:
        item["is_available"] = is_available

    return item

@app.delete("/menu/{item_id}")
def delete_item(item_id: int):
    item = find_menu_item(item_id)

    if not item:
        return {"error": "Item not found"}

    menu.remove(item)

    return {
        "message": f"{item['name']} deleted successfully"
    }

@app.post("/cart/add")
def add_to_cart(item_id: int, quantity: int = 1):
    item = find_menu_item(item_id)

    if not item:
        return {"error": "Item not found"}

    if not item["is_available"]:
        return {"error": "Item not available"}

    # check if already in cart
    for c in cart:
        if c["item_id"] == item_id:
            c["quantity"] += quantity
            return {"message": "Cart updated", "cart": cart}

    cart.append({
        "item_id": item_id,
        "name": item["name"],
        "price": item["price"],
        "quantity": quantity
    })

    return {"message": "Item added to cart", "cart": cart}

@app.delete("/cart/{item_id}")
def remove_from_cart(item_id: int):
    for c in cart:
        if c["item_id"] == item_id:
            cart.remove(c)
            return {"message": "Item removed from cart"}

    return {"error": "Item not in cart"}



@app.post("/cart/checkout")
def checkout(data: CheckoutRequest, response: Response):
    global order_counter

    if not cart:
        return {"error": "Cart is empty"}

    placed_orders = []
    grand_total = 0

    for c in cart:
        total_price = c["price"] * c["quantity"]

        order = {
            "order_id": order_counter,
            "customer_name": data.customer_name,
            "item_name": c["name"],
            "quantity": c["quantity"],
            "total_price": total_price,
            "delivery_address": data.delivery_address
        }

        orders.append(order)
        placed_orders.append(order)

        order_counter += 1
        grand_total += total_price

    cart.clear()
    response.status_code = status.HTTP_201_CREATED

    return {
        "orders": placed_orders,
        "grand_total": grand_total
    }



