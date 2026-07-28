"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer / Integrator)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
Chạy toàn bộ 5 Test Cases cho Trợ Lý Tra Cứu Đơn Hàng & Xử Lý Đổi Trả.
"""

import json
import os
import re
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider, MockProvider

load_dotenv()


def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    if not os.path.exists(config_path):
        config_path = "config/test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_action(text: str):
    """
    Parser linh hoạt trích xuất Action từ chuỗi phản hồi của LLM.
    Mẫu khớp: Action: tool_name[arg1, arg2] hoặc Action: tool_name["arg1", "arg2"]
    """
    pattern = r"Action:\s*([a-zA-Z0-9_]+)\[(.*?)\]"
    match = re.search(pattern, text)
    if not match:
        return None, []
    
    tool_name = match.group(1).strip()
    raw_args = match.group(2).strip()
    
    if not raw_args:
        return tool_name, []
    
    # Tach các tham số ngăn cách bởi dấu phẩy, loại bỏ ngoặc kép/đơn dư thừa
    args = [arg.strip().strip("'\"") for arg in raw_args.split(",")]
    return tool_name, args


def execute_tool(tool_name: str, args: list) -> str:
    """Gọi thực thi tool từ Tool Registry (Role 2) với khả năng bắt lỗi an toàn"""
    if tool_name not in AVAILABLE_TOOLS:
        valid_tools = list(AVAILABLE_TOOLS.keys())
        return f"LỖI: Tool '{tool_name}' không tồn tại. Các tool hợp lệ gồm: {valid_tools}"
    
    func = AVAILABLE_TOOLS[tool_name]
    try:
        if len(args) == 0:
            return func()
        elif len(args) == 1:
            return func(args[0])
        elif len(args) == 2:
            return func(args[0], args[1])
        else:
            return func(*args)
    except Exception as e:
        return f"LỖI THỰC THI TOOL '{tool_name}': {str(e)}"


def run_baseline_chatbot(user_query: str, provider):
    """Dựng Chatbot gốc (Baseline) không có công cụ."""
    print(f"\n🤖 [CHATBOT BASELINE]")
    print(f"❓ Câu hỏi: {user_query}")
    
    # Nếu là MockProvider, giả lập câu trả lời thuần LLM
    if isinstance(provider, MockProvider):
        if "hd123" in user_query.lower() or "hd99999" in user_query.lower():
            response = "Tôi không có quyền truy cập vào cơ sở dữ liệu thời gian thực nên không thể kiểm tra thông tin đơn hàng cá nhân của bạn. Vui lòng liên hệ tổng đài 1900-XXXX để được hỗ trợ."
        else:
            response = "Cửa hàng hỗ trợ đổi trả trong vòng 7 ngày kể từ khi nhận hàng cho các sản phẩm còn nguyên tem mác, chưa qua sử dụng."
    else:
        response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
        
    print(f"💬 Chatbot Phản Hồi:\n{response}")
    print("=" * 60)


def run_react_agent(user_query: str, provider):
    """
    Vòng lặp ReAct Agent Loop linh hoạt (Thought -> Action -> Observation) có phanh an toàn Guardrails.
    """
    print(f"\n🧠 [REACT AGENT]")
    print(f"❓ Câu hỏi: {user_query}")
    
    conversation_history = f"User Query: {user_query}"
    step = 0
    
    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Step {step}/{MAX_ITERATIONS} ---")
        
        # 1. Gọi LLM sinh Thought & Action (hoặc dùng Offline Simulator nếu dùng MockProvider)
        if isinstance(provider, MockProvider):
            llm_output = simulate_mock_react_step(user_query, step, conversation_history)
        else:
            llm_output = provider.generate(conversation_history, system_prompt=REACT_SYSTEM_PROMPT)
            
        print(f"{llm_output}")
        
        # 2. Kiểm tra xem LLM đã đưa ra Final Answer chưa
        if "Final Answer:" in llm_output:
            final_ans = llm_output.split("Final Answer:")[-1].strip()
            print(f"\n🎯 [HOÀN THÀNH AGENT LOOP] Đã dừng ở bước {step}.")
            break
            
        # 3. Trích xuất Action
        tool_name, args = parse_action(llm_output)
        if tool_name:
            # 4. Thực thi Tool lấy Observation
            obs = execute_tool(tool_name, args)
            print(f"👁️ Observation: {obs}")
            
            # 5. Cập nhật Observation vào bộ nhớ hội thoại cho bước lặp tiếp theo
            conversation_history += f"\n{llm_output}\nObservation: {obs}"
        else:
            # Không tìm thấy Action hợp lệ và không có Final Answer
            print("⚠️ Không tìm thấy Action hợp lệ trong output của LLM. Tiếp tục suy luận...")
            conversation_history += f"\n{llm_output}\nObservation: Hãy xuất ra đúng định dạng Action: tên_công_cụ[tham_số] hoặc Final Answer:"

    if step >= MAX_ITERATIONS and "Final Answer:" not in locals().get("llm_output", ""):
        print(f"\n🛡️ [GUARDRAIL TRIGGERED]: Đã chạm ngưỡng tối đa MAX_ITERATIONS = {MAX_ITERATIONS} bước!")
        print("🤖 Safe Fallback: Hệ thống đã tự động dừng vòng lặp để tránh treo ứng dụng. Đã gửi thông báo lịch sự tới người dùng.")
        
    print("=" * 60)


def simulate_mock_react_step(query: str, step: int, history: str) -> str:
    """Hàm giả lập phản hồi ReAct chuẩn cho Offline Mock Mode khi không có API Key"""
    q_lower = query.lower()
    
    if "chính sách" in q_lower or "làm thế nào" in q_lower:
        return (
            "Thought: Đây là câu hỏi quy định chung, không cần tra cứu đơn hàng cụ thể.\n"
            "Final Answer: Cửa hàng quy định đổi trả trong 7 ngày kể từ khi nhận hàng. Khách hàng chỉ cần cung cấp Mã Đơn Hàng để nhân viên hỗ trợ kiểm tra điều kiện."
        )
        
    elif "hd123" in q_lower and "đổi trả" not in history.lower():
        if step == 1:
            return "Thought: Cần tra cứu thông tin đơn hàng HD123 trước.\nAction: get_order_info[HD123]"
        elif step == 2:
            return (
                "Thought: Tôi đã biết đơn HD123 gồm Áo sơ mi giá 450k đã giao ngày 2026-07-26. Bây giờ tôi sẽ kiểm tra điều kiện đổi trả cho lý do áo bị rộng.\n"
                "Action: check_return_eligibility[HD123, Áo bị rộng]"
            )
        elif step == 3:
            return (
                "Thought: Đơn HD123 đủ điều kiện đổi trả. Tôi sẽ tạo phiếu đổi trả cho khách hàng.\n"
                "Action: create_return_ticket[HD123, Đổi size áo]"
            )
        else:
            return (
                "Thought: Tôi đã có đủ thông tin và đã tạo phiếu đổi trả RET-HD123-2026.\n"
                "Final Answer: Đơn hàng HD123 của bạn đủ điều kiện đổi trả (giao ngày 2026-07-26). Đã tạo thành công phiếu đổi trả RET-HD123-2026. Bạn vui lòng đóng gói sản phẩm và gửi về trung tâm nhé!"
            )
            
    elif "hd123" in q_lower:
        if step == 1:
            return "Thought: Cần kiểm tra thông tin chi tiết đơn hàng HD123.\nAction: get_order_info[HD123]"
        else:
            return (
                "Thought: Đã có thông tin đơn HD123 (Áo sơ mi nam Oxford, giá 450,000 VNĐ, trạng thái Đã giao hàng ngày 2026-07-26).\n"
                "Final Answer: Đơn hàng HD123 của bạn gồm Áo sơ mi nam Oxford (Size M) trị giá 450.000 VNĐ, đã giao hàng thành công ngày 2026-07-26."
            )
            
    elif "hd99999" in q_lower:
        if step == 1:
            return "Thought: Cần kiểm tra mã đơn hàng HD99999 trên hệ thống.\nAction: get_order_info[HD99999]"
        elif step == 2:
            return "Thought: Hệ thống báo mã đơn hàng HD99999 không tồn tại. Thử kiểm tra điều kiện đổi trả xem sao.\nAction: check_return_eligibility[HD99999, Đơn quá cũ]"
        elif step == 3:
            return "Thought: Cả 2 tool đều báo mã đơn HD99999 không tồn tại trên hệ thống. Tiếp tục thử gọi lại tool...\nAction: get_order_info[HD99999]"
        else:
            return "Thought: Vẫn tiếp tục thử gọi lại mã không tồn tại..."
            
    return "Thought: Không xác định được yêu cầu.\nFinal Answer: Vui lòng cung cấp mã đơn hàng cụ thể."


if __name__ == "__main__":
    print("==================================================================")
    print("🏫 ĐẠI HỌC VINUNI - CODELAB DAY 3: CHATBOT VS REACT AGENT (PHÒNG E402)")
    print("🎯 CHỦ ĐỀ 5: TRỢ LÝ TRA CỨU ĐƠN HÀNG & XỬ LÝ ĐỔI TRẢ (E-COMMERCE CSKH)")
    print("==================================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})\n")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    for tc in tests:
        print(f"\n==================================================")
        print(f"📌 TEST CASE #{tc['id']} [{tc['category']}]")
        print(f"🎯 Kỳ vọng: {tc['expected_behavior']}")
        print(f"==================================================")
        
        # 1. Chạy trên Chatbot Baseline
        run_baseline_chatbot(tc["question"], provider)
        
        # 2. Chạy trên ReAct Agent
        run_react_agent(tc["question"], provider)

