from evo.runner import ExperimentRunner, load_config

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment', type=str, default='default_config',
                        help='Name of the experiment YAML in the experiments/configs directory')
    args = parser.parse_args()

    config = load_config(args.experiment)
    config['experiment_name'] = args.experiment

    runner = ExperimentRunner(config)
    runner.run()


if __name__ == '__main__':
    main()
