# -*- mode: python -*-

block_cipher = None


a = Analysis(['clkhash\\cli.py'],
             pathex=['C:\\Users\\tho802\\Development\\clkhash'],
             binaries=[],
             datas=[
                 ('clkhash/data/randomnames-schema.json', 'clkhash/data'),
                 ('clkhash/data/*.csv', 'clkhash/data'),
                 ('clkhash/schemas/*.json', 'clkhash/schemas')
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='clkutil',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
