# -*- coding: utf-8 -*-
"""
Migration 19.0.5.10.19 — post-migrate
Runs AFTER the ORM upgrade.

What this migration does:
1. Removes stale year-2000 attendance records imported from devices with dead
   RTC batteries (timestamps with year < 2010).
2. Cleans up the flood of per-record device log Warning entries created before
   the batched-logging fix — keeps only the most recent 500 per device.
3. Patches the biometric.device user_count / user_capacity values that were
   swapped by the bug (resets them to 0 so the next "Get Info" fills them
   correctly).
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info("dotbd_hr_zk_attendance_suite 19.0.5.10.19 post-migrate: start")

    # ── 1. Remove year-2000 raw punch records ────────────────────────────────
    cr.execute("""
        SELECT COUNT(*) FROM zk_machine_attendance
        WHERE punching_time < '2010-01-01'
    """)
    bad_punch_count = cr.fetchone()[0]
    if bad_punch_count:
        _logger.warning(
            "Migration 19.0.5.10.19: deleting %d zk_machine_attendance records "
            "with timestamps before 2010 (device RTC battery fault).",
            bad_punch_count
        )
        cr.execute("""
            DELETE FROM zk_machine_attendance
            WHERE punching_time < '2010-01-01'
        """)

    # ── 2. Remove year-2000 hr.attendance records ────────────────────────────
    cr.execute("""
        SELECT COUNT(*) FROM hr_attendance
        WHERE check_in < '2010-01-01'
    """)
    bad_att_count = cr.fetchone()[0]
    if bad_att_count:
        _logger.warning(
            "Migration 19.0.5.10.19: deleting %d hr_attendance records "
            "with check_in before 2010 (device RTC battery fault).",
            bad_att_count
        )
        cr.execute("""
            DELETE FROM hr_attendance
            WHERE check_in < '2010-01-01'
        """)

    # ── 3. Trim flood of per-record warning device logs ──────────────────────
    # Keep the 500 most recent log entries per device; delete the rest that
    # were created by the old per-record logging loop.
    cr.execute("""
        DELETE FROM biometric_device_log
        WHERE id IN (
            SELECT id FROM (
                SELECT id,
                       ROW_NUMBER() OVER (
                           PARTITION BY device_id
                           ORDER BY create_date DESC
                       ) AS rn
                FROM biometric_device_log
                WHERE log_type = 'download'
                  AND status = 'warning'
                  AND records_found = 0
                  AND records_new = 0
            ) ranked
            WHERE rn > 500
        )
    """)
    cr.execute("""
        SELECT COUNT(*) FROM biometric_device_log
        WHERE log_type = 'download'
          AND status = 'warning'
          AND records_found = 0
          AND records_new = 0
    """)
    remaining = cr.fetchone()[0]
    _logger.info(
        "Migration 19.0.5.10.19: device log cleanup done. "
        "Remaining zero-record warning logs: %d", remaining
    )

    # ── 4. Reset swapped user_count / user_capacity fields ───────────────────
    # After the fix the next "Get Info" will fill them correctly.
    cr.execute("""
        UPDATE biometric_device_details
        SET user_count    = 0,
            user_capacity = 0,
            finger_count    = 0,
            finger_capacity = 0,
            record_count    = 0,
            record_capacity = 0,
            face_count    = 0,
            face_capacity = 0
        WHERE user_count > 0 OR user_capacity > 0
    """)

    _logger.info("dotbd_hr_zk_attendance_suite 19.0.5.10.19 post-migrate: done")
