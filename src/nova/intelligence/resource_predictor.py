"""
Nova Dragon — نظام التنبؤ الذكي بالموارد
يتتبع استهلاك الطاقة ويتنبأ بأفضل وقت لتشغيل المهام
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class ResourcePredictor:
    """محرك التنبؤ الذكي بموارد اللعبة"""

    MAX_BATTERY = 240
    REGEN_PER_MINUTE = 1  # نقطة طاقة كل دقيقة (تقريبي)
    DATA_FILE = "nova_resource_history.json"

    def __init__(self, data_dir: str | Path | None = None):
        self._data_dir = Path(data_dir) if data_dir else Path(".")
        self._history: list[dict[str, Any]] = []
        self._last_known_battery: int = -1
        self._last_update_time: float = 0
        self._load_history()

    # ═══════════════════════════════════════════════════
    #  تسجيل البيانات
    # ═══════════════════════════════════════════════════

    def record_battery(self, value: int) -> None:
        """تسجيل قراءة طاقة جديدة"""
        now = time.time()
        self._last_known_battery = value
        self._last_update_time = now
        self._history.append({
            "type": "battery",
            "value": value,
            "timestamp": now,
            "datetime": datetime.now().isoformat(),
        })
        self._trim_history()
        self._save_history()

    def record_task(self, task_name: str, battery_cost: int, success: bool) -> None:
        """تسجيل مهمة مكتملة مع تكلفة الطاقة"""
        self._history.append({
            "type": "task",
            "task_name": task_name,
            "battery_cost": battery_cost,
            "success": success,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
        })
        if self._last_known_battery > 0:
            self._last_known_battery = max(0, self._last_known_battery - battery_cost)
            self._last_update_time = time.time()
        self._trim_history()
        self._save_history()

    # ═══════════════════════════════════════════════════
    #  التنبؤات
    # ═══════════════════════════════════════════════════

    def predict_full_battery_time(self) -> datetime | None:
        """متى ستمتلئ الطاقة؟"""
        if self._last_known_battery < 0:
            return None
        if self._last_known_battery >= self.MAX_BATTERY:
            return datetime.now()

        remaining = self.MAX_BATTERY - self._last_known_battery
        # حساب الطاقة المتراكمة منذ آخر قراءة
        elapsed_minutes = (time.time() - self._last_update_time) / 60
        current_estimated = min(
            self.MAX_BATTERY,
            self._last_known_battery + int(elapsed_minutes * self.REGEN_PER_MINUTE)
        )
        if current_estimated >= self.MAX_BATTERY:
            return datetime.now()

        remaining_now = self.MAX_BATTERY - current_estimated
        minutes_to_full = remaining_now / self.REGEN_PER_MINUTE
        return datetime.now() + timedelta(minutes=minutes_to_full)

    def get_estimated_battery(self) -> int:
        """الطاقة المقدّرة حالياً"""
        if self._last_known_battery < 0:
            return -1
        elapsed_minutes = (time.time() - self._last_update_time) / 60
        estimated = self._last_known_battery + int(elapsed_minutes * self.REGEN_PER_MINUTE)
        return min(self.MAX_BATTERY, estimated)

    def get_optimal_run_time(self) -> datetime | None:
        """أفضل وقت لتشغيل المهام (قبل امتلاء الطاقة بـ 10 دقائق)"""
        full_time = self.predict_full_battery_time()
        if full_time is None:
            return None
        optimal = full_time - timedelta(minutes=10)
        if optimal < datetime.now():
            return datetime.now()
        return optimal

    def get_daily_summary(self) -> dict[str, Any]:
        """ملخص يومي: إجمالي المهام، الطاقة المستهلكة، معدل النجاح"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0).timestamp()
        today_tasks = [
            h for h in self._history
            if h["type"] == "task" and h["timestamp"] >= today_start
        ]
        total = len(today_tasks)
        success = sum(1 for t in today_tasks if t.get("success", False))
        total_cost = sum(t.get("battery_cost", 0) for t in today_tasks)

        return {
            "total_tasks": total,
            "successful": success,
            "failed": total - success,
            "success_rate": (success / total * 100) if total > 0 else 0,
            "battery_consumed": total_cost,
            "estimated_battery": self.get_estimated_battery(),
        }

    def get_smart_suggestion(self) -> str:
        """اقتراح ذكي بناءً على الحالة الحالية"""
        battery = self.get_estimated_battery()
        if battery < 0:
            return "🔍 لم يتم رصد الطاقة بعد — شغّل اللعبة أولاً."

        full_time = self.predict_full_battery_time()
        if battery >= self.MAX_BATTERY:
            return "🔴 الطاقة ممتلئة! شغّل المهام فوراً لتجنب الهدر."

        if battery >= 200:
            return f"🟡 الطاقة عالية ({battery}/{self.MAX_BATTERY}). يُفضّل تشغيل المهام قريباً."

        if full_time:
            delta = full_time - datetime.now()
            hours = int(delta.total_seconds() // 3600)
            mins = int((delta.total_seconds() % 3600) // 60)
            if hours > 0:
                return f"🟢 الطاقة ستمتلئ خلال {hours} ساعة و {mins} دقيقة."
            else:
                return f"🟡 الطاقة ستمتلئ خلال {mins} دقيقة — جهّز المهام!"

        return f"🟢 الطاقة: {battery}/{self.MAX_BATTERY}"

    # ═══════════════════════════════════════════════════
    #  التخزين
    # ═══════════════════════════════════════════════════

    def _load_history(self) -> None:
        path = self._data_dir / self.DATA_FILE
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._history = data.get("history", [])
                    self._last_known_battery = data.get("last_battery", -1)
                    self._last_update_time = data.get("last_update", 0)
            except Exception:
                self._history = []

    def _save_history(self) -> None:
        path = self._data_dir / self.DATA_FILE
        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump({
                    "history": self._history,
                    "last_battery": self._last_known_battery,
                    "last_update": self._last_update_time,
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _trim_history(self, max_entries: int = 1000) -> None:
        """الاحتفاظ بآخر 1000 سجل فقط"""
        if len(self._history) > max_entries:
            self._history = self._history[-max_entries:]
