def local_packages(pkgs, basefile):
    """ build a list of packages suitable for local installation

    Usage:

        Installation in your setup.py:

        1. copy the file localpgks.py into the same path as your setup.py
        2. write setup(..., install_requires=...) as follows:

            from localpkgs import local_packages
            setup(...,
                  install_requires=local_packages([
                    'somepackage',
                  ])

        For downloading packages:

            $ cd ./myapp (where setup.py lives)
            $ pip download --platform manylinux1_x86_64 --only-binary=:all: --no-binary=:none: -d ./packages .

            This downloads all packages given in install_requires, including dependencies
            in the format required by the omega-ml runtime (which runs under linux).

        For packaging and storing in omegaml

            $ om put scripts ./myapp apps/myapp

    How this works:

        local_packages() builds a list of packages in this format:

                'package@file://path/to/package_binary.tgz'

        This way, pip install will not download
    """
    from pathlib import Path
    import os
    import sys
    is_pip_download = ' '.join(sys.argv).startswith('pip download')
    should_install_locally = os.environ.get('PIP_INSTALL_LOCAL', 'f')[0].lower() in 'yt1'
    should_install_locally |= os.environ.get('PIP_NO_INDEX', 'f')[0].lower() in 'yt1'
    if not (is_pip_download or should_install_locally):
        return pkgs
    packages_dir = Path(basefile).parent / 'packages'
    packages = []
    local_packages = {fn.name.lower().split('-')[0]: fn for fn in packages_dir.glob('./*') if fn.is_file()}
    for p in pkgs:
        raw_p = p.split('==')[0].lower()
        if raw_p in local_packages:
            packages.append(f'{raw_p}@file://{local_packages[raw_p]}')
            del local_packages[raw_p]
        else:
            packages.append(p)
    for p, fn in local_packages.items():
        packages.append(f'{p}@file://{local_packages[p]}')
    return packages
