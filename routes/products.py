from fastapi import APIRouter, HTTPException
from schemas.product import Product
from redis_client.crud import save_hash, get_hash, delete_hash

routes_product = APIRouter()

fake_db = [{
  "id": "76861c6f-da53-47d2-99bf-a3d3f78fd926",
  "name": "Termo 1 litro",
  "price": 20.99,
  "date": "2024-05-18 22:59:11.319168"
}]

@routes_product.post("/create", response_model=Product)
def create(product: Product):
    try:
        # Operation DB
        fake_db.append(product.dict())

        # Operation cache
        save_hash(key=product.dict()["id"], data=product.dict())
        return product
    except Exception as e:
        return e
    
@routes_product.get("/get/{id}")
def get(id: str) : 
    try:
        # Operation cache

        data = get_hash(key=id)
        if len(data) == 0:
            # Operation DB
            product = list(filter(lambda field: field["id"] == id, fake_db))[0]

            # Operation cache
            save_hash(key=id, data=product)

            return product
        return data
    except Exception as e:
        return e
    
@routes_product.delete("/delete/{id}")
def delete(id: str):
    try:
        keys = Product.__fields__.keys()

        # Operación cache
        delete_hash(key=id, keys= keys)
        
        # Operacion DB
        product = list(filter(lambda field:field["id"] != id, fake_db))
        if len(product) != 0:
            fake_db.remove(product)
        return {
            "message":"success"
        }
    except Exception as e:
        return e
    
@routes_product.put("/edit/{id}", response_model=Product)
def edit(id: str, updated_product: Product):
    try:
        # Busca el producto en la base de datos
        product_index = next((index for index, item in enumerate(fake_db) if item["id"] == id), None)
        
        if product_index is None:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Operacion DB
        fake_db[product_index].update(updated_product.dict(exclude_unset=True))

        # Operación cache
        save_hash(key=id, data=fake_db[product_index])
        
        return fake_db[product_index]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
