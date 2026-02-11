from backend.app.models.product import Product
from backend.app.services.confirmation_state import (
    set_last_action,
    get_last_action,
    clear_last_action
)

def execute_command(command: dict, db):
    intent = command.get("intent")
    data = command.get("data", {})

    # -------------------------
    # ADD PRODUCT
    # -------------------------
    if intent == "add_product":
        title = data.get("title")
        model = data.get("model")
        price = data.get("price")

        existing = db.query(Product).filter(
            Product.title == title,
            Product.model == model
        ).first()

        if existing:
            return {
                "status": "pending",
                "intent": "update_price",
                "message": "Product already exists. Update price?",
                "data": {
                    "product_id": existing.id,
                    "new_price": price,
                    "old_price": existing.price
                }
            }

        product = Product(title=title, model=model, price=price)
        db.add(product)
        db.commit()
        db.refresh(product)

        set_last_action({
            "intent": "add_product",
            "product_id": product.id
        })

        return {
            "status": "success",
            "action": "add_product",
            "product_id": product.id
        }

    # -------------------------
    # UPDATE PRICE
    # -------------------------
    if intent == "update_price":
        product_id = data.get("product_id")
        new_price = data.get("new_price")
        old_price = data.get("old_price")

        product = db.query(Product).get(product_id)
        if not product:
            return {
                "status": "error",
                "message": "Product not found"
            }

        product.price = new_price
        db.commit()

        set_last_action({
            "intent": "update_price",
            "product_id": product_id,
            "old_price": old_price
        })

        return {
            "status": "success",
            "action": "update_price",
            "message": "Price updated successfully",
            "product_id": product_id,
            "new_price": new_price
        }

    # -------------------------
    # UNDO LAST ACTION
    # -------------------------
    if intent == "undo":
        last = get_last_action()

        if not last:
            return {
                "status": "ignored",
                "message": "Nothing to undo"
            }

        if last["intent"] == "add_product":
            db.query(Product).filter(
                Product.id == last["product_id"]
            ).delete()

        elif last["intent"] == "update_price":
            product = db.query(Product).get(last["product_id"])
            if product:
                product.price = last["old_price"]

        db.commit()
        clear_last_action()

        return {
            "status": "success",
            "message": "Last action undone"
        }

    # -------------------------
    # UNKNOWN INTENT
    # -------------------------
    return {
        "status": "ignored",
        "message": "Command not understood"
    }