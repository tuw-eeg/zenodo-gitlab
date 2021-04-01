from enum import Enum


class ArchiveFormat(str, Enum):
    ZIP = 'zip'
    TAR_GZ = 'tar.gz'
    TAR_BZ2 = 'tar.bz2'
    TAR = 'tar'
