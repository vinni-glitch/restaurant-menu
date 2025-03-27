from collections import Counter
from models import db, Order, MenuItem
import json

class MenuRecommendation:
    def __init__(self):
        self.orders = Counter()

    def record_order(self, menu_item):
        """
        Records the ordered menu item.
        :param menu_item: Name of the ordered menu item
        """
        self.orders[menu_item] += 1

    def get_popular_items(self):
        """Fetch top 3 most popular menu items based on order frequency."""
        orders = Order.query.with_entities(Order.menu_item_id).all()

        if not orders:
            return [("Chef's Special Dish", 1), ("House Pasta", 1), ("Signature Burger", 1)]  # Default recommendations

        menu_counts = Counter(order[0] for order in orders)
        most_ordered_ids = [menu_id for menu_id, _ in menu_counts.most_common(3)]

        popular_items = []
        for menu_id in most_ordered_ids:
            item = MenuItem.query.get(menu_id)
            if item:
                popular_items.append((item.name, menu_counts[menu_id]))

        return popular_items[:3]

    def save_order_history(self, filename="order_history.json"):
        """
        Saves order data to a JSON file.
        """
        with open(filename, "w") as file:
            json.dump(self.orders, file)

    def load_order_history(self, filename="order_history.json"):
        """
        Loads order data from a JSON file.
        """
        try:
            with open(filename, "r") as file:
                self.orders = Counter(json.load(file))
        except FileNotFoundError:
            self.orders = Counter()
