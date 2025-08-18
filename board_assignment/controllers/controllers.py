# -*- coding: utf-8 -*-
# from odoo import http


# class BoardAssignment(http.Controller):
#     @http.route('/board_assignment/board_assignment', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/board_assignment/board_assignment/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('board_assignment.listing', {
#             'root': '/board_assignment/board_assignment',
#             'objects': http.request.env['board_assignment.board_assignment'].search([]),
#         })

#     @http.route('/board_assignment/board_assignment/objects/<model("board_assignment.board_assignment"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('board_assignment.object', {
#             'object': obj
#         })
