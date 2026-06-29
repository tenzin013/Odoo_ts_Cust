<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- ── Location Form ─────────────────────────────────────────────────── -->
    <record id="view_face_attendance_location_form" model="ir.ui.view">
        <field name="name">face.attendance.location.form</field>
        <field name="model">face.attendance.location</field>
        <field name="arch" type="xml">
            <form string="Attendance Location">
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="action_open_map" type="object"
                                string="View on Map"
                                class="oe_stat_button"
                                icon="fa-map-marker"/>
                    </div>
                    <field name="active" widget="boolean_toggle" class="float-end"/>
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="Location Name"/>
                        </h1>
                    </div>
                    <group>
                        <group string="GPS Coordinates">
                            <field name="latitude"/>
                            <field name="longitude"/>
                            <field name="radius_meters"
                                   widget="integer"
                                   string="Allowed Radius (metres)"/>
                        </group>
                        <group string="Details">
                            <field name="address"/>
                            <field name="company_id" groups="base.group_multi_company"/>
                            <field name="employee_count" readonly="1"
                                   string="Check-ins Today"/>
                        </group>
                    </group>

                    <div class="alert alert-info mt-2" role="alert">
                        <i class="fa fa-info-circle me-2"/>
                        Employees must be within <strong><field name="radius_meters"
                            readonly="1" nolabel="1" class="d-inline"/></strong> metres
                        of <strong>(<field name="latitude" readonly="1" nolabel="1"
                            class="d-inline"/>,
                        <field name="longitude" readonly="1" nolabel="1"
                            class="d-inline"/>)</strong> to mark attendance at this location.
                    </div>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>

    <!-- ── Location List ─────────────────────────────────────────────────── -->
    <record id="view_face_attendance_location_tree" model="ir.ui.view">
        <field name="name">face.attendance.location.list</field>
        <field name="model">face.attendance.location</field>
        <field name="arch" type="xml">
            <list string="Attendance Locations" editable="bottom">
                <field name="name"/>
                <field name="address"/>
                <field name="latitude"/>
                <field name="longitude"/>
                <field name="radius_meters" string="Radius (m)"/>
                <field name="employee_count" string="Check-ins Today"/>
                <field name="active" widget="boolean_toggle"/>
            </list>
        </field>
    </record>

    <!-- ── Location Search ───────────────────────────────────────────────── -->
    <record id="view_face_attendance_location_search" model="ir.ui.view">
        <field name="name">face.attendance.location.search</field>
        <field name="model">face.attendance.location</field>
        <field name="arch" type="xml">
            <search>
                <field name="name"/>
                <field name="address"/>
                <filter string="Active" name="active" domain="[('active','=',True)]"/>
                <filter string="Archived" name="archived" domain="[('active','=',False)]"/>
            </search>
        </field>
    </record>

    <!-- ── Action ────────────────────────────────────────────────────────── -->
    <record id="action_face_attendance_location" model="ir.actions.act_window">
        <field name="name">Attendance Locations</field>
        <field name="res_model">face.attendance.location</field>
        <field name="view_mode">list,form</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Add your first attendance location
            </p>
            <p>
                Configure GPS coordinates and radius for each site where employees
                are allowed to check in and out using face recognition.
            </p>
        </field>
    </record>

</odoo>
