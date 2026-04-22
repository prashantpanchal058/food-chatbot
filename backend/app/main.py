from fastapi import FastAPI
import pickle
import random
import string
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# LOAD FILES
# ---------------------------
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open("data.pkl", "rb") as f:
    data = pickle.load(f)

menu = data["menu"]

responses = {}

for intent in data["intents"]:
    responses[intent["tag"]] = intent["responses"]

# ---------------------------
# STATE (simple global)
# ---------------------------
cart = []
final_order = []
last_order = []
awaiting_selection = False
awaiting_confirmation = False

# ---------------------------
# HELPERS
# ---------------------------
def clean_text(text):
    text = text.lower()
    text = ''.join([c for c in text if c not in string.punctuation])
    text = text.replace("waht", "what")
    text = text.replace("willl", "will")
    return text

def predict_intent(text):
    X = vectorizer.transform([text])
    probs = model.predict_proba(X)
    return model.classes_[probs.argmax()]

def get_items_from_numbers(text):
    items = []
    for w in text.split():
        if w in menu:
            items.append(menu[w]["name"])
    return items

def show_menu():
    return (
        "Menu:\n"
        "1. Pizza ₹199\n"
        "2. Burger ₹99\n"
        "3. Biryani ₹149\n"
        "4. Pasta ₹129\n"
        "5. Fries ₹79\n"
        "Enter item number(s)"
    )

# ---------------------------
# API
# ---------------------------
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    user_input = req.message
    global cart, final_order, last_order
    global awaiting_selection, awaiting_confirmation

    cleaned = clean_text(user_input)

    # MENU
    if "menu" in cleaned:
        awaiting_selection = True
        return {"response": show_menu()}

    # SELECT
    if awaiting_selection:
        items = get_items_from_numbers(cleaned)
        if items:
            cart = items
            awaiting_selection = False
            awaiting_confirmation = True
            return {"response": f"You selected {', '.join(cart)}. Confirm?"}
        else:
            return {"response": "Invalid selection"}

    # CONFIRM
    if awaiting_confirmation:
        if cleaned in ["yes", "ok", "confirm"]:
            final_order.extend(cart)
            cart = []
            awaiting_confirmation = False
            return {"response": "Added to order. Add more or checkout?"}

        elif cleaned in ["no", "cancel"]:
            cart = []
            awaiting_confirmation = False
            return {"response": "Cancelled. Add more or checkout?"}

    # CHECKOUT
    if "checkout" in cleaned:
        if final_order:
            order_id = "ORD" + str(random.randint(1000, 9999))
            last_order = final_order.copy()
            final_order = []
            return {
                "response": f"Order placed! ID: {order_id}"
            }
        return {"response": "No items"}

    # VIEW ORDER
    if "order" in cleaned:
        if final_order:
            return {"response": f"Current: {', '.join(final_order)}"}
        elif last_order:
            return {"response": f"Last: {', '.join(last_order)}"}
        return {"response": "No order"}

    # SPECIAL
    if "special" in cleaned:
        return {"response": "Pizza and Biryani are special 😋"}

    # TIME
    if "time" in cleaned or "when" in cleaned:
        return {"response": "Delivery in 25–30 mins 🚚"}

    # ML fallback
    intent = predict_intent(cleaned)

    if intent in responses:
        return {"response": random.choice(responses[intent])}
    else:
        return {"response": "Sorry, I didn't understand."}