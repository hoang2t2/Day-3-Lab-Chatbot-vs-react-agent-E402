"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" cho Trợ lý Tra cứu Đơn hàng & Xử lý Đổi trả.
"""

# Cơ sở dữ liệu giả lập (Mock Database) về đơn hàng. Ngày giao được tạo tương
# đối để bộ demo luôn còn ý nghĩa khi chạy vào một ngày khác.
from datetime import date, datetime, timedelta


RETURN_WINDOW_DAYS = 7
_today = date.today()

MOCK_ORDERS = {
    "HD123": {
        "order_id": "HD123",
        "customer": "Nguyễn Văn A",
        "product": "Áo sơ mi nam Oxford (Size M)",
        "status": "Đã giao hàng",
        "delivery_date": (_today - timedelta(days=2)).isoformat(),
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
        "delivery_date": (_today - timedelta(days=30)).isoformat(),
        "price": 850000
    },
    "HD234": {
        "order_id": "HD234",
        "customer": "Phạm Minh Anh",
        "product": "Balo laptop chống nước 15.6 inch",
        "status": "Đã giao hàng",
        "delivery_date": _today.isoformat(),
        "price": 790000
    },
    "HD345": {
        "order_id": "HD345",
        "customer": "Vũ Hoàng Long",
        "product": "Bàn phím cơ không dây",
        "status": "Đã giao hàng",
        "delivery_date": (_today - timedelta(days=5)).isoformat(),
        "price": 1350000
    },
    "HD567": {
        "order_id": "HD567",
        "customer": "Đỗ Ngọc Mai",
        "product": "Bình giữ nhiệt 750ml",
        "status": "Đang vận chuyển",
        "delivery_date": None,
        "price": 320000
    },
    "HD678": {
        "order_id": "HD678",
        "customer": "Bùi Quốc Huy",
        "product": "Chuột không dây ergonomic",
        "status": "Đã hủy",
        "delivery_date": None,
        "price": 680000
    }
}


def _return_eligibility(order_id: str, reason: str = "") -> tuple[bool, str]:
    """Kiểm tra điều kiện đổi trả; dùng chung cho kiểm tra và tạo phiếu."""
    clean_id = order_id.strip().upper()
    if clean_id not in MOCK_ORDERS:
        return False, f"LỖI: Không thể kiểm tra điều kiện đổi trả vì mã đơn hàng '{order_id}' không tồn tại."

    order = MOCK_ORDERS[clean_id]
    if order["status"] != "Đã giao hàng":
        return False, (
            f"TỪ CHỐI ĐỔI TRẢ: Đơn hàng '{clean_id}' hiện đang ở trạng thái "
            f"'{order['status']}'. Chỉ hỗ trợ đổi trả khi đã giao hàng thành công."
        )

    try:
        delivery_date = datetime.strptime(order["delivery_date"], "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return False, f"LỖI: Đơn hàng '{clean_id}' không có ngày giao hàng hợp lệ."

    days_since_delivery = (date.today() - delivery_date).days
    if days_since_delivery < 0 or days_since_delivery > RETURN_WINDOW_DAYS:
        return False, (
            f"TỪ CHỐI ĐỔI TRẢ: Đơn hàng '{clean_id}' giao ngày {order['delivery_date']} "
            f"({days_since_delivery} ngày trước), đã quá thời hạn {RETURN_WINDOW_DAYS} ngày quy định."
        )

    return True, (
        f"ĐỦ ĐIỀU KIỆN ĐỔI TRẢ: Đơn hàng '{clean_id}' ({order['product']}) được giao ngày "
        f"{order['delivery_date']} ({days_since_delivery} ngày trước). Lý do: "
        f"'{reason or 'Không nêu'}'. Khách hàng có thể tạo phiếu đổi trả."
    )


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
    _, message = _return_eligibility(order_id, reason)
    return message


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
    is_eligible, eligibility_message = _return_eligibility(clean_id, reason)
    if not is_eligible:
        return f"TỪ CHỐI TẠO PHIẾU: {eligibility_message}"
    
    ticket_id = f"RET-{clean_id}-{date.today():%Y%m%d}"
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
