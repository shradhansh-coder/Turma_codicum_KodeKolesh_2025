import hashlib
import json
import os
from datetime import datetime


class SimpleChain:
    def __init__(self, chain_file: str):
        self.chain_file = chain_file
        if not os.path.exists(self.chain_file):
            self._write_chain([self._create_genesis_block()])

    def _read_chain(self):
        with open(self.chain_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_chain(self, chain):
        with open(self.chain_file, 'w', encoding='utf-8') as f:
            json.dump(chain, f, indent=2)

    def _create_genesis_block(self):
        data = {
            'index': 0,
            'timestamp': datetime.utcnow().isoformat(),
            'data': 'genesis',
            'previous_hash': '0' * 64,
        }
        data['hash'] = self._hash_block(data)
        return data

    def _hash_block(self, block):
        payload = f"{block['index']}{block['timestamp']}{block['data']}{block['previous_hash']}".encode('utf-8')
        return hashlib.sha256(payload).hexdigest()

    def add_block(self, data: dict):
        chain = self._read_chain()
        prev = chain[-1]
        block = {
            'index': prev['index'] + 1,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data,
            'previous_hash': prev['hash']
        }
        block['hash'] = self._hash_block(block)
        chain.append(block)
        self._write_chain(chain)
        return block

    def verify(self):
        chain = self._read_chain()
        for i in range(1, len(chain)):
            b, prev = chain[i], chain[i-1]
            if b['previous_hash'] != prev['hash']:
                return False
            if self._hash_block({k: b[k] for k in ['index', 'timestamp', 'data', 'previous_hash']}) != b['hash']:
                return False
        return True

    def find_by_document_id(self, doc_id: str):
        chain = self._read_chain()
        results = []
        for b in chain:
            d = b.get('data')
            if isinstance(d, dict) and d.get('document_id') == doc_id:
                results.append(b)
        return results

    @staticmethod
    def sha256_file(path: str):
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
