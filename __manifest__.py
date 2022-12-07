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
    'version': '1.0.1.1',
    'category': 'Prepress',
    'demo': [],
    'depends': ['portal','cancel_motif'],
    'data': [
        'security/prepress_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/prepress_proof_views.xml'
    ],
    'license': 'LGPL-3',
}
