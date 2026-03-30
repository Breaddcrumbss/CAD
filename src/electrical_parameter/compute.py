import argparse
import json
import os
import sys

def compute_params(base: dict):
    params = {}

    # Batteries
    params['batteries_in_series'] = base['battery']["battery_in_series"]
    params['batteries_in_parallel'] = base['battery']["battery_in_parallel"]
    params['total_batteries'] = (params['batteries_in_series'] *
                                params['batteries_in_parallel'])
    
    # MPPT Tracker
    params['num_mppt'] = base['mppt_panel']["config_1"]["count"]

    # Solar Panels
    params["panels_in_series_per_mppt"] = base['mppt_panel']["config_1"]["panel_info"].get("in_series", base['panels_transversal'])
    params["panels_in_parallel_per_mppt"] = base['mppt_panel']["config_1"]["panel_info"].get("in_parallel", base['panels_longitudinal']//2)
    params["panels_per_mppt"] = (params["panels_in_series_per_mppt"] * params["panels_in_parallel_per_mppt"])
    params["total_panels"] = (params["panels_per_mppt"] * params['num_mppt'])

    assert params["total_panels"] == (base['panels_transversal'] * base['panels_longitudinal']), f"MPPT config has does not match overall panel count \n {params['num_mppt']} MPPTs with {params['panels_in_parallel_per_mppt']} * {params['panels_in_series_per_mppt']} each, = {params["total_panels"]} panels, but total panels is {base['panels_transversal']} * {base['panels_longitudinal']} = {base['panels_transversal'] * base['panels_longitudinal']}"

    required_params = ['panels_longitudinal', 'panels_transversal', 'pillar_width', 'panel_length', 'crossdeck_width', 
                       'panel_width', 'panel_base_level', 'panel_height', 'deck_width', 'deck_level']
    for param in required_params:
        params[param] = base[param]

    return params


