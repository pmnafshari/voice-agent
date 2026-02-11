import re

def parse_command(text: str) -> dict:
    text_lower = text.lower().strip()

    # -------- CONFIRMATION (MUST BE FIRST) --------
    if any(word in text_lower for word in ["yes", "confirm", "ok", "okay", "بله", "تایید"]):
        return {
            "intent": "confirm"
        }
     # -------- Undo --------
    if any(word in text_lower for word in ["undo", "cancel", "revert", "برگرد"]):
        return {"intent": "undo"}
    # -------- INTENT --------
    if "add" in text_lower or "اضافه" in text_lower:
        intent = "add_product"
    elif "remove" in text_lower or "delete" in text_lower or "حذف" in text_lower:
        intent = "remove_product"
    elif "update" in text_lower or "change" in text_lower or "ویرایش" in text_lower:
        intent = "update_product"
    else:
        return {
            "intent": "unknown",
            "message": "Command not understood"
        }

    # -------- PRICE --------
    price_match = re.search(r"(\d+)", text)
    price = int(price_match.group(1)) if price_match else None

    # -------- MODEL --------
    model_match = re.search(r"model\s*([a-zA-Z0-9]+)", text, re.IGNORECASE)
    model = model_match.group(1) if model_match else None

    # -------- TITLE --------
    title = None
    words = text_lower.split()
    if len(words) >= 2:
        title = words[1]

    return {
        "intent": intent,
        "data": {
            "title": title,
            "model": model,
            "price": price
        }
    }