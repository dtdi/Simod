# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 21:25:10 2019

@author: Manuel Camargo
"""
import os
import sys
import getopt
import simod as sim

from support_modules import support as sup

# =============================================================================
# Main function
# =============================================================================


def main(argv):
    settings = dict()
    args = dict()
    settings = define_general_settings(settings)
    # Exec mode 'single', 'optimizer'
    settings['exec_mode'] = 'optimizer'
    # Similarity metric 'tsd', 'dl_mae', 'tsd_min', 'mae'
    settings['sim_metric'] = 'tsd'
    # Parameters settled manually or catched by console for batch operations
    if not argv:
        # Event-log filename
        settings['file'] = 'Production.csv'
        settings['repetitions'] = 2
        settings['simulation'] = True
        if settings['exec_mode'] == 'single':
            # gateways probabilities 'discovery', 'random', 'equiprobable'
            settings['gate_management'] = 'equiprobable'
            # Similarity btw the resources profile execution (Song e.t. all)
            settings['rp_similarity'] = 0.5
            # Splitminer settings [0..1] default epsilon = 0.1, eta = 0.4
            settings['epsilon'] = 0.1
            settings['eta'] = 0.4
            # 'removal', 'replacement', 'repair'
            settings['alg_manag'] = 'repair'
            # Processing time definition method:
            # 'manual', 'automatic', 'semi-automatic'
            settings['pdef_method'] = 'automatic'
            # temporal file for results
            settings['temp_file'] = sup.file_id(prefix='SE_')
            # Single Execution
            simod = sim.Simod(settings)
            simod.execute_pipeline(settings['exec_mode'])
        elif settings['exec_mode'] == 'optimizer':
            args['epsilon'] = [0.0, 1.0]
            args['eta'] = [0.0, 1.0]
            args['max_eval'] = 3
            # Similarity btw the resources profile execution (Song e.t. all)
            args['rp_similarity'] = [0.5, 0.9]
            args['gate_management'] = ['discovery', 'random', 'equiprobable']
            settings['temp_file'] = sup.file_id(prefix='OP_')
            settings['pdef_method'] = 'automatic'
            # Execute optimizer
            if not os.path.exists(os.path.join('outputs',
                                               settings['temp_file'])):
                open(os.path.join('outputs',
                                  settings['temp_file']), 'w').close()
                # sim.hyper_execution(settings, args)
                optimizer = sim.DiscoveryOptimizer(settings, args)
                optimizer.execute_trials()
    else:
        # Catch parameters by console
        try:
            opts, _ = getopt.getopt(argv, "hf:e:n:m:r:",
                                    ['eventlog=', "epsilon=", "eta=",
                                     "alg_manag=", "repetitions="])
            for opt, arg in opts:
                key = catch_parameter(opt)
                if key in ['epsilon', 'eta']:
                    settings[key] = float(arg)
                elif key == 'repetitions':
                    settings[key] = int(arg)
                else:
                    settings[key] = arg
        except getopt.GetoptError:
            print('Invalid option')
            sys.exit(2)
        settings['simulation'] = True
        sim.single_exec(settings)
# =============================================================================
# Support
# =============================================================================


def catch_parameter(opt):
    """Change the captured parameters names"""
    switch = {'-h': 'help', '-f': 'file', '-e': 'epsilon',
              '-n': 'eta', '-m': 'alg_manag', '-r': 'repetitions'}
    try:
        return switch[opt]
    except Exception as e:
        print(e.message)
        raise Exception('Invalid option ' + opt)


def define_general_settings(settings):
    """ Sets the app general settings"""
    column_names = {'Case ID': 'caseid', 'Activity': 'task',
                    'lifecycle:transition': 'event_type', 'Resource': 'user'}
    # Event-log reading options
    settings['read_options'] = {'timeformat': '%Y-%m-%dT%H:%M:%S.%f',
                                'column_names': column_names,
                                'one_timestamp': False,
                                'filter_d_attrib': True,
                                'ns_include': True}
    # Folders structure
    settings['input'] = 'inputs'
    settings['output'] = os.path.join('outputs', sup.folder_id())
    # External tools routes
    settings['miner_path'] = os.path.join('external_tools',
                                          'splitminer',
                                          'splitminer.jar')
    settings['bimp_path'] = os.path.join('external_tools',
                                         'bimp',
                                         'qbp-simulator-engine.jar')
    settings['align_path'] = os.path.join('external_tools',
                                          'proconformance',
                                          'ProConformance2.jar')
    settings['aligninfo'] = os.path.join(settings['output'],
                                         'CaseTypeAlignmentResults.csv')
    settings['aligntype'] = os.path.join(settings['output'],
                                         'AlignmentStatistics.csv')
    return settings


if __name__ == "__main__":
    main(sys.argv[1:])
