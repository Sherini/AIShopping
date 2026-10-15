
import re
import joblib
from pathlib import Path

from backend.products import products


# --------------------------------------------------
# 1. Understand the customer's shopping request
# --------------------------------------------------

def understand_request(message: str):
    message = message.lower().strip()

    # Identify the product
    product_keywords = {
        "headphones": [
            "headphones", "headphone", "earphones", "earbuds"
        ],
        "mouse": ["mouse"],
        "t-shirt": ["t-shirt", "tshirt", "shirt"],
        "backpack": ["backpack", "bag"],
        "shoes": ["shoes", "shoe", "footwear"]
    }

    detected_product = None

    for product, keywords in product_keywords.items():
        if any(keyword in message for keyword in keywords):
            detected_product = product
            break

    # Identify customer preferences
    preferences = []

    preference_keywords = {
        "wireless": ["wireless", "cordless"],
        "comfortable": ["comfortable", "comfy"],
        "lightweight": ["lightweight", "light weight"],
        "affordable": ["cheap", "affordable", "budget-friendly"]
    }

    for preference, keywords in preference_keywords.items():
        if any(keyword in message for keyword in keywords):
            preferences.append(preference)

    # Identify the maximum budget, including comma-separated prices
    max_price = None

    price_match = re.search(
        r"(?:under|below|less than|within|budget of)"
        r"\s*₹?\s*([\d,]+(?:\.\d+)?)",
        message
    )

    if price_match:
        max_price = float(price_match.group(1).replace(",", ""))

    return {
        "original_message": message,
        "detected_product": detected_product,
        "max_price": max_price,
        "preferences": preferences
    }


# --------------------------------------------------
# 2. Recommend products using product, budget,
#    and preference information
# --------------------------------------------------

def recommend_from_request(message: str):
    request = understand_request(message)

    detected_product = request["detected_product"]
    max_price = request["max_price"]
    preferences = request["preferences"]

    recommendations = []

    if detected_product is not None:
        for item in products:
            product_text = (
                item["name"] + " " +
                item["category"] + " " +
                item["description"]
            ).lower()

            # Check product match
            matches_product = (
                detected_product in product_text
                or (
                    detected_product == "headphones"
                    and "headphone" in product_text
                )
                or (
                    detected_product == "shoes"
                    and "shoe" in product_text
                )
                or (
                    detected_product == "t-shirt"
                    and "shirt" in product_text
                )
            )

            # Check budget
            matches_budget = (
                max_price is None
                or item["price"] <= max_price
            )

            # Check preferences against product information
            matches_preferences = True

            for preference in preferences:
                if preference == "wireless":
                    if not any(word in product_text for word in [
                        "wireless", "cordless"
                    ]):
                        matches_preferences = False

                elif preference == "comfortable":
                    if not any(word in product_text for word in [
                        "comfortable", "comfy"
                    ]):
                        matches_preferences = False

                elif preference == "lightweight":
                    if not any(word in product_text for word in [
                        "lightweight", "light weight"
                    ]):
                        matches_preferences = False

                elif preference == "affordable":
                    # An affordable request needs a stated budget
                    if max_price is None:
                        matches_preferences = False

            if (
                matches_product
                and matches_budget
                and matches_preferences
            ):
                recommendations.append(item)

    return {
        "message": message,
        "detected_product": detected_product,
        "max_price": max_price,
        "preferences": preferences,
        "total_recommendations": len(recommendations),
        "recommendations": recommendations
    }


# --------------------------------------------------
# 3. Load the saved machine-learning model
# --------------------------------------------------

model_path = Path(__file__).with_name("intent_model.joblib")
intent_model = joblib.load(model_path)


# --------------------------------------------------
# 4. Predict intent and perform the appropriate action
# --------------------------------------------------

def predict_intent(message: str):
    prediction = intent_model.predict([message])[0]

    if prediction == "browse_products":
        return {
            "message": message,
            "predicted_intent": prediction,
            "response": "Here are all the available products.",
            "products": products
        }

    elif prediction == "search_product":
        request = understand_request(message)

        return {
            "message": message,
            "predicted_intent": prediction,
            "response": "Here is the product you requested.",
            "detected_product": request["detected_product"],
            "preferences": request["preferences"]
        }

    elif prediction == "find_by_budget":
        result = recommend_from_request(message)

        return {
            "message": message,
            "predicted_intent": prediction,
            "response": "Here are the matching products.",
            "detected_product": result["detected_product"],
            "max_price": result["max_price"],
            "preferences": result["preferences"],
            "total_recommendations": result["total_recommendations"],
            "recommendations": result["recommendations"]
        }

    return {
        "message": message,
        "predicted_intent": prediction,
        "response": (
            "Sorry, I could not understand your shopping request."
        )
    }
