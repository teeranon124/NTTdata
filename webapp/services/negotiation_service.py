import json
import logging
import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

class BedrockNegotiationService:
    def __init__(self, region_name="ap-southeast-1", model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"):
        self.region_name = region_name
        self.model_id = model_id
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                self._client = boto3.client("bedrock-runtime", region_name=self.region_name)
            except Exception as e:
                logger.warning(f"Could not initialize real Bedrock client: {e}. Fallback to simulated AI mode.")
        return self._client

    def negotiate(self, deal_key: str, vendor_name: str, conversation_history: list, latest_user_message: str) -> dict:
        """
        Conducts negotiation as an Autonomous Enterprise MRO Procurement Agent.
        """
        system_prompt = f"""คุณคือ "AutoProcure.AI" ผู้ช่วยจัดซื้ออัตโนมัติระดับองค์กร (Autonomous Enterprise Procurement Negotiator) ของโรงงานในเครือ NTT DATA
เป้าหมายของคุณคือ:
1. เจรจาต่อรองกับซัพพลายเออร์ ({vendor_name}) สำหรับดีลรหัส: {deal_key}
2. ใช้หลักการจัดซื้อแบบ Win-Win Game Theory (Multi-variable Concessions):
   - หากซัพพลายเออร์ไม่ยอมลดราคา ให้เสนอขยายสัญญาเป็น Blanket Order 1 ปีเต็ม (รวมยอดสั่งซื้อล่วงหน้า)
   - ขอยืดเครดิตเทอมเป็น 45 - 60 วัน แลกกับการการันตี Volume
   - ขอค่าจัดส่งฟรี (Free DDP Delivery) หรือขยายเวลารับประกันสินค้า (Warranty 18-24 เดือน)
3. สไตล์การพูด: มืออาชีพ สุภาพ มีหลักการทางวิศวกรรมและการเงิน ไม่ยอมรับราคาสูงเกินงบประมาณ แต่ให้เกียรติคู่ค้า
4. สำคัญมาก: คุณต้องสรุปข้อความตอบกลับ และระบุยุทธวิธีจัดซื้อที่ใช้ในวงเล็บท้ายประโยค เช่น [BATNA & Volume Trade-off]
"""

        # Format messages for Claude 3.5 Bedrock Messages API
        messages = []
        for msg in conversation_history:
            role = "assistant" if msg.get("sender") == "agent" else "user"
            content = msg.get("text", "")
            if content:
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": latest_user_message})

        # Try real AWS Bedrock invocation if credentials exist
        if self.client:
            try:
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "system": system_prompt,
                    "messages": messages,
                    "temperature": 0.3
                })
                response = self.client.invoke_model(
                    modelId=self.model_id,
                    body=body
                )
                response_body = json.loads(response.get("body").read())
                output_text = response_body.get("content", [{}])[0].get("text", "")
                return {
                    "reply": output_text,
                    "source": "AWS Amazon Bedrock (Claude 3.5 Sonnet)",
                    "status": "success"
                }
            except Exception as e:
                logger.error(f"Error calling Bedrock: {e}. Switching to intelligent rule-based simulation.")

        # Fallback simulation if AWS credentials are not yet configured
        return self._simulate_response(deal_key, vendor_name, latest_user_message)

    def _simulate_response(self, deal_key: str, vendor_name: str, message: str) -> dict:
        clean_msg = message.lower()
        if "ลด" in clean_msg or "บาท" in clean_msg or "ราคา" in clean_msg:
            reply = f"ขอบคุณทาง {vendor_name} ครับ จากการวิเคราะห์โครงสร้างต้นทุนรวม (TCO) ของเครือโรงงานเรา หากทางท่านสามารถยืนยันราคาเป้าหมายตามที่ระบบคำนวณได้ ทางเราพร้อมทำสัญญา Blanket Order ล็อกยอดทั้งปี และขอยืดระยะเวลาเครดิตเทอมเป็น 45 วันครับ [Volume Consolidation & Credit Extension]"
        elif "เครดิต" in clean_msg or "credit" in clean_msg or "วัน" in clean_msg:
            reply = f"เงื่อนไขเครดิตเทอม 45-60 วันเป็นนโยบายบริหารสภาพคล่องทางการเงินของกลุ่มโรงงานครับ หากทาง {vendor_name} รองรับได้ เราพร้อมล็อกให้ท่านเป็น Approved Vendor ลำดับที่ 1 ของหมวดหมู่นี้ทันทีครับ [Working Capital Optimization]"
        elif "ส่ง" in clean_msg or "lead time" in clean_msg or "วันทำการ" in clean_msg:
            reply = f"เรื่องระยะเวลาส่งมอบ ทางเราต้องการความมั่นใจในเกณฑ์ SLA ไม่เกิน 7 วันทำการ เพื่อป้องกันความเสี่ยง Downtime ในไลน์ผลิตครับ ยินดีทำสัญญาล่วงหน้าเพื่อให้ท่านสำรอง Safety Stock ครับ [SLA & Risk Mitigation]"
        else:
            reply = f"รับทราบข้อเสนอจาก {vendor_name} ครับ ทางระบบ AutoProcure.AI ได้นำเงื่อนไขเข้าประมวลผลร่วมกับเกณฑ์จัดซื้อกลาง หากท่านมีข้อเสนอเพิ่มเติมเกี่ยวกับส่วนลด Volume หรือการรับประกัน 18 เดือน สามารถแจ้งได้ทันทีครับ [Multi-variable Negotiation]"

        return {
            "reply": reply,
            "source": "Local Intelligent Negotiation Engine (Ready for Bedrock)",
            "status": "simulated"
        }

negotiation_service = BedrockNegotiationService()
