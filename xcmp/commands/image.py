#!/usr/bin/python3
# coding:utf-8

from typing import Optional
from typing import Sequence

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ..utils import URL_PROG
from ..utils import __prog_image__
from ..utils import __version__
from ..utils import imagecmp


@add_command(__prog_image__)
def add_cmd(_arg: argp):
    group = _arg.argument_group("objects")
    group.add_argument("_paths_",
                       type=str,
                       nargs="+",
                       metavar="OBJ",
                       help="Specify all objects(directorys or files)")
    group.add_argument("--exclude",
                       type=str,
                       nargs="+",
                       default=[],
                       metavar="OBJ",
                       action="extend",
                       dest="_exclude_",
                       help="Specify exclude directorys or files")

    group = _arg.argument_group("actions")
    mgroup = group.add_mutually_exclusive_group()
    mgroup.add_argument("--same",
                        action="store_true",
                        dest="_action_same_",
                        help="Only list same images")
    mgroup.add_argument("--diff",
                        action="store_true",
                        dest="_action_diff_",
                        help="Not list same images")


@run_command(add_cmd)
def run_cmd(cmds: commands) -> int:
    paths = cmds.args._paths_
    exclude = cmds.args._exclude_
    icmp = imagecmp.scan(paths=paths, exclude=exclude)

    if cmds.args._action_diff_ or not cmds.args._action_same_:
        for hash, path in icmp.diff.items():
            cmds.stdout(f"{hash} {path}")

    if cmds.args._action_same_ or not cmds.args._action_diff_:
        for hash, paths in icmp.same.items():
            cmds.stdout(f"{hash}")
            for path in paths:
                cmds.stdout(f"\t{path}")

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = commands()
    cmds.version = __version__
    return cmds.run(root=add_cmd,
                    argv=argv,
                    prog=__prog_image__,
                    description="Compare images.",
                    epilog=f"For more, please visit {URL_PROG}.")
