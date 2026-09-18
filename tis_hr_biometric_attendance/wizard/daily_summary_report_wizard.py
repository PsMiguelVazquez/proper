from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, time
import pytz


class DailySummaryReportWizard(models.TransientModel):
    _name = 'daily.summary.report.wizard'
    _description = 'Daily Summary Report Wizard'

    date_of_summary = fields.Date(string='Date', required=True, default=fields.Date.today)

    @api.constrains('date_of_summary')
    def _check_date_to_not_future(self):
        for wizard in self:
            if wizard.date_of_summary > fields.Date.today():
                raise ValidationError("The selected date cannot be in the future.")

    def _get_report_data(self):
        date = self.date_of_summary
        weekday = str(date.weekday())
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        start_dt = tz.localize(datetime.combine(date, time.min))
        end_dt = tz.localize(datetime.combine(date, time.max))

        employees = self.env['hr.employee'].search([])
        total_employees = len(employees)

        attendance_logs = self.env['attendance.log'].search([
            ('punching_time', '>=', start_dt),
            ('punching_time', '<=', end_dt),
            ('employee_id', '!=', False)
        ])

        presented_ids = attendance_logs.filtered(
            lambda log: log.status in ['0', '2']
        ).mapped('employee_id.id')
        presented_ids_set = set(presented_ids)

        absented_employees = employees.filtered(lambda emp: emp.id not in presented_ids_set)
        presented_employees = employees.filtered(lambda emp: emp.id in presented_ids_set)

        late_arrival_count = 0
        early_leaving_count = 0
        detailed_presented = []
        detailed_absented = []

        for emp in employees:
            emp_logs = attendance_logs.filtered(lambda l: l.employee_id.id == emp.id)
            calendar = emp.resource_calendar_id
            if not emp_logs or not calendar:
                continue

            today_att = calendar.attendance_ids.filtered(lambda a: a.dayofweek == weekday)
            if not today_att:
                continue

            hour_from = min(today_att.mapped('hour_from'))
            hour_to = max(today_att.mapped('hour_to'))

            expected_start = tz.localize(datetime.combine(date, time(int(hour_from), int((hour_from % 1) * 60))))
            expected_end = tz.localize(datetime.combine(date, time(int(hour_to), int((hour_to % 1) * 60))))

            checkin_logs = emp_logs.filtered(lambda l: l.status == '0')
            checkout_logs = emp_logs.filtered(lambda l: l.status == '1')

            if checkin_logs:
                first_checkin = min([l.punching_time.astimezone(tz) for l in checkin_logs])
                if first_checkin > expected_start:
                    late_arrival_count += 1
                    late_time = str(first_checkin - expected_start).split('.')[0]
                else:
                    late_time = '00:00:00'
            else:
                first_checkin = None
                late_time = '00:00:00'

            if checkout_logs:
                last_checkout = max([l.punching_time.astimezone(tz) for l in checkout_logs])
                if last_checkout < expected_end:
                    early_leaving_count += 1
                    early_time = str(expected_end - last_checkout).split('.')[0]
                else:
                    early_time = '00:00:00'
            else:
                last_checkout = None
                early_time = '00:00:00'

            if emp.id in presented_ids_set:
                detailed_presented.append({
                    'name': emp.name,
                    'company': emp.company_id.name if emp.company_id else '',
                    'department': emp.department_id.name if emp.department_id else '',
                    'first_checkin': first_checkin.strftime('%Y-%m-%d %H:%M:%S') if first_checkin else '',
                    'last_checkout': last_checkout.strftime('%Y-%m-%d %H:%M:%S') if last_checkout else '',
                    'late_time': late_time,
                    'early_time': early_time,
                })

        detailed_absented = [
            {
                'name': emp.name,
                'company': emp.company_id.name if emp.company_id else '',
                'department': emp.department_id.name if emp.department_id else '',
            } for emp in absented_employees
        ]

        return {
            'total_employees': total_employees,
            'present_employees': len(presented_ids_set),
            'absent_employees': len(absented_employees),
            'late_arrivals': late_arrival_count,
            'early_leavings': early_leaving_count,
            'absent_employee_lines': detailed_absented,
            'present_employee_lines': detailed_presented,
        }

    def action_print_report(self):
        self.ensure_one()

        report_data = self._get_report_data()

        report_context = {
            'date_of_summary': self.date_of_summary.strftime('%Y-%m-%d'),
            **report_data
        }

        return self.env.ref('tis_hr_biometric_attendance.wizard_daily_summary_report_action').report_action(
            self, data=report_context
        )
