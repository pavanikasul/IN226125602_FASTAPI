from fastapi import FastAPI

app = FastAPI()

products = [
    {"id":1,"name":"Laptop","price":50000,"category":"Electronics","in_stock":True},
    {"id":2,"name":"Mouse","price":500,"category":"Electronics","in_stock":False},
    {"id":3,"name":"XYZ","price":1500,"category":"Electronics","in_stock":True},
    {"id":4,"name":"Monitor","price":12000,"category":"Electronics","in_stock":True},
    {"id":5,"name":"Laptop Stand","price":1500,"category":"Stationary","in_stock":True},
    {"id":6,"name":"Mechanical Keyboard","price":3500,"category":"Furniture","in_stock":True},
    {"id":7,"name":"XYZ","price":2000,"category":"Furniture","in_stock":False}
]


# Question: 1
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


#Question: 2
@app.get("/products/category/{category}")
def get_products_by_category(category: str):
    result = []

    for product in products:
        if product["category"].lower() == category.lower():
            result.append(product)

    return {"products": result}


#Qyestion: 3
@app.get("/products/instock")
def get_instock_products():
    result = []

    for product in products:
        if product["in_stock"] == True:
            result.append(product)

    return {
        "products": result,
        "count":len(result)
        }


#Question: 4
@app.get("/store/summary")
def store_summary():
    total_products = len(products)

    instock = 0
    outstock = 0
    categories={}

    for product in products:
        if product["in_stock"]:
            instock += 1
        else:
            outstock += 1

        cat=product["category"]
        if cat not in categories:
            categories[cat]=0
        categories[cat]+=1

    return {
        "total_products": total_products,
        "in_stock": instock,
        "out_of_stock": outstock,
        "category":categories
    }



#Question: 5
@app.get("/products/search/{name}")
def search_products(name: str):
    result = []

    for product in products:
        if name.lower() in product["name"].lower():
            result.append(product)

    return {"products": result, "count": len(result)}


#Cheapest and Most-Expensive Products
@app.get("/products/price-summary")
def price_summary():
    cheapest = min(products, key=lambda x: x["price"])
    expensive = max(products, key=lambda x: x["price"])

    return {
        "cheapest_product": cheapest,
        "most_expensive_product": expensive
    }