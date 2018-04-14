import shlex

def print_cmd(cmd, shell=False, env=None):
    print('> ', end='')
    if env is not None:
        print(' '.join(sorted('{}={}'.format(k, shlex.quote(v))
                for k, v in env.items())), end=' ')
    if shell:
        print(cmd)
    else:
        print(' '.join(cmd))
