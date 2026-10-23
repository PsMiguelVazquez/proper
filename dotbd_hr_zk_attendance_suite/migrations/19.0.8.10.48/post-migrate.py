# -*- coding: utf-8 -*-
"""
Migration: 19.0.8.10.48 (post-migrate)
Copy all group_payroll_access members into group_dotbd_payroll_visible
so existing users keep their payroll menu access after the upgrade.
"""
import logging
logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute("""
        SELECT res_id FROM ir_model_data
        WHERE module = 'dotbd_hr_zk_attendance_suite'
          AND name   = 'group_dotbd_payroll_visible'
    """)
    row = cr.fetchone()
    if not row:
        logger.warning("19.0.8.10.48 post: group_dotbd_payroll_visible not found — skipping")
        return
    new_group_id = row[0]

    cr.execute("""
        SELECT res_id FROM ir_model_data
        WHERE module = 'dotbd_hr_zk_attendance_suite'
          AND name   = 'group_payroll_access'
    """)
    row = cr.fetchone()
    if not row:
        logger.warning("19.0.8.10.48 post: group_payroll_access not found — skipping")
        return
    old_group_id = row[0]

    cr.execute("""
        INSERT INTO res_groups_users_rel (gid, uid)
        SELECT %s, uid FROM res_groups_users_rel WHERE gid = %s
        ON CONFLICT DO NOTHING
    """, (new_group_id, old_group_id))

    logger.info(
        "19.0.8.10.48 post: copied %d users from group_payroll_access "
        "to group_dotbd_payroll_visible", cr.rowcount)
