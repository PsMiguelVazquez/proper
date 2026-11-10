# -*- coding: utf-8 -*-
"""
Migration: 19.0.8.10.48 (pre-migrate)

Fixes UndefinedColumn crashes caused by new fields added to transient models.
Odoo normally adds columns on module upgrade (-u), but if a server restarts
with new code before -u runs, the INSERT into res_config_settings crashes with
"column X does not exist".

Fixes applied:
1. Drop res_users.dotbd_show_payroll (store=True -> store=False).
2. Ensure all new res_config_settings columns exist (Boolean + numeric).
   Covers: enable_native_payroll and all other recently added settings.
"""

import logging
logger = logging.getLogger(__name__)


def _ensure_col(cr, table, col, col_type='boolean', default='false'):
    """Add column if it doesn't exist — safe to call multiple times."""
    cr.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name=%s AND column_name=%s",
        (table, col))
    if not cr.fetchone():
        cr.execute(
            f'ALTER TABLE {table} ADD COLUMN "{col}" {col_type} DEFAULT %s',
            (default,))
        logger.info("19.0.8.10.48 pre: added %s.%s", table, col)


def migrate(cr, version):
    # ── 1. Drop stale dotbd_show_payroll column from res_users ─────────────────
    cr.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name='res_users' AND column_name='dotbd_show_payroll'")
    if cr.fetchone():
        cr.execute('ALTER TABLE res_users DROP COLUMN dotbd_show_payroll')
        logger.info("19.0.8.10.48 pre: dropped res_users.dotbd_show_payroll")

    # ── 2. Ensure res_config_settings columns exist ─────────────────────────────
    # Boolean settings
    for col in [
        'enable_native_payroll',
        'enable_late_penalties',
        'enable_auto_payslip',
        'payslip_notify_hr',
        'payslip_auto_email',
        'enable_hr_payroll_sync',
        'enable_absence_fine',
        'enable_auto_close',
        'print_check_payslip_status',
        'weekend_monday', 'weekend_tuesday', 'weekend_wednesday',
        'weekend_thursday', 'weekend_friday', 'weekend_saturday', 'weekend_sunday',
    ]:
        _ensure_col(cr, 'res_config_settings', col, 'boolean', 'false')

    # Integer settings
    for col, default in [
        ('late_check_in_after', '0'),
        ('maximum_minutes', '240'),
        ('auto_close_checkout_offset_hours', '0'),
        ('max_shift_hours', '16'),
        ('max_open_attendance_hours', '18'),
        ('shift_hours_default', '8'),
        ('native_fallback_hours', '36'),
        ('dotbd_salary_journal_id', '0'),
        ('dotbd_salary_expense_account_id', '0'),
        ('dotbd_salary_payable_account_id', '0'),
        ('dotbd_salary_deduction_account_id', '0'),
    ]:
        _ensure_col(cr, 'res_config_settings', col, 'integer', default)

    # Float / double settings
    for col in ['deduction_amount', 'absence_fine_amount']:
        _ensure_col(cr, 'res_config_settings', col, 'double precision', '0')

    logger.info("19.0.8.10.48 pre: res_config_settings columns ensured")
