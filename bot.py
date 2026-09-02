import os
import json
import threading
from flask import Flask
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

ORDERS_FILE = "orders.json"

# =========================================================
# PRODUCT INVENTORY
# =========================================================

INVENTORY_FILE = "inventory.json"


def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        return {}

    try:
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_inventory(inventory):
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(
            inventory,
            f,
            ensure_ascii=False,
            indent=2
        )


def get_product_delivery(product_key):
    inventory = load_inventory()

    items = inventory.get(product_key, [])

    if not items:
        return None

    delivery = items.pop(0)

    inventory[product_key] = items

    save_inventory(inventory)

    return delivery
# =========================================================
# RENDER WEB SERVER
# =========================================================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "FSH SHOP Bot is running!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


# =========================================================
# PRODUCTS
# =========================================================

PRODUCTS = {
    "capcut_1": {
        "product": "🎬 CapCut",
        "plan": "১ মাস",
        "price": "৪০০ টাকা",
        "info_type": "inventory",
    },
    "capcut_6": {
        "product": "🎬 CapCut",
        "plan": "৬ মাস",
        "price": "২০৮০ টাকা",
        "info_type": "inventory",
    },

    "canva_6": {
        "product": "🎨 Canva",
        "plan": "৬ মাস (AI ছাড়া)",
        "price": "৫৯ টাকা",
        "info_type": "email",
    },
    "canva_1_no_ai": {
        "product": "🎨 Canva",
        "plan": "১ বছর (AI ছাড়া)",
        "price": "৯০ টাকা",
        "info_type": "email",
    },
    "canva_1_ai": {
        "product": "🎨 Canva",
        "plan": "১ বছর (AI সহ)",
        "price": "২৮০ টাকা",
        "info_type": "inventory",
    },

    "google_6": {
        "product": "🤖 Google AI Pro",
        "plan": "৬ মাস",
        "price": "৫৫০ টাকা",
        "info_type": "email",
    },
    "google_no_warranty": {
        "product": "🤖 Google AI Pro",
        "plan": "No Warranty",
        "price": "২২০ টাকা",
        "info_type": "email",
    },

    "virtual_3": {
        "product": "💳 Virtual Card",
        "plan": "৩ বছর",
        "price": "৯৫০ টাকা",
        "info_type": "inventory",
    },

    "fb_1000": {
        "product": "👥 Facebook Follower",
        "plan": "প্রতি ১,০০০ Follower",
        "price": "১৬০ টাকা",
        "info_type": "facebook",
    },
}


# =========================================================
# PAYMENT METHODS
# =========================================================

PAYMENTS = {
    "bkash": {
        "name": "Bkash",
        "type": "Personal",
        "number": "01985821381",
    },
    "nagad": {
        "name": "Nagad",
        "type": "Personal",
        "number": "01985821381",
    },
    "rocket": {
        "name": "Rocket",
        "type": "Personal",
        "number": "01540739640",
    },
    "binance": {
        "name": "Binance",
        "type": "Personal",
        "number": "175373847",
    },
}


# =========================================================
# ORDER DATABASE
# =========================================================

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return {}

    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_orders(orders):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            orders,
            f,
            ensure_ascii=False,
            indent=2
        )


def create_order_id():
    orders = load_orders()

    highest = 1000

    for order_id in orders:
        try:
            number = int(order_id.replace("FSH-", ""))
            highest = max(highest, number)
        except:
            pass

    return f"FSH-{highest + 1}"


# =========================================================
# MAIN MENU
# =========================================================

def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🛍️ Prodact",
                callback_data="products"
            )
        ],
        [
            InlineKeyboardButton(
                "💳 Payment",
                callback_data="payment"
            ),
            InlineKeyboardButton(
                "📞 Support",
                callback_data="support"
            )
        ],
        [
            InlineKeyboardButton(
                "👤 My Profile",
                callback_data="my_info"
            )
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    user = update.effective_user

    await update.message.reply_text(
        f"👋 স্বাগতম {user.first_name}!\n\n"
        "FSH SHOP-এ আপনাকে স্বাগতম।\n\n"
        "নিচের মেনু থেকে একটি অপশন নির্বাচন করুন:",
        reply_markup=main_menu()
    )


# =========================================================
# PRODUCTS MENU
# =========================================================

async def show_products(query):

    keyboard = [
        [
            InlineKeyboardButton(
                "🎬 CapCut",
                callback_data="product_capcut"
            )
        ],
        [
            InlineKeyboardButton(
                "🎨 Canva",
                callback_data="product_canva"
            )
        ],
        [
            InlineKeyboardButton(
                "🤖 Google AI Pro",
                callback_data="product_google"
            )
        ],
        [
            InlineKeyboardButton(
                "💳 Virtual Card",
                callback_data="product_virtual"
            )
        ],
        [
            InlineKeyboardButton(
                "👥 Facebook Follower",
                callback_data="product_facebook"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 মূল মেনু",
                callback_data="main_menu"
            )
        ],
    ]

    await query.edit_message_text(
        "🛍️ FSH SHOP Products\n\n"
        "আপনার প্রয়োজনীয় Product নির্বাচন করুন:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# PLAN MENUS
# =========================================================

async def capcut_plans(query):

    keyboard = [
        [
            InlineKeyboardButton(
                "১ মাস — ৪০০ টাকা",
                callback_data="plan_capcut_1"
            )
        ],
        [
            InlineKeyboardButton(
                "৬ মাস — ২০৮০ টাকা",
                callback_data="plan_capcut_6"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 প্রোডাক্ট",
                callback_data="products"
            )
        ],
    ]

    await query.edit_message_text(
        "🎬 CapCut\n\n"
        "আপনার Plan নির্বাচন করুন:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def canva_plans(query):

    keyboard = [
        [
            InlineKeyboardButton(
                "৬ মাস — ৫৯ টাকা (AI ছাড়া)",
                callback_data="plan_canva_6"
            )
        ],
        [
            InlineKeyboardButton(
                "১ বছর — ৯০ টাকা (AI ছাড়া)",
                callback_data="plan_canva_1_no_ai"
            )
        ],
        [
            InlineKeyboardButton(
                "১ বছর — ২৮০ টাকা (AI সহ)",
                callback_data="plan_canva_1_ai"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 প্রোডাক্ট",
                callback_data="products"
            )
        ],
    ]

    await query.edit_message_text(
        "🎨 Canva\n\n"
        "আপনার Plan নির্বাচন করুন:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def google_plans(query):

    keyboard = [
        [
            InlineKeyboardButton(
                "৬ মাস — ৫৫০ টাকা",
                callback_data="plan_google_6"
            )
        ],
        [
            InlineKeyboardButton(
                "No Warranty — ২২০ টাকা",
                callback_data="plan_google_no_warranty"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 প্রোডাক্ট",
                callback_data="products"
            )
        ],
    ]

    await query.edit_message_text(
        "🤖 Google AI Pro\n\n"
        "আপনার Plan নির্বাচন করুন:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def virtual_plans(query):

    keyboard = [
        [
            InlineKeyboardButton(
                "৩ বছর — ৯৫০ টাকা",
                callback_data="plan_virtual_3"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 প্রোডাক্ট",
                callback_data="products"
            )
        ],
    ]

    await query.edit_message_text(
        "💳 Virtual Card\n\n"
        "Plan নির্বাচন করুন:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def facebook_plans(query):

    keyboard = [
        [
            InlineKeyboardButton(
                "১,০০০ Follower — ১৬০ টাকা",
                callback_data="plan_fb_1000"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 প্রোডাক্ট",
                callback_data="products"
            )
        ],
    ]

    await query.edit_message_text(
        "👥 Facebook Follower\n\n"
        "Package নির্বাচন করুন:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# PLAN SELECTED
# =========================================================

async def selected_plan(query, context, product_key):

    product = PRODUCTS[product_key]

    context.user_data["selected_product"] = product_key

    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 অর্ডার করুন",
                callback_data="start_order"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 প্রোডাক্ট",
                callback_data="products"
            )
        ],
    ]

    await query.edit_message_text(
        f"{product['product']}\n\n"
        f"📅 Plan: {product['plan']}\n"
        f"💰 Price: {product['price']}\n\n"
        "অর্ডার করতে নিচের বাটনে চাপুন:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# START ORDER
# =========================================================

async def start_order(query, context):

    product_key = context.user_data.get("selected_product")

    if not product_key:
        await query.edit_message_text(
            "❌ Product পাওয়া যায়নি। আবার চেষ্টা করুন।"
        )
        return

    product = PRODUCTS[product_key]

    keyboard = [
        [
            InlineKeyboardButton(
                "💚 Bkash",
                callback_data="order_pay_bkash"
            )
        ],
        [
            InlineKeyboardButton(
                "🟠 Nagad",
                callback_data="order_pay_nagad"
            )
        ],
        [
            InlineKeyboardButton(
                "🔴 Rocket",
                callback_data="order_pay_rocket"
            )
        ],
        [
            InlineKeyboardButton(
                "🟡 Binance",
                callback_data="order_pay_binance"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ বাতিল",
                callback_data="products"
            )
        ],
    ]

    await query.edit_message_text(
        "🛒 Order Details\n\n"
        f"📦 Product: {product['product']}\n"
        f"📅 Plan: {product['plan']}\n"
        f"💰 Price: {product['price']}\n\n"
        "Payment Method নির্বাচন করুন:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# PAYMENT
# =========================================================

async def order_payment(query, context, payment_key):

    product_key = context.user_data.get("selected_product")

    if not product_key:
        await query.edit_message_text(
            "❌ Order information পাওয়া যায়নি।"
        )
        return

    payment = PAYMENTS[payment_key]

    context.user_data["selected_payment"] = payment_key

    keyboard = [
        [
            InlineKeyboardButton(
                "✍️ Transaction ID দিন",
                callback_data="enter_transaction"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Order বাতিল",
                callback_data="products"
            )
        ],
    ]

    await query.edit_message_text(
        f"💳 {payment['name']}\n\n"
        f"Account Type: {payment['type']}\n"
        f"Number / ID: {payment['number']}\n\n"
        "Payment সম্পন্ন করার পর নিচের বাটনে চাপুন।",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def ask_transaction(query, context):

    context.user_data["waiting_transaction"] = True

    await query.edit_message_text(
        "🧾 Transaction ID দিন\n\n"
        "আপনার Payment-এর Transaction ID লিখে পাঠান।"
    )


# =========================================================
# RECEIVE TRANSACTION
# =========================================================

async def receive_transaction(update, context):

    if not context.user_data.get("waiting_transaction"):
        return

    transaction_id = update.message.text.strip()

    product_key = context.user_data.get("selected_product")
    payment_key = context.user_data.get("selected_payment")

    if not product_key or not payment_key:
        await update.message.reply_text(
            "❌ Order information পাওয়া যায়নি।\n"
            "/start দিয়ে আবার চেষ্টা করুন।"
        )
        context.user_data.clear()
        return

    product = PRODUCTS[product_key]
    payment = PAYMENTS[payment_key]
    user = update.effective_user

    order_id = create_order_id()

    orders = load_orders()

    orders[order_id] = {
        "order_id": order_id,
        "user_id": user.id,
        "name": user.first_name,
        "username": user.username or "",
        "product_key": product_key,
        "product": product["product"],
        "plan": product["plan"],
        "price": product["price"],
        "payment": payment["name"],
        "transaction_id": transaction_id,
        "status": "pending",
        "customer_info": None,
        "delivery": None,
    }

    save_orders(orders)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Approve Order",
                callback_data=f"approve_{order_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Reject Order",
                callback_data=f"reject_{order_id}"
            )
        ],
    ])

    admin_text = (
        "🔔 NEW ORDER RECEIVED\n\n"
        f"🆔 Order ID: {order_id}\n\n"
        f"📦 Product: {product['product']}\n"
        f"📅 Plan: {product['plan']}\n"
        f"💰 Price: {product['price']}\n\n"
        f"💳 Payment: {payment['name']}\n"
        f"🔢 Transaction ID: {transaction_id}\n\n"
        f"👤 Customer: {user.first_name}\n"
        f"🔗 Username: @{user.username if user.username else 'নেই'}\n"
        f"🆔 Telegram ID: {user.id}"
    )

    try:

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            reply_markup=keyboard
        )

    except Exception as e:

        print("ADMIN MESSAGE ERROR:", e)

        await update.message.reply_text(
            "⚠️ Order তৈরি হয়েছে, কিন্তু Admin-এর কাছে "
            "notification পাঠানো যায়নি।"
        )

        context.user_data.clear()
        return

    await update.message.reply_text(
        "✅ Order Submitted Successfully!\n\n"
        f"🆔 Order ID: {order_id}\n"
        f"📦 {product['product']}\n"
        f"📅 {product['plan']}\n"
        f"💰 {product['price']}\n\n"
        "আপনার Order Admin-এর কাছে পাঠানো হয়েছে।"
    )

    context.user_data.clear()


# =========================================================
# ADMIN APPROVE
# =========================================================

async def approve_order(query, context, order_id):

    if query.from_user.id != ADMIN_ID:
        

        await query.answer(
            "❌ আপনি Admin নন।",
            show_alert=True
        )
        return

    orders = load_orders()

    if order_id not in orders:

        await query.edit_message_text(
            "❌ Order পাওয়া যায়নি।"
        )
        return

    order = orders[order_id]

    if order["status"] != "pending":

        await query.answer(
            "এই Order ইতোমধ্যে Process করা হয়েছে।",
            show_alert=True
        )
        return

    product = PRODUCTS[order["product_key"]]

    order["status"] = "approved"

    save_orders(orders)

    info_type = product["info_type"]

    # -----------------------------------------
    # EMAIL PRODUCTS
    # -----------------------------------------

    if info_type == "email":

        context.user_data["collect_info_for"] = order_id

        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                "✅ আপনার Order Approved!\n\n"
                f"🆔 Order ID: {order_id}\n"
                f"📦 {order['product']}\n"
                f"📅 {order['plan']}\n\n"
                "📧 এখন আপনার Gmail / Email address পাঠান।"
            )
        )

        await query.edit_message_text(
            f"✅ Order {order_id} Approved.\n\n"
            "Customer-এর Email চাওয়া হয়েছে।"
        )

    # -----------------------------------------
    # FACEBOOK
    # -----------------------------------------

    elif info_type == "facebook":

        context.user_data["collect_info_for"] = order_id

        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                "✅ আপনার Order Approved!\n\n"
                f"🆔 Order ID: {order_id}\n"
                f"📦 {order['product']}\n\n"
                "🔗 আপনার Facebook Profile/Page Link "
                "অথবা ID পাঠান।"
            )
        )

        await query.edit_message_text(
            f"✅ Order {order_id} Approved.\n\n"
            "Customer-এর Facebook Link/ID চাওয়া হয়েছে।"
        )

     # -----------------------------------------
    # AUTOMATIC INVENTORY DELIVERY
    # -----------------------------------------

    elif info_type == "inventory":

        delivery = get_product_delivery(
            order["product_key"]
        )

        # Stock না থাকলে
        if not delivery:

            order["status"] = "out_of_stock"

            save_orders(orders)

            await context.bot.send_message(
                chat_id=order["user_id"],
                text=(
                    "⚠️ আপনার Order Approved হয়েছে, "
                    "কিন্তু এই Product বর্তমানে Out of Stock.\n\n"
                    f"🆔 Order ID: {order_id}\n"
                    f"📦 {order['product']}\n"
                    f"📅 {order['plan']}\n\n"
                    "দয়া করে Admin-এর সাথে যোগাযোগ করুন।"
                )
            )

            await query.edit_message_text(
                f"⚠️ Order {order_id} Approved, "
                "কিন্তু Product Out of Stock."
            )

            return

        # Customer-কে Automatic Delivery
        try:

            await context.bot.send_message(
                chat_id=order["user_id"],
                text=(
                    "🎉 আপনার Order Successfully Delivered!\n\n"
                    f"🆔 Order ID: {order_id}\n"
                    f"📦 Product: {order['product']}\n"
                    f"📅 Plan: {order['plan']}\n\n"
                    "🔐 Delivery Information:\n\n"
                    f"{delivery}\n\n"
                    "ধন্যবাদ FSH SHOP-এর সাথে থাকার জন্য। ❤️"
                )
            )

            order["status"] = "delivered"
            order["delivery"] = delivery

            save_orders(orders)

            await query.edit_message_text(
                f"✅ Order {order_id} Approved & Delivered."
            )

        except Exception as e:

            print("AUTO DELIVERY ERROR:", e)

            await query.edit_message_text(
                f"❌ Order {order_id} Delivery Failed."
            )
