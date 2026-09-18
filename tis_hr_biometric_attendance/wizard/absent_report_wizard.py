from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError

class AbsenceReportWizard(models.TransientModel):
    _name = 'absence.report.wizard'
    _description = 'Absence Report Wizard'

    date_from = fields.Date(string='From Date', required=True, default=fields.Date.today)
    date_to = fields.Date(string='To Date', required=True, default=fields.Date.today)

    @api.constrains('date_to')
    def _check_date_to_not_future(self):
        for wizard in self:
            if wizard.date_to > fields.Date.today():
                raise ValidationError("The 'To Date' cannot be in the future. Please select today or an earlier date.")

    @api.constrains('date_from')
    def _check_date_from_not_future(self):
        for wizard in self:
            if wizard.date_from > fields.Date.today():
                raise ValidationError("The 'To Date' cannot be in the future. Please select today or an earlier date.")

    def action_print_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }

        attendance_model = self.env['hr.attendance']
        employee_model = self.env['hr.employee']

        absent_records = []

        current_day = self.date_from
        while current_day <= self.date_to:
            all_employees = employee_model.search([])
            attended_employees = attendance_model.search([
                ('check_in', '>=', current_day),
                ('check_in', '<', current_day + timedelta(days=1)),
            ]).mapped('employee_id')

            absents = all_employees.filtered(lambda e: e not in attended_employees)

            for emp in absents:
                absent_records.append({
                    'name': emp.name,
                    'location': emp.company_id.name or '',
                    'department': emp.department_id.name if emp.department_id else '',
                    'absent_date': current_day.strftime('%Y-%m-%d'),
                })

            current_day += timedelta(days=1)

        data['absent_lines'] = absent_records

        return self.env.ref('tis_hr_biometric_attendance.action_absence_report_pdf').report_action(self, data=data)
