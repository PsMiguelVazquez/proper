from odoo import models, fields

class EnrollFaceWizard(models.TransientModel):
    _name = "enroll.face.wizard"
    _description = "Enroll Face Wizard"

    device_user_id = fields.Many2one("biometric.attendance.devices", string="Device User", required=True)

    message = fields.Text(
        string="Message",
        default="Are you sure you want to enroll a new face template for this user? "
                "A command will be created and sent to the device.then command success then enroll face "
    )

    def action_confirm(self):
        self.ensure_one()
        return self.device_user_id._create_enroll_face_command()
