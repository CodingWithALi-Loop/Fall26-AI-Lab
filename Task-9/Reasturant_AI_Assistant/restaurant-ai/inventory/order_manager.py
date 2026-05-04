import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from inventory.stock_manager import StockManager

class OrderManager:
    def __init__(self):
        self.stock_manager = StockManager()
        self.active_orders = {}  # session_id -> order_data
        self.completed_orders = []
        self.orders_file = Path(__file__).resolve().parent.parent / "data" / "orders.json"
        self._load_orders()

    def _load_orders(self):
        """Load completed orders from file."""
        if self.orders_file.exists():
            try:
                with open(self.orders_file, 'r') as f:
                    data = json.load(f)
                    self.completed_orders = data.get('completed_orders', [])
            except:
                self.completed_orders = []

    def _save_orders(self):
        """Save completed orders to file."""
        data = {
            'completed_orders': self.completed_orders,
            'last_updated': datetime.now().isoformat()
        }
        self.orders_file.parent.mkdir(exist_ok=True)
        with open(self.orders_file, 'w') as f:
            json.dump(data, f, indent=2)

    def start_order_session(self, session_id: str, initial_items: List[Dict]) -> Dict[str, Any]:
        """Start a new order session with initial items."""
        order_data = {
            'session_id': session_id,
            'order_id': str(uuid.uuid4())[:8].upper(),
            'items': initial_items,
            'status': 'collecting_info',
            'customer_info': {},
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }

        self.active_orders[session_id] = order_data
        return order_data

    def update_customer_info(self, session_id: str, info: Dict[str, Any]) -> bool:
        """Update customer information for an order."""
        if session_id not in self.active_orders:
            return False

        self.active_orders[session_id]['customer_info'].update(info)
        self.active_orders[session_id]['last_updated'] = datetime.now().isoformat()
        return True

    def get_order_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current order status."""
        return self.active_orders.get(session_id)

    def process_order(self, session_id: str) -> Dict[str, Any]:
        """Process and complete the order."""
        if session_id not in self.active_orders:
            return {'success': False, 'message': 'No active order found.'}

        order = self.active_orders[session_id]

        # Check stock availability
        for item in order['items']:
            current_stock = self.stock_manager.stock_for(item['item'])
            if current_stock < item['quantity']:
                return {
                    'success': False,
                    'message': f'Sorry, only {current_stock} {item["item"]} available. Order cancelled.'
                }

        # Update stock
        stock_updated = True
        for item in order['items']:
            if not self.stock_manager.update_stock(item['item'], item['quantity']):
                stock_updated = False
                break

        if not stock_updated:
            return {'success': False, 'message': 'Failed to update inventory. Order cancelled.'}

        # Mark order as completed
        order['status'] = 'completed'
        order['completed_at'] = datetime.now().isoformat()
        order['total_amount'] = self.calculate_total(order['items'])

        # Move to completed orders
        self.completed_orders.append(order)
        self._save_orders()
        del self.active_orders[session_id]

        return {
            'success': True,
            'message': f'Order #{order["order_id"]} processed successfully!',
            'order_details': order
        }

    def calculate_total(self, items: List[Dict]) -> float:
        """Calculate total amount for items."""
        total = 0
        for item in items:
            details = self.stock_manager.get_item_details(item['item'])
            if details:
                total += details['price'] * item['quantity']
        return total

    def cancel_order(self, session_id: str) -> bool:
        """Cancel an active order."""
        if session_id in self.active_orders:
            del self.active_orders[session_id]
            return True
        return False

    def get_pending_orders(self) -> List[Dict]:
        """Get all pending orders for team processing."""
        return list(self.active_orders.values())

    def get_completed_orders(self, limit: int = 10) -> List[Dict]:
        """Get recent completed orders."""
        return self.completed_orders[-limit:] if self.completed_orders else []