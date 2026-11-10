# -*- coding: utf-8 -*-
"""
Migration: 19.0.5.9.11

Before this version, ADMS/hybrid devices had `time_sync_method` hidden in the
UI — the field defaulted to 'odoo' but was never intentionally set. The device
timezone was determined solely by `custom_timezone` (always returned first in
_get_device_timezone_for_adms).

From 19.0.5.9.11, `time_sync_method` is now respected. To preserve existing
behavior for all ADMS/hybrid devices, we migrate them to 'custom' so their
existing `custom_timezone` value continues to be used.
"""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Migration 19.0.5.9.11: Setting time_sync_method='custom' for ADMS/hybrid devices...")

    cr.execute("""
        UPDATE biometric_device_details
        SET time_sync_method = 'custom'
        WHERE connection_mode IN ('adms', 'hybrid')
          AND (time_sync_method = 'odoo' OR time_sync_method IS NULL)
    """)
    updated = cr.rowcount
    _logger.info(
        "Migration 19.0.5.9.11: Updated %d ADMS/hybrid device(s) → time_sync_method='custom'",
        updated)
