from odoo import models, fields, api
from odoo.exceptions import UserError


class EnrollFingerWizard(models.TransientModel):
    _name = 'enroll.finger.wizard'
    _description = 'Enroll Finger Wizard'

    device_user_id = fields.Many2one(
        'biometric.attendance.devices',
        string="Device User",
        required=True
    )
    hand = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right')
    ], string="Hand", required=True)

    finger = fields.Selection([
        ('little', 'Little Finger'),
        ('ring', 'Ring Finger'),
        ('middle', 'Middle Finger'),
        ('point', 'Point Finger'),
        ('thumb', 'Thumb Finger'),
    ], string="Finger", required=True)

    def _get_fid(self):
        """Return FID based on hand + finger mapping."""
        mapping = {
            'left': {
                'little': 0,
                'ring': 1,
                'middle': 2,
                'point': 3,
                'thumb': 4,
            },
            'right': {
                'thumb': 5,
                'point': 6,
                'middle': 7,
                'ring': 8,
                'little': 9,
            }
        }
        return mapping[self.hand][self.finger]

    def action_confirm(self):
        """Generate the ENROLL_FP command with correct FID."""
        self.ensure_one()
        fid = self._get_fid()

        device_user = self.device_user_id
        if not device_user.device_id.is_adms:
            raise UserError("Enrollment is only supported on ADMS-connected devices.")

        # Prevent duplicate enrollment for same FID
        if any(ft.f_id == fid for ft in device_user.finger_template_ids):
            raise UserError(f"Finger already enrolled with FID={fid}.")

        # Create command
        command_id = self.env['device.command'].sudo().create({
            'name': 'ENROLL_FP',
            'device_id': device_user.device_id.id,
            'pin': device_user.biometric_attendance_id,
        })

        # Use your original command structure
        command_text = (
            f"C:{command_id.id}:ENROLL_FP "
            f"PIN={device_user.biometric_attendance_id}\tFID={fid}\tRETRY=1\tOVERWRITE=1\n"
        )
        command_id.execution_log = command_text

        return True
