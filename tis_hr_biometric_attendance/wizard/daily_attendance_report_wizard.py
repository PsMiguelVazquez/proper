from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, time


class DailyAttendanceReportWizard(models.TransientModel):
    _name = 'daily.attendance.report.wizard'
    _description = 'Daily Attendance Report Wizard'

    date_of_report = fields.Date(string='Date', required=True, default=fields.Date.today)

    @api.constrains('date_of_report')
    def _check_date_to_not_future(self):
        for wizard in self:
            if wizard.date_of_report > fields.Date.today():
                raise ValidationError("The selected date cannot be in the future.")

    def action_print_report(self):
        self.ensure_one()
        # Pass self as the document object, no need for separate data dict
        return self.env.ref('tis_hr_biometric_attendance.action_daily_attendance_report_pdf').report_action(self)

    def get_attendance_data(self, date_of_report):
        employee_model = self.env['hr.employee']
        attendance_model = self.env['hr.attendance']
        report_lines = []

        for emp in employee_model.search([('active', '=', True)]):
            attendances = attendance_model.search([
                ('employee_id', '=', emp.id),
                ('check_in', '>=', datetime.combine(date_of_report, time.min)),
                ('check_in', '<=', datetime.combine(date_of_report, time.max)),
            ], order="check_in asc")

            if attendances:
                checkin = attendances[0].check_in
                checkout = attendances[-1].check_out if attendances[-1].check_out else None
                worked_hours = sum(att.worked_hours for att in attendances)
                diff_hours = 0.0
                if checkin and checkout:
                    diff = checkout - checkin
                    diff_hours = round(diff.total_seconds() / 3600, 2)

                report_lines.append({
                    'employee_name': emp.name,
                    'checkin': checkin,
                    'checkout': checkout,
                    'difference': diff_hours,
                    'worked_hours': round(worked_hours),
                })

        return report_lines