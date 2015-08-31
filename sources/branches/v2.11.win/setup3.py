from distutils.core import setup
import py2exe
import matplotlib
import numpy

setup(windows=[
                {
                  "script":  'SoundIndex_2.0.py',
                  'icon_resources': [(1, 'myIcon.ico')]
                }
              ],
   	  options={
      	  'py2exe': {
      	  		r'packages': ['wx.lib.pubsub', 'amara'],
        	    r'includes': [r'scipy.sparse.csgraph._validation',
            	              r'scipy.special._ufuncs_cxx',
            	              r'scipy.linalg.cython_blas',
            	              r'scipy.linalg.cython_lapack',
            	              r'scipy.integrate']
        	}
      },
      data_files=matplotlib.get_py2exe_datafiles())
