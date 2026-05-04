import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from inventory.stock_manager import StockManager
from inventory.order_manager import OrderManager

class ConversationManager:
    def __init__(self):
        self.stock_manager = StockManager()
        self.order_manager = OrderManager()
        self.sessions = {}  # session_id -> conversation_state

    def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Process user message and return response."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'state': 'greeting',
                'order_items': [],
                'customer_info': {},
                'booking_info': {},
                'next_question': None
            }

        state = self.sessions[session_id]['state']

        if state == 'greeting':
            return self._handle_greeting(session_id, message)
        elif state == 'collecting_order':
            return self._handle_order_collection(session_id, message)
        elif state == 'confirming_order':
            return self._handle_order_confirmation(session_id, message)
        elif state == 'collecting_info':
            return self._handle_info_collection(session_id, message)
        elif state == 'processing_order':
            return self._handle_order_processing(session_id, message)
        elif state == 'booking':
            return self._handle_booking_flow(session_id, message)
        else:
            return self._handle_general_query(session_id, message)

    def _handle_greeting(self, session_id: str, message: str) -> Dict[str, Any]:
        """Handle initial greeting and detect if user wants to order or use quick actions."""
        message_lower = message.lower().strip()

        if self._is_menu_request(message_lower):
            return self._menu_response(session_id)

        if self._is_booking_request(message_lower):
            self.sessions[session_id]['state'] = 'booking'
            self.sessions[session_id]['booking_info'] = {}
            self.sessions[session_id]['next_question'] = 'date'
            return {
                'message': "Sure! Let's book your table. What date would you like the reservation for?",
                'state': 'booking'
            }

        if self._is_contact_request(message_lower):
            return {
                'message': "You can reach our support team at +91-98765-43210 or support@restaurant.ai. We're available 9 AM to 11 PM.",
                'state': 'greeting'
            }

        if self._is_basic_questions_request(message_lower):
            return {
                'message': "I can help with orders, restaurant timings, policies, booking a table, and the menu. Try asking: 'What are your timings?', 'I want 2 burgers', or 'Book a table'.",
                'state': 'greeting'
            }

        # Check if user is asking to order
        order_keywords = ['want', 'order', 'get', 'like', 'please', 'can i', 'i would like']
        has_order_intent = any(keyword in message_lower for keyword in order_keywords)

        if has_order_intent or self._extract_order_items(message):
            items = self._extract_order_items(message)
            if items:
                self.sessions[session_id]['order_items'] = items
                self.sessions[session_id]['state'] = 'confirming_order'
                return self._ask_order_confirmation(session_id)
            else:
                self.sessions[session_id]['state'] = 'collecting_order'
                return {
                    'message': "I'd be happy to help you order! What would you like to order today? For example: '2 burgers and 1 pizza'",
                    'state': 'collecting_order'
                }

        return self._handle_general_query(session_id, message)

    def _handle_order_collection(self, session_id: str, message: str) -> Dict[str, Any]:
        """Handle order collection after asking what they want."""
        items = self._extract_order_items(message)
        if items:
            self.sessions[session_id]['order_items'] = items
            self.sessions[session_id]['state'] = 'confirming_order'
            return self._ask_order_confirmation(session_id)
        else:
            return {
                'message': "I didn't understand your order. Could you please specify what you'd like? For example: '2 burgers and 1 pizza'",
                'state': 'collecting_order'
            }

    def _ask_order_confirmation(self, session_id: str) -> Dict[str, Any]:
        """Ask user to confirm their order."""
        items = self.sessions[session_id]['order_items']
        order_summary = self._format_order_summary(items)

        return {
            'message': f"Great! Here's your order:\n{order_summary}\n\nWould you like to proceed with this order? (yes/no)",
            'state': 'confirming_order',
            'order_summary': order_summary
        }

    def _handle_order_confirmation(self, session_id: str, message: str) -> Dict[str, Any]:
        """Handle order confirmation response."""
        message_lower = message.lower().strip()

        if message_lower in ['yes', 'y', 'yes please', 'confirm', 'proceed', 'ok']:
            # Start order session
            order_data = self.order_manager.start_order_session(session_id, self.sessions[session_id]['order_items'])
            self.sessions[session_id]['order_id'] = order_data['order_id']
            self.sessions[session_id]['state'] = 'collecting_info'
            self.sessions[session_id]['next_question'] = 'name'

            return {
                'message': f"Perfect! Your order #{order_data['order_id']} has been started. To complete your order, I need some information:\n\nWhat's your full name?",
                'state': 'collecting_info',
                'next_question': 'name'
            }
        elif message_lower in ['no', 'n', 'cancel', 'change']:
            self.sessions[session_id]['order_items'] = []
            self.sessions[session_id]['state'] = 'collecting_order'
            return {
                'message': "No problem! Let's start over. What would you like to order?",
                'state': 'collecting_order'
            }
        else:
            return {
                'message': "Please reply with 'yes' to confirm or 'no' to change your order.",
                'state': 'confirming_order'
            }

    def _handle_info_collection(self, session_id: str, message: str) -> Dict[str, Any]:
        """Collect customer information step by step."""
        customer_info = self.sessions[session_id].get('customer_info', {})
        next_question = self.sessions[session_id].get('next_question', 'name')

        if next_question == 'name':
            customer_info['name'] = message.strip()
            self.sessions[session_id]['customer_info'] = customer_info
            self.sessions[session_id]['next_question'] = 'phone'
            return {
                'message': f"Thanks {customer_info['name']}! What's your phone number for delivery updates?",
                'state': 'collecting_info',
                'next_question': 'phone'
            }

        elif next_question == 'phone':
            customer_info['phone'] = message.strip()
            self.sessions[session_id]['customer_info'] = customer_info
            self.sessions[session_id]['next_question'] = 'delivery_type'
            return {
                'message': "Got it! Would you like delivery or pickup? (delivery/pickup)",
                'state': 'collecting_info',
                'next_question': 'delivery_type'
            }

        elif next_question == 'delivery_type':
            delivery_type = message.lower().strip()
            if delivery_type in ['delivery', 'pickup']:
                customer_info['delivery_type'] = delivery_type
                self.sessions[session_id]['customer_info'] = customer_info

                if delivery_type == 'delivery':
                    self.sessions[session_id]['next_question'] = 'address'
                    return {
                        'message': "Great! What's your delivery address?",
                        'state': 'collecting_info',
                        'next_question': 'address'
                    }
                else:
                    self.sessions[session_id]['next_question'] = 'special_instructions'
                    return {
                        'message': "Perfect! Any special instructions for your order? (or 'none' if none)",
                        'state': 'collecting_info',
                        'next_question': 'special_instructions'
                    }
            else:
                return {
                    'message': "Please specify 'delivery' or 'pickup'.",
                    'state': 'collecting_info',
                    'next_question': 'delivery_type'
                }

        elif next_question == 'address':
            customer_info['address'] = message.strip()
            self.sessions[session_id]['customer_info'] = customer_info
            self.sessions[session_id]['next_question'] = 'special_instructions'
            return {
                'message': "Thanks! Any special instructions for your order? (or 'none' if none)",
                'state': 'collecting_info',
                'next_question': 'special_instructions'
            }

        elif next_question == 'special_instructions':
            customer_info['special_instructions'] = message.strip() if message.lower() != 'none' else ''
            self.sessions[session_id]['customer_info'] = customer_info
            self.sessions[session_id]['state'] = 'processing_order'

            # Update order manager with customer info
            self.order_manager.update_customer_info(session_id, customer_info)

            return {
                'message': "All set! Ready to process your order. Type 'confirm' to place the order or 'cancel' to stop.",
                'state': 'processing_order'
            }

        # Fallback if state tracking gets out of sync
        return {
            'message': "I need a bit more information to continue. Can you please provide your name?",
            'state': 'collecting_info',
            'next_question': 'name'
        }

    def _handle_order_processing(self, session_id: str, message: str) -> Dict[str, Any]:
        """Handle final order processing."""
        message_lower = message.lower().strip()

        if message_lower == 'confirm':
            result = self.order_manager.process_order(session_id)
            if result['success']:
                # Reset session
                self.sessions[session_id] = {'state': 'greeting', 'order_items': [], 'customer_info': {}}
                return {
                    'message': result['message'] + "\n\nYour order has been sent to our team for preparation. We'll contact you soon!\n\nWould you like to place another order? (yes/no)",
                    'state': 'greeting',
                    'order_completed': True,
                    'order_details': result.get('order_details')
                }
            else:
                return {
                    'message': result['message'],
                    'state': 'processing_order'
                }
        elif message_lower == 'cancel':
            self.order_manager.cancel_order(session_id)
            self.sessions[session_id] = {'state': 'greeting', 'order_items': [], 'customer_info': {}}
            return {
                'message': "Order cancelled. Would you like to start a new order? (yes/no)",
                'state': 'greeting'
            }
        else:
            return {
                'message': "Please type 'confirm' to place your order or 'cancel' to stop.",
                'state': 'processing_order'
            }

    def _handle_general_query(self, session_id: str, message: str) -> Dict[str, Any]:
        """Handle general questions with direct answers."""
        message_lower = message.lower()

        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return {
                'message': "Hello! Welcome to our restaurant! I'm here to help you with orders, menu details, bookings, and policies.",
                'state': 'greeting'
            }
        elif any(word in message_lower for word in ['timing', 'hours', 'open', 'close']):
            return {
                'message': self._load_text_file('timming.txt'),
                'state': 'greeting'
            }
        elif any(word in message_lower for word in ['policy', 'refund', 'cancel']):
            return {
                'message': self._load_text_file('policy.txt'),
                'state': 'greeting'
            }
        elif 'price' in message_lower:
            price_response = self._price_query_response(session_id, message)
            if price_response:
                return price_response
            return self._menu_response(session_id)
        elif any(word in message_lower for word in ['menu', 'items', 'dish']):
            return self._menu_response(session_id)
        elif any(word in message_lower for word in ['contact', 'support', 'help']):
            return {
                'message': "You can reach our support team at +91-98765-43210 or support@restaurant.ai. We're here daily from 9 AM to 11 PM.",
                'state': 'greeting'
            }
        else:
            return {
                'message': "I can help with orders, timings, policies, menu items, and table bookings. How can I assist you today?",
                'state': 'greeting'
            }

    def _menu_response(self, session_id: str) -> Dict[str, Any]:
        items = self.stock_manager.menu_df.sort_values(['category', 'item'])
        lines: list[str] = []

        for category, group in items.groupby('category', sort=False):
            lines.append(f"{category}:")
            for _, row in group.iterrows():
                lines.append(
                    f"• {row['item']} — Rs. {row['price']} ({row['stock']} available; {row['preparation_time']})"
                )
            lines.append("")

        if len(lines) > 200:
            lines = lines[:200] + ["...and more items are available. Ask for a specific category or item."]

        return {
            'message': "Here's our menu:\n" + "\n".join(lines).strip(),
            'state': 'greeting'
        }

    def _price_query_response(self, session_id: str, message: str) -> Optional[Dict[str, Any]]:
        matched_item = self.stock_manager.find_item(message)
        if not matched_item:
            return None

        details = self.stock_manager.get_item_details(matched_item)
        if not details:
            return None

        return {
            'message': (
                f"{details['item']} costs Rs. {details['price']}. "
                f"We have {details['stock']} in stock and it is prepared in about {details['preparation_time']}."
            ),
            'state': 'greeting'
        }

    def _is_menu_request(self, message_lower: str) -> bool:
        return (
            'restaurant menu' in message_lower
            or 'menu' in message_lower
            or 'see menu' in message_lower
        )

    def _is_booking_request(self, message_lower: str) -> bool:
        return 'book a table' in message_lower or 'reserve' in message_lower or 'table booking' in message_lower

    def _is_contact_request(self, message_lower: str) -> bool:
        return 'contact support' in message_lower or 'contact' in message_lower or 'support' in message_lower

    def _is_basic_questions_request(self, message_lower: str) -> bool:
        return 'basic questions' in message_lower or 'help' in message_lower

    def _load_text_file(self, file_name: str) -> str:
        file_path = Path(__file__).resolve().parent.parent / 'data' / file_name
        if not file_path.exists():
            return "Sorry, I don't have that information available right now."

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def _handle_booking_flow(self, session_id: str, message: str) -> Dict[str, Any]:
        booking_info = self.sessions[session_id].get('booking_info', {})
        next_question = self.sessions[session_id].get('next_question', 'date')
        message_text = message.strip()

        if next_question == 'date':
            booking_info['date'] = message_text
            self.sessions[session_id]['booking_info'] = booking_info
            self.sessions[session_id]['next_question'] = 'time'
            return {
                'message': 'Great! What time would you like the table reserved for?',
                'state': 'booking',
                'next_question': 'time'
            }

        if next_question == 'time':
            booking_info['time'] = message_text
            self.sessions[session_id]['booking_info'] = booking_info
            self.sessions[session_id]['next_question'] = 'party_size'
            return {
                'message': 'How many people should the reservation be for?',
                'state': 'booking',
                'next_question': 'party_size'
            }

        if next_question == 'party_size':
            booking_info['party_size'] = message_text
            self.sessions[session_id]['booking_info'] = booking_info
            self.sessions[session_id]['next_question'] = 'name'
            return {
                'message': 'Please provide a name for the reservation.',
                'state': 'booking',
                'next_question': 'name'
            }

        if next_question == 'name':
            booking_info['name'] = message_text
            self.sessions[session_id]['booking_info'] = booking_info
            self.sessions[session_id]['next_question'] = 'phone'
            return {
                'message': 'Great. What phone number can we reach you on?',
                'state': 'booking',
                'next_question': 'phone'
            }

        if next_question == 'phone':
            booking_info['phone'] = message_text
            self.sessions[session_id]['booking_info'] = booking_info
            self.sessions[session_id]['next_question'] = 'confirm'
            summary = self._format_booking_summary(booking_info)
            return {
                'message': f'Thanks! Here is your reservation summary:\n{summary}\n\nPlease reply with "yes" to confirm or "no" to cancel.',
                'state': 'booking',
                'next_question': 'confirm'
            }

        if next_question == 'confirm':
            if message_text.lower() in ['yes', 'y', 'confirm', 'sure']:
                booking_info['status'] = 'confirmed'
                self._save_booking(booking_info)
                self.sessions[session_id] = {
                    'state': 'greeting',
                    'order_items': [],
                    'customer_info': {},
                    'booking_info': {},
                    'next_question': None
                }
                return {
                    'message': 'Your table is confirmed! We look forward to seeing you. If you need anything else, just ask.',
                    'state': 'greeting'
                }
            else:
                self.sessions[session_id] = {
                    'state': 'greeting',
                    'order_items': [],
                    'customer_info': {},
                    'booking_info': {},
                    'next_question': None
                }
                return {
                    'message': 'No problem, your table booking process has been cancelled. How else may I help you?',
                    'state': 'greeting'
                }

        return {
            'message': 'I am ready to help with your table booking. When would you like the reservation?',
            'state': 'booking'
        }

    def _format_booking_summary(self, booking_info: Dict[str, str]) -> str:
        return (
            f"Date: {booking_info.get('date', 'N/A')}\n"
            f"Time: {booking_info.get('time', 'N/A')}\n"
            f"Party size: {booking_info.get('party_size', 'N/A')}\n"
            f"Name: {booking_info.get('name', 'N/A')}\n"
            f"Phone: {booking_info.get('phone', 'N/A')}"
        )

    def _save_booking(self, booking_info: Dict[str, str]) -> None:
        bookings_file = Path(__file__).resolve().parent.parent / 'data' / 'bookings.json'
        bookings_file.parent.mkdir(exist_ok=True)
        try:
            if bookings_file.exists():
                with open(bookings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'bookings': []}
            data['bookings'].append(booking_info)
            with open(bookings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _extract_order_items(self, message: str) -> List[Dict[str, Any]]:
        """Extract order items and quantities from message."""
        items = []
        message = message.lower()

        # Simple pattern matching for quantities and items
        patterns = [
            r'(\d+)\s*(pizza|pizzas)',
            r'(\d+)\s*(burger|burgers)',
            r'(\d+)\s*(fries|french fries)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                quantity = int(match[0])
                item_name = match[1]
                if self.stock_manager.item_exists(item_name):
                    items.append({
                        'item': self.stock_manager.find_item(item_name),
                        'quantity': quantity
                    })

        return items

    def _format_order_summary(self, items: List[Dict]) -> str:
        """Format order items into readable summary."""
        summary_lines = []
        total = 0

        for item in items:
            details = self.stock_manager.get_item_details(item['item'])
            if details:
                item_total = details['price'] * item['quantity']
                total += item_total
                summary_lines.append(f"• {item['quantity']}x {item['item']} - Rs. {item_total}")

        summary_lines.append(f"\n**Total: Rs. {total}**")
        return "\n".join(summary_lines)