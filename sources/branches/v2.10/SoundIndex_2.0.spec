# -*- mode: python -*-

block_cipher = None


a = Analysis(['SoundIndex_2.0.py'],
             pathex=['/home/victor/Documents/Docs/Stage/SoundIndex_2/sources/trunk'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             cipher=block_cipher)
a.datas+=[('bitmaps/zoom_in.png', '/home/victor/Documents/Docs/Stage/SoundIndex_2/sources/trunk/bitmaps/zoom_in.png', 'DATA')]
pyz = PYZ(a.pure,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SoundIndex_2.0',
          debug=False,
          strip=None,
          upx=True,
          console=False )

