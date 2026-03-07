import uuid
import shutil
from pathlib import Path
from typing import List
import os

from schema import File, Metrics


class FileNameError(Exception):
    pass


class FileManager:
    def __init__(self, directory: str, data: Metrics, files: List[File], language: str):
        self.base_dir = Path(directory)
        self.session_dir = (self.base_dir / str(uuid.uuid4())).resolve()
        self.stats = self.session_dir / str(uuid.uuid4())
        self.data = data
        self.files = files
        self.lang = language

    def __enter__(self):
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.stats.touch(exist_ok=True)
        self.stats.chmod(666)

        for file in self.files:
            file_path = self.session_dir / file.name

            if not file.name or '..' in file.name or file_path.parent.resolve() != self.session_dir:
                raise FileNameError(f"Invalid file name: {file.name}")
            
            with open(file_path, mode='w') as f:
                f.write(file.content)

        if self.lang == "golang":
            cache = Path("/tmp/.go_cache")
            cache.mkdir(exist_ok=True)
            os.environ["GOCACHE"] = str(cache)
            os.system(f"chown user {cache}")

        self.session_dir.chmod(777)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            file = open(self.stats, mode='r').readlines()
            stats = file[0].split()
            if len(file) == 2:
                stats = file[1].split()
            if len(stats) == 2:
                self.data.time = f"{float(stats[0]):.2f} s"
                self.data.phys_mem = f"{round(int(stats[1]) / 1024, 2)} Mb"
        
            shutil.rmtree(self.session_dir)
        except Exception as e:
            print(e)
    
