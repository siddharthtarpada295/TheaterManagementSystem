# -*- coding: utf-8 -*-
{
    'name': "Theater Management Module",

    'summary': """
        Manage Theater Ticket Bookings""",

    'description': """
Theater management system for managing Ticket Booking:
------------------------------------------------------
            - Managing Shows 
            - Ticket Bookings
            - Employee Management  
    """,

    'author': "Siddharth",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        'data/data.xml',
        'data/sequence.xml',
        'data/theater_check_show_stages.xml',
        'report/report.xml',
        'security/ir.model.access.csv',
        'views/theater_configuration_views.xml',
        'views/theater_booking_views.xml',
        'views/theater_shows_views.xml',
        'views/theater_movie_views.xml',
        'views/theater_menu_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
