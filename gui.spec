# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['gui.py'],
             pathex=['/home/pi/Face'],
             binaries=[],
             datas=[
				('config.json', '.'),
				('beep.wav', '.'),
				('haarcascade.xml', '.'),
				('openface_nn4.small2.v1.t7', '.'),
				('icons', 'icons'),
				('Clients', 'Clients'),
				('face_detection_model', 'face_detection_model'),
				('unknown', 'unknow'),
				('Records', 'Records')				
			],
             hiddenimports=[
				'pyttsx3.drivers',
			    'pyttsx3.drivers.dummy',
			    'pyttsx3.drivers.espeak',
    			'pyttsx3.drivers.nsss',
    			'pyttsx3.drivers.sapi5',
				'PIL._tkinter_finder'
			],
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
          [],
          exclude_binaries=True,
          name='gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='gui')
