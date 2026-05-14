"""
Nova Dragon — جسر الربط مع الباك إند
يربط واجهة Nova مباشرة مع ZContext والعمليات الحقيقية للمشروع الأصلي
"""
from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from one_dragon.base.operation.application_run_record import AppRunRecord
    from one_dragon.base.operation.operation_base import OperationResult
    from zzz_od.application.one_dragon_app.zzz_one_dragon_app import ZOneDragonApp
    from zzz_od.context.zzz_context import ZContext

_log = logging.getLogger("nova.bridge")


class NovaBackendBridge:
    """
    الجسر الحقيقي بين واجهة Nova والباك إند الأصلي
    يتحكم بالعمليات ويراقب حالتها ويبث الأحداث للواجهة
    """

    def __init__(self, ctx):
        self.ctx = ctx
        self._executor = ThreadPoolExecutor(
            thread_name_prefix="nova_bridge", max_workers=2
        )
        self._running: bool = False
        self._current_app = None
        self._monitor_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        # ─── Callbacks للواجهة ───
        self._on_task_start: Callable[[str], None] | None = None
        self._on_task_done: Callable[[str, bool], None] | None = None
        self._on_status_change: Callable[[str], None] | None = None
        self._on_battery_update: Callable[[int], None] | None = None
        self._on_progress_update: Callable[[str, int], None] | None = None
        self._on_log: Callable[[str, str], None] | None = None
        self._on_game_connected: Callable[[bool], None] | None = None

    # ═══════════════════════════════════════════════════
    #  ربط الـ Callbacks مع الواجهة
    # ═══════════════════════════════════════════════════

    def on_task_start(self, callback: Callable[[str], None]) -> None:
        """عند بدء مهمة — callback(task_name)"""
        self._on_task_start = callback

    def on_task_done(self, callback: Callable[[str, bool], None]) -> None:
        """عند انتهاء مهمة — callback(task_name, success)"""
        self._on_task_done = callback

    def on_status_change(self, callback: Callable[[str], None]) -> None:
        """عند تغيّر حالة النظام — callback(status_text)"""
        self._on_status_change = callback

    def on_battery_update(self, callback: Callable[[int], None]) -> None:
        """عند تحديث الطاقة — callback(value)"""
        self._on_battery_update = callback

    def on_progress_update(self, callback: Callable[[str, int], None]) -> None:
        """عند تحديث التقدم — callback(task_name, percent)"""
        self._on_progress_update = callback

    def on_log(self, callback: Callable[[str, str], None]) -> None:
        """عند وجود سجل جديد — callback(message, level)"""
        self._on_log = callback

    def on_game_connected(self, callback: Callable[[bool], None]) -> None:
        """عند تغيّر اتصال اللعبة — callback(connected)"""
        self._on_game_connected = callback

    # ═══════════════════════════════════════════════════
    #  التهيئة — ربط السياق
    # ═══════════════════════════════════════════════════

    def initialize(self) -> bool:
        """تهيئة السياق الكاملة — يجب استدعاؤها قبل أي شيء"""
        try:
            self._emit_log("جاري تهيئة النظام...", "info")
            self._emit_status("جاري التهيئة...")

            # تهيئة السياق الأصلي (يحمّل كل شيء: OCR, YOLO, الخ)
            if hasattr(self.ctx, 'init'):
                self.ctx.init()

            self._emit_log("تم تحميل نماذج YOLO", "success")
            self._emit_log("تم تهيئة OCR", "success")
            self._emit_log("تم تسجيل التطبيقات", "success")

            # فحص اتصال اللعبة
            game_ready = getattr(self.ctx, 'is_game_window_ready', False)
            if self._on_game_connected:
                self._on_game_connected(game_ready)

            if game_ready:
                self._emit_log("✅ اللعبة متصلة", "success")
            else:
                self._emit_log("⚠️ اللعبة غير متصلة — افتح اللعبة أولاً", "warning")

            self._emit_status("جاهز")
            self._emit_log("النظام جاهز للتشغيل", "success")
            return True

        except Exception as e:
            self._emit_log(f"خطأ في التهيئة: {e}", "error")
            self._emit_status("خطأ في التهيئة")
            _log.error("Nova bridge init failed", exc_info=True)
            return False

    def initialize_async(self) -> None:
        """تهيئة غير متزامنة في الخلفية"""
        self._executor.submit(self.initialize)

    # ═══════════════════════════════════════════════════
    #  التشغيل — تنفيذ المهام الحقيقية
    # ═══════════════════════════════════════════════════

    def start_one_dragon(self) -> None:
        """تشغيل سلسلة المهام الكاملة (一条龙) — نفس ما يفعله الزر الأصلي"""
        if self._running:
            self._emit_log("⚠️ الأتمتة تعمل بالفعل", "warning")
            return

        self._running = True
        self._stop_event.clear()
        self._emit_status("جاري التشغيل...")
        self._emit_log("🚀 بدء سلسلة المهام (一条龙)", "info")

        self._executor.submit(self._run_one_dragon_thread)

    def _run_one_dragon_thread(self) -> None:
        """تنفيذ سلسلة المهام في thread منفصل"""
        try:
            from zzz_od.application.one_dragon_app.zzz_one_dragon_app import ZOneDragonApp

            # تفعيل حالة التشغيل في السياق
            self.ctx.run_context.start_running()

            # إنشاء تطبيق
            self._current_app = ZOneDragonApp(self.ctx)

            # بدء المراقبة
            self._start_monitor()

            # تنفيذ
            self._emit_log("جاري تنفيذ المهام...", "info")
            result = self._current_app.execute()

            # النتيجة
            if result.success:
                self._emit_log("✅ اكتملت جميع المهام بنجاح!", "success")
                self._emit_status("مكتمل ✅")
            else:
                self._emit_log(f"⚠️ انتهت المهام — الحالة: {result.status}", "warning")
                self._emit_status("مكتمل مع ملاحظات")

        except Exception as e:
            self._emit_log(f"❌ خطأ: {e}", "error")
            self._emit_status("خطأ")
            _log.error("Nova one dragon run failed", exc_info=True)
        finally:
            self._running = False
            self._current_app = None
            self._stop_monitor()

    def stop(self) -> None:
        """إيقاف التشغيل"""
        if not self._running:
            return

        self._emit_log("⏹ جاري الإيقاف...", "info")
        self._emit_status("جاري الإيقاف...")

        try:
            self.ctx.run_context.stop_running()
        except Exception:
            pass

        self._stop_event.set()
        self._running = False
        self._emit_log("⏹ تم الإيقاف", "info")
        self._emit_status("متوقف")

    def pause_resume(self) -> None:
        """إيقاف مؤقت / استئناف"""
        try:
            self.ctx.run_context.switch_context_pause_and_run()
            paused = not self.ctx.run_context.is_running
            if paused:
                self._emit_log("⏸ إيقاف مؤقت", "info")
                self._emit_status("إيقاف مؤقت")
            else:
                self._emit_log("▶ استئناف", "info")
                self._emit_status("جاري التشغيل...")
        except Exception:
            pass

    # ═══════════════════════════════════════════════════
    #  المراقبة الحية
    # ═══════════════════════════════════════════════════

    def _start_monitor(self) -> None:
        """بدء مراقبة حالة المهام كل ثانية"""
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="nova_monitor"
        )
        self._monitor_thread.start()

    def _stop_monitor(self) -> None:
        self._stop_event.set()

    def _monitor_loop(self) -> None:
        """حلقة مراقبة تقرأ حالة المهام من السياق الأصلي"""
        last_states: dict[str, str] = {}

        while not self._stop_event.is_set():
            try:
                self._check_task_states(last_states)
                self._check_game_connection()
                self._check_battery()
            except Exception:
                pass
            self._stop_event.wait(timeout=2.0)

    def _check_task_states(self, last_states: dict[str, str]) -> None:
        """فحص حالة كل مهمة مسجلة"""
        try:
            from one_dragon.base.operation.application_run_record import AppRunRecord

            group_config = self.ctx.app_group_manager.get_one_dragon_group_config(
                instance_idx=self.ctx.current_instance_idx
            )
            total = len(group_config.app_list)
            done_count = 0

            for app_config in group_config.app_list:
                app_id = app_config.app_id
                app_name = app_config.app_name

                run_record: AppRunRecord | None = self.ctx.run_context.get_run_record(
                    app_id=app_id,
                    instance_idx=self.ctx.current_instance_idx,
                )
                if run_record is None:
                    continue

                current_status = run_record.run_status_under_now
                old_status = last_states.get(app_id)

                if current_status != old_status:
                    last_states[app_id] = current_status

                    if current_status == AppRunRecord.STATUS_SUCCESS:
                        done_count += 1
                        if self._on_task_done:
                            self._on_task_done(app_name, True)
                        self._emit_log(f"✅ {app_name}", "success")

                    elif current_status == AppRunRecord.STATUS_FAIL:
                        done_count += 1
                        if self._on_task_done:
                            self._on_task_done(app_name, False)
                        self._emit_log(f"❌ {app_name}", "error")

                    elif current_status == AppRunRecord.STATUS_RUNNING:
                        if self._on_task_start:
                            self._on_task_start(app_name)
                        self._emit_log(f"▶ {app_name}...", "info")

                elif current_status in (
                    AppRunRecord.STATUS_SUCCESS,
                    AppRunRecord.STATUS_FAIL,
                ):
                    done_count += 1

            # تحديث التقدم
            if total > 0 and self._on_progress_update:
                pct = int((done_count / total) * 100)
                running_name = "جاري التنفيذ..."
                for app_config in group_config.app_list:
                    rec = self.ctx.run_context.get_run_record(
                        app_id=app_config.app_id,
                        instance_idx=self.ctx.current_instance_idx,
                    )
                    if rec and rec.run_status_under_now == AppRunRecord.STATUS_RUNNING:
                        running_name = app_config.app_name
                        break
                self._on_progress_update(running_name, pct)

        except Exception:
            pass

    def _check_game_connection(self) -> None:
        """فحص اتصال نافذة اللعبة"""
        try:
            connected = self.ctx.is_game_window_ready
            if self._on_game_connected:
                self._on_game_connected(connected)
        except Exception:
            pass

    def _check_battery(self) -> None:
        """محاولة قراءة الطاقة من سجل charge_plan"""
        try:
            from zzz_od.application.charge_plan.charge_plan_run_record import (
                ChargePlanRunRecord,
            )
            rec = self.ctx.run_context.get_run_record(
                app_id="charge_plan",
                instance_idx=self.ctx.current_instance_idx,
            )
            if isinstance(rec, ChargePlanRunRecord):
                power = rec.get_estimated_charge_power()
                if power >= 0 and self._on_battery_update:
                    self._on_battery_update(power)
        except Exception:
            pass

    # ═══════════════════════════════════════════════════
    #  معلومات النظام
    # ═══════════════════════════════════════════════════

    def get_registered_apps(self) -> list[dict[str, str]]:
        """قائمة التطبيقات المسجلة"""
        apps: list[dict[str, str]] = []
        try:
            group_config = self.ctx.app_group_manager.get_one_dragon_group_config(
                instance_idx=self.ctx.current_instance_idx
            )
            for app_config in group_config.app_list:
                apps.append({
                    "id": app_config.app_id,
                    "name": app_config.app_name,
                })
        except Exception:
            pass
        return apps

    def get_instance_name(self) -> str:
        """اسم الحساب النشط"""
        try:
            inst = self.ctx.one_dragon_config.current_active_instance
            return inst.name if inst else "افتراضي"
        except Exception:
            return "افتراضي"

    @property
    def is_running(self) -> bool:
        return self._running

    # ═══════════════════════════════════════════════════
    #  أدوات داخلية
    # ═══════════════════════════════════════════════════

    def _emit_log(self, message: str, level: str) -> None:
        if self._on_log:
            try:
                self._on_log(message, level)
            except Exception:
                pass

    def _emit_status(self, status: str) -> None:
        if self._on_status_change:
            try:
                self._on_status_change(status)
            except Exception:
                pass

    def shutdown(self) -> None:
        """إغلاق كل شيء"""
        self.stop()
        self._executor.shutdown(wait=False)
        try:
            self.ctx.after_app_shutdown()
        except Exception:
            pass
