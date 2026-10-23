# -*- coding: utf-8 -*-
"""
Migration script for dotbd_hr_zk_attendance_suite
Version: 18.0.3.0.0

This runs BEFORE the module is upgraded.
Deletes old views that reference the removed 'leave_attendance_category' field.
"""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migration function called by Odoo before upgrading the module.

    Args:
        cr: Database cursor
        version: Current installed version (before upgrade)
    """
    _logger.info("="*80)
    _logger.info("MIGRATION 18.0.3.0.0: Cleaning up old views...")
    _logger.info(f"Upgrading from version: {version}")
    _logger.info("="*80)

    # Method 1: Delete by specific XML ID
    _logger.info("Method 1: Deleting by exact XML ID...")
    cr.execute("""
        DELETE FROM ir_ui_view
        WHERE key = 'dotbd_hr_zk_attendance_suite.view_hr_leave_type_form_inherit'
    """)
    deleted_by_xmlid = cr.rowcount
    _logger.info(f"   Deleted {deleted_by_xmlid} view(s) by exact XML ID")

    # Method 2: Delete by XML ID pattern
    _logger.info("Method 2: Deleting by XML ID pattern...")
    cr.execute("""
        DELETE FROM ir_ui_view
        WHERE key LIKE 'dotbd_hr_zk_attendance_suite.%hr_leave_type%'
          AND model = 'hr.leave.type'
    """)
    deleted_by_xmlid_pattern = cr.rowcount
    _logger.info(f"   Deleted {deleted_by_xmlid_pattern} view(s) by XML ID pattern")

    # Method 3: Delete views that reference the removed field in arch_db
    # arch_db is JSONB in Odoo 18, so cast to text first
    _logger.info("Method 3: Deleting by field reference in arch_db...")
    cr.execute("""
        DELETE FROM ir_ui_view
        WHERE model = 'hr.leave.type'
          AND arch_db::text LIKE '%leave_attendance_category%'
    """)
    deleted_by_field = cr.rowcount
    _logger.info(f"   Deleted {deleted_by_field} view(s) by field reference")

    # Method 4: Clean up orphaned ir_model_data entries
    _logger.info("Method 4: Cleaning up ir_model_data entries...")
    cr.execute("""
        DELETE FROM ir_model_data
        WHERE module = 'dotbd_hr_zk_attendance_suite'
          AND model = 'ir.ui.view'
          AND name = 'view_hr_leave_type_form_inherit'
    """)
    deleted_model_data = cr.rowcount
    _logger.info(f"   Deleted {deleted_model_data} model data entry(ies)")

    total_deleted = deleted_by_xmlid + deleted_by_xmlid_pattern + deleted_by_field + deleted_model_data

    _logger.info("="*80)
    if total_deleted > 0:
        _logger.info(f"✅ Migration complete: {total_deleted} total item(s) deleted")
    else:
        _logger.info("ℹ️ No old views found - database is clean")
    _logger.info("="*80)
