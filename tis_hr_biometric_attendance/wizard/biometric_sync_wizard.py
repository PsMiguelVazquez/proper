# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class BiometricSyncWizard(models.TransientModel):
    _name = 'biometric.sync.wizard'
    _description = 'Biometric Device Sync Wizard'

    device_ids = fields.Many2many(
        'biometric.config',
        string="Devices",
        required=True,
        help="Target devices to which selected users will be synced."
    )
    user_ids = fields.Many2many(
        'biometric.attendance.devices',
        string="Users",
        required=True,
        help="Users to be synced to the selected devices."
    )



    def _push_userinfo(self, device, user):
        DeviceCommand = self.env['device.command'].sudo()


        pin = user.biometric_attendance_id
        card_number = user.employee_id.barcode if user.employee_id.barcode else "0000000000"

        cmd = DeviceCommand.create({
            'name': 'DATA UPDATE USERINFO',
            'device_id': device.id,
            'employee_id': user.employee_id.id,
            'pin': pin,
            'status': 'pending',
        })

        # Build execution log in the exact format your device expects
        cmd.execution_log = (
            f"C:{cmd.id}:DATA UPDATE USERINFO "
            f"PIN={pin}\t"
            f"Name={user.device_user_name or user.employee_id.name or ''}\t"
            f"Pri=0\tPasswd=\tCard=[{card_number}]\tGrp=1\tTZ=0000000000000000\n"
        )

    def _push_fingerprints(self, device, user):
        DeviceCommand = self.env['device.command'].sudo()

        for finger in user.finger_template_ids:
            fid = finger.f_id or "0"
            tmp_value = finger.template_data or ""
            size = int(finger.f_size or "0")

            cmd = DeviceCommand.create({
                'name': 'DATA UPDATE FINGERTMP',
                'device_id': device.id,
                'pin': user.biometric_attendance_id,
                'status': 'pending',
            })

            cmd.execution_log = (
                f"C:{cmd.id}:DATA UPDATE FINGERTMP PIN={user.biometric_attendance_id}\tFID={fid}\tSize={size}\tValid=1\tTMP={tmp_value}\n"
            )


    def action_confirm_sync(self):
        """Sync selected users to selected devices with full data."""
        self.ensure_one()
        if not self.device_ids or not self.user_ids:
            raise UserError(_("Please select at least one Device and one User."))

        for device in self.device_ids:
            for user in self.user_ids:
                if not user.device_id or not user.biometric_attendance_id:
                    raise UserError(_(
                        "User %s is missing a Biometric User ID. Please set it before syncing."
                    ) % (user.display_name,))

                self._push_userinfo(device, user)
                self._push_fingerprints(device, user)
                # self._push_faces(device, user)

        # close wizard
        return {'type': 'ir.actions.act_window_close'}
