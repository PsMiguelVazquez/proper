# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, time
import pytz


class AttendanceLog(models.Model):
    _name = 'attendance.log'
    _description = 'attendance log'
    _order = 'punching_time desc'
    _rec_name = 'punching_time'

    status = fields.Selection([('0', 'Check In'),
                               ('1', 'Check Out'),
                               ('2', 'Punched')], string='Status')
    punching_time = fields.Datetime('Punching Time')
    is_calculated = fields.Boolean('Calculated', default=False)
    device_id = fields.Many2one('biometric.config', string='Device')
    used_for = fields.Selection(related='device_id.used_for')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.company)
    device_user_id = fields.Many2one('biometric.attendance.devices',
                              "Device User", ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  related='device_user_id.employee_id',
                                  store=True)
    employee_name = fields.Char('Employee Name',
                                related='device_user_id.employee_id.name')
    status_number = fields.Char("Status Number")
    number = fields.Char("Number")
    timestamp = fields.Integer("Time stamp")
    status_string = fields.Char("Status String")


    punching_date = fields.Date('Punching Date', compute='_compute_punching_date', store=True)

    @api.depends('punching_time')
    def _compute_punching_date(self):
        for record in self:
            if record.punching_time:
                # Convert UTC time to user's timezone, then extract date
                user_tz = self.env.context.get('tz') or self.env.user.tz or 'UTC'
                local_dt = record.punching_time.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(user_tz))
                record.punching_date = local_dt.date()
            else:
                record.punching_date = False



    def unlink(self):
        if any(self.filtered(lambda log: log.is_calculated == True)):
            raise UserError(('You cannot delete a Record which is already Calculated !!!'))
        return super(AttendanceLog, self).unlink()


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    punch_date = fields.Date(string='Punch Date')

    def compute_in_out_difference(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                check_in = datetime.strptime(str(attendance.check_in.replace(microsecond=0)), '%Y-%m-%d %H:%M:%S')
                check_out = datetime.strptime(str(attendance.check_out.replace(microsecond=0)), '%Y-%m-%d %H:%M:%S')
                diff1 = check_out - check_in
                total_seconds = diff1.seconds
                diff2 = total_seconds / 3600.0
                attendance.in_out_diff = diff2
            else:
                attendance.in_out_diff = 0

    in_out_diff = fields.Float('Difference', compute='compute_in_out_difference')

    def unlink(self):
        for record in self:
            domain = [('employee_id', '=', record.employee_id.id), '|',
                      ('punching_time', '=', record.check_in),
                      ('punching_time', '=', record.check_out)]
            attend_obj = self.env['attendance.log'].search(domain)
            for log in attend_obj:
                log.is_calculated = False
        return super(HrAttendance, self).unlink()

# used for auto check out
    def write(self, vals):
        result = super(HrAttendance, self).write(vals)
        if 'check_out' in vals and 'out_mode' in vals and vals['out_mode'] == 'auto_check_out':
            for rec in self:
                device_user = self.env['biometric.attendance.devices'].search(
                    [('employee_id', '=', rec.employee_id.id)], limit=1)
                self.env['attendance.log'].create({
                    'status': '1',  # Check Out
                    'punching_time': vals['check_out'],
                    'employee_id': rec.employee_id.id,
                    'company_id': rec.employee_id.company_id.id ,
                    'device_user_id': device_user.id if device_user else False,
                    'status_number': '1',
                    'is_calculated': 'True',
                })
        return result

