/** @odoo-module **/

import { Component, onWillStart, useState } from '@odoo/owl';
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";

class BiometricDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            total_employees: 0,
            presented_employees: 0,
            absented_employees: 0,
            late_arrival_employees: 0,
            early_leaving_employees: 0,
            presented_employee_details: [],
            absented_employee_details: [],
            late_arrival_employee_details: [],
            early_leaving_employee_details: [],
            isLoading: true,
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            const data = await this.orm.call('biometric.dashboard', 'get_dashboard_data');
            this.state.total_employees = data.total_employees;
            this.state.presented_employees = data.presented_employees;
            this.state.absented_employees = data.absented_employees;
            this.state.late_arrival_employees = data.late_arrival_employees;
            this.state.early_leaving_employees = data.early_leaving_employees;

            // Save employee lists
            this.state.presented_employee_details = data.presented_employee_details || [];
            this.state.absented_employee_details = data.absented_employee_details || [];

            this.state.late_arrival_employee_details = data.late_arrival_employee_details || [];
            this.state.early_leaving_employee_details = data.early_leaving_employee_details || [];

            this.state.isLoading = false;
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.state.isLoading = false;
        }
    }
}

BiometricDashboard.template = "tis_hr_biometric_attendance.BiometricDashboard";
registry.category("actions").add("biometric_dashboard", BiometricDashboard);
