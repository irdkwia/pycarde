import os, shutil
from PIL import Image
import json
from pycarde.constants import *
from pycarde.card import RawAppCard, PkSTAppCard, STViewCard, PkViewCard, PkAbilityCard, PkConstructCard

NTOTYPE = {x.__name__: x for x in [RawAppCard, PkSTAppCard, STViewCard, PkViewCard, PkAbilityCard, PkConstructCard]}
TRANSCO = []
SER_TRANSCO = {k: v for k, v in TRANSCO}
DESER_TRANSCO = {k: v for v, k in TRANSCO}

class Directory:
    def __init__(self, path, mode='r'):
        if mode=='r' and not os.path.isdir(path):
            raise Exception("Not an existing directory!")
        elif mode=='w':
            if not os.path.isdir(path) and os.path.exists(path):
                raise Exception("Not a directory!")
            if os.path.isdir(path):
                shutil.rmtree(path)
            os.makedirs(path, exist_ok=True)
        self.path = path
        self.mode = mode

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass
    
    def open(self, path, mode='r'):
        if mode!='r' and self.mode=='r':
            raise Exception("Trying to write in read mode!")
        return open(os.path.join(self.path, path), mode=mode+'b')

class CardSerializer:
    def serializevariable(zf, k, v):
        if isinstance(v, bytes) or isinstance(v, bytearray):
            with zf.open(k+".dat", 'w') as file:
                file.write(v)
            v = {"file": k+".dat", "type": FTYPE_DATA}
        elif isinstance(v, Image.Image):
            with zf.open(k+".png", 'w') as file:
                v.save(file, 'PNG')
            v = {"file": k+".png", "type": FTYPE_IMAGE}
        elif isinstance(v, list) or isinstance(v, tuple):
            nv = []
            for i, e in enumerate(v):
                nv.append(CardSerializer.serializevariable(zf, "%s-%d"%(k,i), e))
            v = nv
        return v
    
    @staticmethod
    def serialize(card, zf):
        serdict = dict()
        for k, v in card.__dict__.items():
            if k in SER_TRANSCO:
                k = SER_TRANSCO[k]
            v = CardSerializer.serializevariable(zf, k, v)
            serdict[k] = v
        with zf.open('info.json', 'w') as file:
            file.write(json.dumps({"type": card.__class__.__name__, "data": serdict}, indent="\t", ensure_ascii=False).encode("utf-8"))

    def deserializevariable(zf, v):
        if isinstance(v, dict):
            with zf.open(v["file"], 'r') as file:
                if v["type"]==FTYPE_DATA:
                    v = file.read()
                elif v["type"]==FTYPE_IMAGE:
                    v = Image.open(file)
                    v.load()
                else:
                    raise Exception("Invalid file type!")
        elif isinstance(v, list) or isinstance(v, tuple):
            nv = []
            for i, e in enumerate(v):
                nv.append(CardSerializer.deserializevariable(zf, e))
            v = nv
        return v
    
    @staticmethod
    def deserialize(zf):
        with zf.open('info.json', 'r') as file:
            deserdict = json.loads(file.read().decode("utf-8"))
        card = NTOTYPE[deserdict["type"]](0,0)
        for k, v in deserdict["data"].items():
            if k in DESER_TRANSCO:
                k = DESER_TRANSCO[k]
            v = CardSerializer.deserializevariable(zf, v)
            setattr(card, k, v)
        return card
