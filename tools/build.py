from pathlib import Path
import subprocess,sys,shutil
root=Path(__file__).resolve().parents[1]
dist=root/'dist';dist.mkdir(exist_ok=True)
shutil.copytree(root/'assets',dist/'assets',dirs_exist_ok=True)
if '--regenerate' in sys.argv:
 for script in ['build-animations.py','build-cyan-animations.py']:
  subprocess.run([sys.executable,str(root/'source'/script)],check=True,cwd=root)
subprocess.run([sys.executable,str(root/'source/build-player.py')],check=True,cwd=root)
for name in ['index.html','player.js']:shutil.copyfile(dist/name,root/name)
shutil.copytree(dist/'assets',root/'assets',dirs_exist_ok=True)
print('Player rebuilt.')
