# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2024. All rights reserved.


{
    'name': 'ZKteco Biometric Attendance Integration',
    'version': '0.1',
    'category': 'Human Resources',
    'sequence': 1,
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'summary': 'Biometric attendance integration',
    'website': 'http://www.technaureus.com/',
    'price': 205,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'description': """
 Synchronization of employee attendance with biometric machine ...""",
    'depends': ['hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/biometric_data.xml',
        'views/biometric_device_config_view.xml',
        'views/biometric_attnd_log_view.xml',
        'wizard/attendance_calc_wizard_view.xml',
        'wizard/biometric_device_view.xml',
        'wizard/attendance_report_wizard_view.xml',
        'wizard/attendance_adms_download_wizard_view.xml',
        'wizard/restart_button_wizard_view.xml',
        'wizard/absent_report_wizard_view.xml',
        'wizard/daily_summary_report_wizard_view.xml',
        'wizard/daily_attendance_report_wizard_view.xml',
        'wizard/biometric_sync_wizard_view.xml',
        'wizard/enroll_face_wizard_view.xml',
        'wizard/enroll_finger_wizard_view.xml',
        'report/daily_attendance_report.xml',
        'report/daily_attendance_report_template.xml',
        'report/absence_report.xml',
        'report/absence_report_template.xml',
        'report/daily_summary_report.xml',
        'report/daily_summary_report_template.xml',
        'views/hr_attendance_view.xml',
        'views/hr_employee_view.xml',
        'views/res_config_settings.xml',
        'views/attendance_data_log_device_view.xml',
        'views/attendance_state_views.xml',
        'views/device_command_view.xml',
        'views/op_stamp_log_view.xml',
        'views/stamp_log.xml',
        'views/biometric_attendance_devices_views.xml',
        'views/finger_template_views.xml',
        'views/biometric_dashboard_menu.xml',
        'views/face_template_views.xml',

    ],
    'assets': {
            'web.assets_backend': [
                'tis_hr_biometric_attendance/static/src/js/biometric_dashboard.js',
                'tis_hr_biometric_attendance/static/src/xml/biometric_dashboard_view.xml',
            ],
    },
    'demo': [
    ],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'live_test_url': 'https://www.youtube.com/watch?v=GCq-7WzserA&t=104s'
}
