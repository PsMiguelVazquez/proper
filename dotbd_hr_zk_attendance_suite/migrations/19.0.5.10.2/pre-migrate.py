# -*- coding: utf-8 -*-
"""
Migration script for v19.0.5.10.2
Fix: Drop foreign key constraints on res.config.settings that were created
when dotbd_salary_journal_id and related fields were Many2one fields.

These constraints prevent deletion of journals/accounts and cause errors:
"Constraint: res_config_settings_dotbd_salary_journal_id_fkey"

The fields have been changed to Integer fields storing record IDs instead
of Many2one references, so these constraints are no longer needed.
"""
import logging

_logger = logging.getLogger(__name__)

MODULE = 'dotbd_hr_zk_attendance_suite'

# List of foreign key constraints to drop
CONSTRAINTS_TO_DROP = [
    'res_config_settings_dotbd_salary_journal_id_fkey',
    'res_config_settings_dotbd_salary_expense_account_id_fkey',
    'res_config_settings_dotbd_salary_payable_account_id_fkey',
    'res_config_settings_dotbd_salary_deduction_account_id_fkey',
]


def migrate(cr, version):
    """Drop obsolete foreign key constraints on res.config.settings."""
    _logger.info("Running pre-migration for %s v19.0.5.10.2...", MODULE)

    for constraint_name in CONSTRAINTS_TO_DROP:
        # Check if constraint exists
        cr.execute("""
            SELECT conname
            FROM pg_constraint
            WHERE conname = %s
            AND conrelid = 'res_config_settings'::regclass
        """, (constraint_name,))

        if cr.fetchone():
            _logger.info("Dropping constraint: %s", constraint_name)
            cr.execute("""
                ALTER TABLE res_config_settings
                DROP CONSTRAINT IF EXISTS %s
            """ % constraint_name)
            _logger.info("Constraint %s dropped successfully", constraint_name)
        else:
            _logger.debug("Constraint %s does not exist, skipping", constraint_name)

    _logger.info("Pre-migration for %s v19.0.5.10.2 completed", MODULE)
