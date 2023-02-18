# -*- coding: utf-8 -*- 


{
    'name': 'Prepress management',
    'author': 'Soft-integration',
    'application': True,
    'installable': True,
    'auto_install': False,
    'qweb': [],
    'description': False,
    'images': [],
    'version': '1.0.1.85',
    'category': 'Prepress',
    'demo': [],
    'depends': ['portal',
                'cancel_motif',
                'product_customer',
                'product_dimensions',
                'web_custom_groups'],
    'data': [
        'security/prepress_management_security.xml',
        'security/ir.model.access.csv',
        'data/prepress_management_data.xml',
        'data/ir_sequence_data.xml',
        'views/prepress_proof_views.xml',
        'views/prepress_cutting_die_views.xml',
        'views/prepress_plate_views.xml',
        'views/product_views.xml',
        'views/cancel_motif_views.xml',
        'wizard/prepress_proof_flash_views.xml',
        'wizard/prepress_proof_quarantined_confirmation_views.xml'
    ],
    'license': 'LGPL-3',
}
