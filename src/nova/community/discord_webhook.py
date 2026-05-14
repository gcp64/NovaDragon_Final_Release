"""
Nova Dragon — Discord Webhook Integration
ربط مجتمعي متقدم مع Embeds غنية بستايل Cyberpop
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from io import BytesIO
from typing import Any

import cv2
import requests
from cv2.typing import MatLike

from one_dragon.utils.log_utils import log


class NovaDiscordWebhook:
    """نظام Discord Webhook مع Embeds غنية بألوان Cyberpop"""

    # ألوان Embeds (عشري)
    COLOR_SUCCESS = 0x39FF14    # أخضر نيون
    COLOR_FAIL = 0xFF2D78       # وردي ساخن
    COLOR_INFO = 0x00F0FF       # سيان كهربائي
    COLOR_WARNING = 0xFFE02B    # أصفر نيون
    COLOR_SESSION = 0xA855F7    # بنفسجي

    def __init__(self, webhook_url: str = "", username: str = "Nova Dragon 🐉"):
        self.webhook_url: str = webhook_url
        self.username: str = username
        self.avatar_url: str = ""
        self._enabled: bool = bool(webhook_url)

    @property
    def is_enabled(self) -> bool:
        return self._enabled and bool(self.webhook_url)

    def configure(self, webhook_url: str, username: str = "Nova Dragon 🐉") -> None:
        """تحديث إعدادات الـ Webhook"""
        self.webhook_url = webhook_url.strip()
        self.username = username
        self._enabled = bool(self.webhook_url)

    # ═══════════════════════════════════════════════════
    #  إرسال الرسائل
    # ═══════════════════════════════════════════════════

    def send_text(self, content: str) -> tuple[bool, str]:
        """إرسال رسالة نصية بسيطة"""
        if not self.is_enabled:
            return False, "Webhook غير مفعّل"

        payload = {
            "username": self.username,
            "content": content,
        }
        if self.avatar_url:
            payload["avatar_url"] = self.avatar_url

        return self._post(payload)

    def send_embed(
        self,
        title: str,
        description: str,
        color: int = COLOR_INFO,
        fields: list[dict[str, Any]] | None = None,
        footer: str | None = None,
        image: MatLike | None = None,
        thumbnail_url: str | None = None,
    ) -> tuple[bool, str]:
        """إرسال Embed غني بستايل Cyberpop"""
        if not self.is_enabled:
            return False, "Webhook غير مفعّل"

        embed: dict[str, Any] = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if fields:
            embed["fields"] = fields

        if footer:
            embed["footer"] = {"text": footer}
        else:
            embed["footer"] = {
                "text": f"Nova Dragon 🐉 | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }

        if thumbnail_url:
            embed["thumbnail"] = {"url": thumbnail_url}

        payload: dict[str, Any] = {
            "username": self.username,
            "embeds": [embed],
        }
        if self.avatar_url:
            payload["avatar_url"] = self.avatar_url

        # إذا يوجد صورة، أرسلها كمرفق
        if image is not None:
            embed["image"] = {"url": "attachment://screenshot.jpg"}
            return self._post_with_image(payload, image)

        return self._post(payload)

    # ═══════════════════════════════════════════════════
    #  رسائل جاهزة (Templates)
    # ═══════════════════════════════════════════════════

    def send_session_start(self) -> tuple[bool, str]:
        """إشعار بدء الجلسة"""
        return self.send_embed(
            title="🚀 بدء جلسة جديدة",
            description="تم تشغيل Nova Dragon وبدء الأتمتة.",
            color=self.COLOR_INFO,
            fields=[
                {"name": "⏰ الوقت", "value": datetime.now().strftime("%H:%M:%S"), "inline": True},
                {"name": "📅 التاريخ", "value": datetime.now().strftime("%Y-%m-%d"), "inline": True},
            ],
        )

    def send_session_end(
        self,
        duration: str,
        tasks_done: int,
        battles: int,
        success_rate: float,
    ) -> tuple[bool, str]:
        """إشعار انتهاء الجلسة مع ملخص"""
        status_emoji = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
        return self.send_embed(
            title=f"{status_emoji} انتهت الجلسة",
            description="ملخص الأداء لهذه الجلسة:",
            color=self.COLOR_SESSION,
            fields=[
                {"name": "⏱️ المدة", "value": duration, "inline": True},
                {"name": "📋 المهام", "value": str(tasks_done), "inline": True},
                {"name": "⚔️ المعارك", "value": str(battles), "inline": True},
                {"name": "📈 النجاح", "value": f"{success_rate:.0f}%", "inline": True},
            ],
        )

    def send_task_result(
        self,
        task_name: str,
        success: bool,
        details: str = "",
        image: MatLike | None = None,
    ) -> tuple[bool, str]:
        """إشعار بنتيجة مهمة"""
        color = self.COLOR_SUCCESS if success else self.COLOR_FAIL
        status = "✅ نجاح" if success else "❌ فشل"
        return self.send_embed(
            title=f"{status} | {task_name}",
            description=details or f"اكتملت المهمة {'بنجاح' if success else 'مع وجود أخطاء'}.",
            color=color,
            image=image,
        )

    def send_battery_alert(self, current: int, maximum: int = 240) -> tuple[bool, str]:
        """تنبيه امتلاء الطاقة"""
        pct = (current / maximum) * 100
        if pct >= 95:
            emoji, msg = "🔴", "الطاقة ممتلئة! شغّل المهام الآن."
        elif pct >= 80:
            emoji, msg = "🟡", "الطاقة على وشك الامتلاء."
        else:
            emoji, msg = "🟢", "مستوى الطاقة طبيعي."

        return self.send_embed(
            title=f"{emoji} تنبيه الطاقة",
            description=msg,
            color=self.COLOR_WARNING if pct >= 80 else self.COLOR_INFO,
            fields=[
                {"name": "⚡ الطاقة", "value": f"{current}/{maximum}", "inline": True},
                {"name": "📊 النسبة", "value": f"{pct:.0f}%", "inline": True},
            ],
        )

    # ═══════════════════════════════════════════════════
    #  الطبقة الداخلية
    # ═══════════════════════════════════════════════════

    def _post(self, payload: dict) -> tuple[bool, str]:
        try:
            resp = requests.post(
                self.webhook_url,
                json=payload,
                timeout=15,
            )
            if resp.status_code in (200, 204):
                return True, "تم الإرسال بنجاح"
            return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            log.error("Discord Webhook error", exc_info=True)
            return False, f"خطأ: {e}"

    def _post_with_image(
        self, payload: dict, image: MatLike
    ) -> tuple[bool, str]:
        try:
            # تحويل الصورة
            bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            _, buf = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
            img_bytes = BytesIO(buf.tobytes())

            files = {
                "file": ("screenshot.jpg", img_bytes, "image/jpeg"),
            }
            form_data = {
                "payload_json": json.dumps(payload),
            }
            resp = requests.post(
                self.webhook_url,
                data=form_data,
                files=files,
                timeout=30,
            )
            if resp.status_code in (200, 204):
                return True, "تم الإرسال بنجاح (مع صورة)"
            return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            log.error("Discord Webhook image error", exc_info=True)
            return False, f"خطأ: {e}"

    def test_connection(self) -> tuple[bool, str]:
        """اختبار الاتصال بالـ Webhook"""
        return self.send_embed(
            title="🧪 اختبار الاتصال",
            description="تم الاتصال بنجاح! Nova Dragon جاهز لإرسال التقارير.",
            color=self.COLOR_INFO,
            footer="هذه رسالة اختبار — يمكنك حذفها.",
        )
