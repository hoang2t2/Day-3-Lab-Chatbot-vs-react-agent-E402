import io
import os
import sys
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import run_react_agent
from providers import MockProvider
from tools import check_return_eligibility, create_return_ticket


class DemoDataFlowTests(unittest.TestCase):
    def test_demo_return_eligibility(self):
        self.assertIn("ĐỦ ĐIỀU KIỆN", check_return_eligibility("HD123", "Áo bị rộng"))
        self.assertIn("ĐỦ ĐIỀU KIỆN", check_return_eligibility("HD345", "Không phù hợp"))
        self.assertIn("TỪ CHỐI", check_return_eligibility("HD456", "Không cần"))
        self.assertIn("TỪ CHỐI", check_return_eligibility("HD567", "Không cần"))
        self.assertIn("TỪ CHỐI", check_return_eligibility("HD789", "Quá hạn"))

    def test_ticket_cannot_be_created_for_ineligible_order(self):
        self.assertIn("TỪ CHỐI TẠO PHIẾU", create_return_ticket("HD456"))
        self.assertIn("TỪ CHỐI TẠO PHIẾU", create_return_ticket("HD789"))

    def test_return_request_creates_ticket_in_mock_flow(self):
        output = io.StringIO()
        with redirect_stdout(output):
            response = run_react_agent(
                "Đơn hàng HD123 của tôi bị rộng size, hãy kiểm tra và tạo phiếu đổi giúp tôi.",
                MockProvider(),
            )
        trace = output.getvalue()
        self.assertIn("check_return_eligibility[HD123", trace)
        self.assertIn("create_return_ticket[HD123", trace)
        self.assertIn("TẠO PHIẾU ĐỔI TRẢ THÀNH CÔNG", response)

    def test_unknown_order_returns_a_final_answer(self):
        output = io.StringIO()
        with redirect_stdout(output):
            response = run_react_agent("Tôi muốn đổi trả đơn HD99999.", MockProvider())
        self.assertIn("không tìm thấy", response.lower())
        self.assertNotIn("GUARDRAIL TRIGGERED", output.getvalue())

    def test_ineligible_demo_order_does_not_create_ticket(self):
        output = io.StringIO()
        with redirect_stdout(output):
            response = run_react_agent("Tôi muốn đổi trả đơn HD567.", MockProvider())
        self.assertIn("không đủ điều kiện", response.lower())
        self.assertNotIn("create_return_ticket", output.getvalue())


if __name__ == "__main__":
    unittest.main()
