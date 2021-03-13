# -*- coding: utf-8 -*-
# from odoo import http


# class TheaterManagementModule(http.Controller):
#     @http.route('/theater_management_module/theater_management_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/theater_management_module/theater_management_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('theater_management_module.listing', {
#             'root': '/theater_management_module/theater_management_module',
#             'objects': http.request.env['theater_management_module.theater_management_module'].search([]),
#         })

#     @http.route('/theater_management_module/theater_management_module/objects/<model("theater_management_module.theater_management_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('theater_management_module.object', {
#             'object': obj
#         })
