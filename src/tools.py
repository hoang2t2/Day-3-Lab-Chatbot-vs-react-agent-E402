"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" cho Trợ lý Tra cứu Đơn hàng & Xử lý Đổi trả.
"""

# Cơ sở dữ liệu giả lập (Mock Database) về đơn hàng
MOCK_ORDERS = {
    "HD123": {
        "order_id": "HD123",
        "customer": "Nguyễn Văn A",
        "product": "Áo sơ mi nam Oxford (Size M)",
        "status": "Đã giao hàng",
        "delivery_date": "2026-07-26",  # Trong vòng 7 ngày -> Đủ điều kiện
        "price": 450000
    },
    "HD456": {
        "order_id": "HD456",
        "customer": "Trần Thị B",
        "product": "Giày Sneaker thể thao (Size 38)",
        "status": "Đang vận chuyển",
        "delivery_date": None,
        "price": 1200000
    },
    "HD789": {
        "order_id": "HD789",
        "customer": "Lê Văn C",
        "product": "Tai nghe Bluetooth Wireless",
        "status": "Đã giao hàng",
        "delivery_date": "2026-06-01",  # Đã quá 7 ngày -> Không đủ điều kiện
        "price": 850000
    }
}


def get_order_info(order_id: str) -> str:
    """
    Tra cứu thông tin chi tiết và trạng thái của đơn hàng theo Mã Đơn Hàng (Order ID).
    
    Args:
        order_id (str): Mã đơn hàng (Ví dụ: 'HD123', 'HD456', 'HD789')
        
    Returns:
        str: Chuỗi thông tin chi tiết về đơn hàng hoặc thông báo lỗi nếu không tìm thấy.
    """
    clean_id = order_id.strip().upper()
    if clean_id in MOCK_ORDERS:
        order = MOCK_ORDERS[clean_id]
        delivery = order['delivery_date'] if order['delivery_date'] else 'Chưa giao'
        return (
            f"Thông tin đơn hàng [{order['order_id']}]:\n"
            f"- Khách hàng: {order['customer']}\n"
            f"- Sản phẩm: {order['product']}\n"
            f"- Giá tiền: {order['price']:,} VNĐ\n"
            f"- Trạng thái: {order['status']}\n"
            f"- Ngày giao hàng: {delivery}"
        )
    return f"Không tìm thấy mã đơn hàng '{order_id}' trong hệ thống."


def check_return_eligibility(order_id: str, reason: str = "") -> str:
    """
    Kiểm tra xem đơn hàng có đủ điều kiện đổi trả theo quy định hay không (Chỉ hỗ trợ đổi trả trong vòng 7 ngày kể từ khi giao hàng).
    
    Args:
        order_id (str): Mã đơn hàng cần kiểm tra (Ví dụ: 'HD123')
        reason (str): Lý do xin đổi trả (Ví dụ: 'Áo bị rộng size', 'Hàng bị lỗi')
        
    Returns:
        str: Kết quả đánh giá đủ điều kiện hoặc từ chối kèm lý do cụ thể.
    """
    clean_id = order_id.strip().upper()
    if clean_id not in MOCK_ORDERS:
        return f"LỖI: Không thể kiểm tra điều kiện đổi trả vì mã đơn hàng '{order_id}' không tồn tại."
    
    order = MOCK_ORDERS[clean_id]

    if order["status"] != "Đã giao hàng":
        return f"TỪ CHỐI ĐỔI TRẢ: Đơn hàng '{clean_id}' hiện đang ở trạng thái '{order['status']}'. Chỉ hỗ trợ đổi trả khi đã giao hàng thành công."
    
    if clean_id == "HD789":
        return f"TỪ CHỐI ĐỔI TRẢ: Đơn hàng '{clean_id}' giao ngày 2026-06-01 (Đã quá thời hạn 7 ngày quy định)."
        
    return f"ĐỦ ĐIỀU KIỆN ĐỔI TRẢ: Đơn hàng '{clean_id}' ({order['product']}) được giao ngày {order['delivery_date']} (Trong vòng 7 ngày). Lý do: '{reason or 'Không nêu'}'. Khách hàng có thể tạo phiếu đổi trả."


def create_return_ticket(order_id: str, reason: str = "Đổi trả theo yêu cầu") -> str:
    """
    Tạo phiếu yêu cầu đổi trả sản phẩm chính thức trên hệ thống.
    
    Args:
        order_id (str): Mã đơn hàng cần đổi trả (Ví dụ: 'HD123')
        reason (str): Lý do đổi trả chi tiết
        
    Returns:
        str: Mã phiếu đổi trả (Return Ticket ID) và hướng dẫn gửi hàng.
    """
    clean_id = order_id.strip().upper()
    if clean_id not in MOCK_ORDERS:
        return f"LỖI: Không thể tạo phiếu đổi trả do mã đơn hàng '{order_id}' không tồn tại trên hệ thống."
    
    ticket_id = f"RET-{clean_id}-2026"
    return (
        f"TẠO PHIẾU ĐỔI TRẢ THÀNH CÔNG!\n"
        f"- Mã phiếu đổi trả: {ticket_id}\n"
        f"- Mã đơn hàng: {clean_id}\n"
        f"- Lý do: {reason}\n"
        f"- Hướng dẫn: Đóng gói sản phẩm và gửi về trung tâm hỗ trợ kèm mã phiếu {ticket_id}."
    )


# Danh sách các tool được đăng ký để ReAct Agent sử dụng
AVAILABLE_TOOLS = {
    "get_order_info": get_order_info,
    "check_return_eligibility": check_return_eligibility,
    "create_return_ticket": create_return_ticket,
}