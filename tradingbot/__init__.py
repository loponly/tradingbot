""" Trading bot """

__version__ = '2020.10'

if __version__ == 'develop':
    try:
        import subprocess

        __version__ = 'develop' + subprocess.check_output(
            ['git', 'log', '--format="%h"', '-n 1'],
            stderr=subprocess.DEVNULL).decode("utf-8").rstrip().strip('"')
    except Exception:
        # git not available, ignore
        try:
            from pathlib import Path
            versionfile = Path('./freqtrade_commit')
            if versionfile.is_file():
                __version__ = f"docker-{versionfile.read_text()[:8]}"
        except Exception:
            pass