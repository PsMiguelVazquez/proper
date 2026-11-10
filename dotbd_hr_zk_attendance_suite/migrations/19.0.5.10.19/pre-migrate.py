# -*- coding: utf-8 -*-
"""
Migration 19.0.5.10.19 — pre-migrate
Runs BEFORE the ORM upgrade.

Safe operations only (no ORM calls — the model registry is not yet updated).
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info("dotbd_hr_zk_attendance_suite 19.0.5.10.19 pre-migrate: start")

    # Nothing destructive to do before the ORM loads.
    # Placeholder so Odoo recognises this as a versioned migration.

    _logger.info("dotbd_hr_zk_attendance_suite 19.0.5.10.19 pre-migrate: done")
