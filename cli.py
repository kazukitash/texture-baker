import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from modules.utilities.bake_texture import bake_texture

if __name__ == "__main__":
    bake_texture()
