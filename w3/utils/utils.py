import argparse


def args_to_str(args: argparse.Namespace) -> str:
    out = ''
    out += '-'.join(map(str, args.units))
    out += '_' + '-'.join(args.activation)
    out += '_' + args.loss
    out += '_' + args.optimizer
    out += '_' + '-'.join(args.metrics)
    out += '_' + str(args.image_size)
    return out


def str_to_args(s: str) -> argparse.Namespace:
    args = argparse.Namespace()
    params = s.split('_')

    args.units = map(int, params[0].split('-'))
    args.activation = params[1].split('-')
    args.loss = params[2]
    args.optimizer = params[3]
    args.metrics = params[4].split('-')
    args.image_size = int(params[5])

    return args
