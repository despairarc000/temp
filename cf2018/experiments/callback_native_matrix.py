"""Opt-in isolated native callback matrix; no sockets or phone experiment."""
import argparse
import json
from native_callback_controls import callback_probe
from native_control import LIBRARY_SHA256


def matrix(library):
    cases=[('transport_observer',{}),('transport_state4',{'state':4}),
           ('transport_empty',{'observer':False}),
           ('dispatch_bind_boundary',{'stage':'dispatch'}),
           ('dispatch_error9',{'stage':'dispatch','result':9}),
           ('dispatch_no_connector',{'stage':'dispatch','connector':False}),
           ('dispatch_bad_observer_cast',{'stage':'dispatch','cast':False}),
           ('dispatch_bad_buffer_cast',{'stage':'dispatch','buffer_cast':False}),
           ('dispatch_actual_bind_open',{'stage':'dispatch','execute_bind':True}),
           ('dispatch_empty',{'stage':'dispatch','observer':False})]
    return {'schema':1,'base_main':'c9b1d3555f8dd4036d64d1d34cb47a440b881c4c',
            'library_sha256':LIBRARY_SHA256,
            'evidence':'NATIVE_CALLBACK_WITH_EXPLICIT_RUNTIME_STUBS_NOT_AUTH',
            'controls':[{'name':name,'configuration':config,
                         'actual':callback_probe(library,**config)}
                        for name,config in cases]}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--library')
    a=p.parse_args()
    if a.library: print(json.dumps(matrix(a.library),indent=2))
    else: print('Inactive: supply --library for offline native controls.')
