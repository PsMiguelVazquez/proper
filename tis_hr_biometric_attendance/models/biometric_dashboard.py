from odoo import models, api
from datetime import datetime, timedelta, time
import pytz


class BiometricDashboard(models.AbstractModel):
    _name = 'biometric.dashboard'
    _description = 'Displaying DashBoard Data'

    @api.model
    def get_dashboard_data(self):
        today = datetime.combine(datetime.today().date(), time.min)
        local_tz = pytz.timezone(self.env.user.tz or 'UTC')
        weekday = str(today.weekday())  # Monday = 0

        employees = self.env['hr.employee'].search([])
        total_employees = len(employees)

        attendance_logs = self.env['attendance.log'].search([
            ('punching_time', '>=', today),
            ('employee_id', '!=', False)
        ])

        # For present count, check status 0 (Check In) or 2 (Punched)
        presented_employee_ids = attendance_logs.filtered(
            lambda l: l.status in ['0', '2']
        ).mapped('employee_id.id')

        presented_count = len(set(presented_employee_ids))
        absented_count = total_employees - presented_count

        late_arrival_count = 0
        early_leaving_count = 0

        for emp in employees:
            emp_logs = attendance_logs.filtered(lambda log: log.employee_id.id == emp.id)
            if not emp_logs:
                continue

            calendar = emp.resource_calendar_id
            if not calendar:
                continue

            today_attendance = calendar.attendance_ids.filtered(lambda a: a.dayofweek == weekday)
            if not today_attendance:
                continue

            expected_start = min(today_attendance.mapped('hour_from'))
            expected_end = max(today_attendance.mapped('hour_to'))

            expected_start_dt = local_tz.localize(
                datetime.combine(today.date(), time(int(expected_start), int((expected_start % 1) * 60)))
            )
            expected_end_dt = local_tz.localize(
                datetime.combine(today.date(), time(int(expected_end), int((expected_end % 1) * 60)))
            )

            # Check earliest check-in
            checkin_logs = emp_logs.filtered(lambda log: log.status == '0')
            if checkin_logs:
                earliest_checkin = min([log.punching_time.astimezone(local_tz) for log in checkin_logs])
                if earliest_checkin > expected_start_dt:
                    late_arrival_count += 1

            # Check latest check-out
            checkout_logs = emp_logs.filtered(lambda log: log.status == '1')
            if checkout_logs:
                latest_checkout = max([log.punching_time.astimezone(local_tz) for log in checkout_logs])
                if latest_checkout < expected_end_dt:
                    early_leaving_count += 1

        # Employee Detail presented and absent Lists
        presented_employees = self.env['hr.employee'].browse(list(set(presented_employee_ids)))
        absented_employees = employees.filtered(lambda emp: emp.id not in presented_employee_ids)

        presented_data = [
            {
                'name': emp.name,
                'job_title': emp.job_id.name if emp.job_id else '',
                'image': emp.image_1920.decode('utf-8') if emp.image_1920 else None,
            } for emp in presented_employees
        ]

        absented_data = [
            {
                'name': emp.name,
                'job_title': emp.job_id.name if emp.job_id else '',
                'image': emp.image_1920.decode('utf-8') if emp.image_1920 else None,
            } for emp in absented_employees
        ]

        # Late Arrival Employee Details
        late_arrival_data = []
        for emp in employees:
            emp_logs = attendance_logs.filtered(lambda log: log.employee_id.id == emp.id)
            if not emp_logs:
                continue

            calendar = emp.resource_calendar_id
            if not calendar:
                continue

            today_attendance = calendar.attendance_ids.filtered(lambda a: a.dayofweek == weekday)
            if not today_attendance:
                continue

            expected_start = min(today_attendance.mapped('hour_from'))
            expected_start_dt = local_tz.localize(
                datetime.combine(today.date(), time(int(expected_start), int((expected_start % 1) * 60)))
            )

            checkin_logs = emp_logs.filtered(lambda log: log.status == '0')
            if checkin_logs:
                earliest_checkin = min([log.punching_time.astimezone(local_tz) for log in checkin_logs])
                if earliest_checkin > expected_start_dt:
                    delay = earliest_checkin - expected_start_dt
                    late_arrival_data.append({
                        'name': emp.name,
                        'job_title': emp.job_id.name if emp.job_id else '',
                        'image': emp.image_1920.decode('utf-8') if emp.image_1920 else None,
                        'late_by': str(delay).split('.')[0]
                    })

        # Early Leaving Employee Details
        early_leaving_data = []
        for emp in employees:
            emp_logs = attendance_logs.filtered(lambda log: log.employee_id.id == emp.id)
            if not emp_logs:
                continue

            calendar = emp.resource_calendar_id
            if not calendar:
                continue

            today_attendance = calendar.attendance_ids.filtered(lambda a: a.dayofweek == weekday)
            if not today_attendance:
                continue

            expected_end = max(today_attendance.mapped('hour_to'))
            expected_end_dt = local_tz.localize(
                datetime.combine(today.date(), time(int(expected_end), int((expected_end % 1) * 60)))
            )

            checkout_logs = emp_logs.filtered(lambda log: log.status == '1')
            if checkout_logs:
                latest_checkout = max([log.punching_time.astimezone(local_tz) for log in checkout_logs])
                if latest_checkout < expected_end_dt:
                    early = expected_end_dt - latest_checkout
                    early_leaving_data.append({
                        'name': emp.name,
                        'job_title': emp.job_id.name if emp.job_id else '',
                        'image': emp.image_1920.decode('utf-8') if emp.image_1920 else None,
                        'left_early_by': str(early).split('.')[0]  # HH:MM:SS
                    })

        return {
            'total_employees': total_employees,
            'presented_employees': presented_count,
            'absented_employees': absented_count,
            'late_arrival_employees': late_arrival_count,
            'early_leaving_employees': early_leaving_count,
            'presented_employee_details': presented_data,
            'absented_employee_details': absented_data,
            'late_arrival_employee_details': late_arrival_data,
            'early_leaving_employee_details': early_leaving_data,
        }

