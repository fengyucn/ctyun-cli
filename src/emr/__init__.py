"""
翼MapReduce(EMR)模块
"""

from .client import EMRClient
from .commands import emr

__all__ = ['EMRClient', 'emr']
